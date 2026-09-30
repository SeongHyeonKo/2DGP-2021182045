"""Play Ninja Turtle sprite-sheet animations in sequence.

The source sheet has uneven frame sizes and animation lengths, so each frame
is cropped and its connected sheet background is made transparent at startup.
"""

from collections import Counter, deque
from pathlib import Path
import struct
import tempfile
import zlib

from pico2d import *


CANVAS_WIDTH = 960
CANVAS_HEIGHT = 720
FRAME_DELAY = 0.10
REPEAT_COUNT = 5
PAUSE_SECONDS = 1.0
BACKGROUND_TOLERANCE = 24


def _decode_png(path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"스프라이트 시트가 올바른 PNG 파일이 아닙니다: {path}")

    offset = 8
    image_data = bytearray()
    width = height = bit_depth = color_type = None
    while offset < len(data):
        chunk_length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        chunk = data[offset + 8:offset + 8 + chunk_length]
        offset += chunk_length + 12
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
                ">IIBBBBB", chunk
            )
            if (bit_depth, color_type, compression, filtering, interlace) != (8, 2, 0, 0, 0):
                raise ValueError("8-bit 비인터레이스 RGB PNG 스프라이트 시트가 필요합니다.")
        elif chunk_type == b"IDAT":
            image_data.extend(chunk)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None:
        raise ValueError("PNG 헤더를 읽을 수 없습니다.")

    bytes_per_pixel = 3
    row_size = width * bytes_per_pixel
    compressed = zlib.decompress(image_data)
    rows = []
    previous = bytearray(row_size)
    position = 0

    for _ in range(height):
        filter_type = compressed[position]
        position += 1
        row = bytearray(compressed[position:position + row_size])
        position += row_size

        for index in range(row_size):
            left = row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            above = previous[index]
            upper_left = previous[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            if filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = above
            elif filter_type == 3:
                predictor = (left + above) // 2
            elif filter_type == 4:
                estimate = left + above - upper_left
                left_distance = abs(estimate - left)
                above_distance = abs(estimate - above)
                upper_left_distance = abs(estimate - upper_left)
                if left_distance <= above_distance and left_distance <= upper_left_distance:
                    predictor = left
                elif above_distance <= upper_left_distance:
                    predictor = above
                else:
                    predictor = upper_left
            elif filter_type == 0:
                predictor = 0
            else:
                raise ValueError(f"지원하지 않는 PNG 필터입니다: {filter_type}")
            row[index] = (row[index] + predictor) & 0xFF

        rows.append(bytes(row))
        previous = row

    return width, height, rows


def _make_chunk(chunk_type, payload):
    chunk = chunk_type + payload
    return struct.pack(">I", len(payload)) + chunk + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)


def _write_rgba_png(path, width, height, rgba):
    scanlines = bytearray()
    stride = width * 4
    for y in range(height):
        scanlines.append(0)
        scanlines.extend(rgba[y * stride:(y + 1) * stride])

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _make_chunk(b"IHDR", header)
        + _make_chunk(b"IDAT", zlib.compress(scanlines))
        + _make_chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def _extract_frame(rows, sheet_width, sheet_background, region, output_path):
    left, top, right, bottom = region
    width, height = right - left, bottom - top
    if left < 0 or top < 0 or right > sheet_width or width <= 0 or height <= 0:
        raise ValueError(f"스프라이트 프레임 영역이 이미지 범위를 벗어났습니다: {region}")

    pixels = [
        tuple(rows[y][x * 3:x * 3 + 3])
        for y in range(top, bottom)
        for x in range(left, right)
    ]
    background = Counter(pixels).most_common(1)[0][0]

    background_colors = (background, sheet_background)

    def matches_background(pixel):
        return any(
            all(abs(pixel[channel] - color[channel]) <= BACKGROUND_TOLERANCE for channel in range(3))
            for color in background_colors
        )

    transparent = bytearray(width * height)
    queue = deque()

    def enqueue(index):
        if not transparent[index] and matches_background(pixels[index]):
            transparent[index] = 1
            queue.append(index)

    for x in range(width):
        enqueue(x)
        enqueue((height - 1) * width + x)
    for y in range(height):
        enqueue(y * width)
        enqueue(y * width + width - 1)

    while queue:
        index = queue.popleft()
        x, y = index % width, index // width
        if x:
            enqueue(index - 1)
        if x + 1 < width:
            enqueue(index + 1)
        if y:
            enqueue(index - width)
        if y + 1 < height:
            enqueue(index + width)

    visible = [index for index, is_background in enumerate(transparent) if not is_background]
    if not visible:
        raise ValueError(f"프레임에서 캐릭터를 찾을 수 없습니다: {region}")

    min_x = min(index % width for index in visible)
    max_x = max(index % width for index in visible) + 1
    min_y = min(index // width for index in visible)
    max_y = max(index // width for index in visible) + 1
    output_width, output_height = max_x - min_x, max_y - min_y
    rgba = bytearray(output_width * output_height * 4)

    for y in range(min_y, max_y):
        for x in range(min_x, max_x):
            source_index = y * width + x
            target_index = ((y - min_y) * output_width + x - min_x) * 4
            if not transparent[source_index]:
                rgba[target_index:target_index + 3] = bytes(pixels[source_index])
                rgba[target_index + 3] = 255

    _write_rgba_png(output_path, output_width, output_height, rgba)
    return output_width, output_height


def _grid_regions(start_x, start_y, count):
    return [
        (start_x + index * 97, start_y, start_x + index * 97 + 88, start_y + 90)
        for index in range(count)
    ]


FRAME_REGIONS = {
    "걷기": _grid_regions(15, 179, 8),
    "달리기": _grid_regions(15, 293, 4),
    "점프": [
        (404, 293, 476, 382),
        (476, 293, 542, 382),
        (542, 284, 611, 382),
        (611, 293, 688, 382),
        (710, 293, 783, 382),
    ],
    "공격": _grid_regions(15, 435, 8),
    "히트": _grid_regions(15, 670, 4),
    "사망": _grid_regions(402, 670, 4),
}


def _load_animations(temp_directory):
    asset_names = ("Sprite_Sheet_Ninja_Turtle.png", "Sprite_sheet_Ninja_Turtle.png")
    sheet_path = next(
        (Path(__file__).with_name(name) for name in asset_names if Path(__file__).with_name(name).is_file()),
        None,
    )
    if sheet_path is None:
        expected_path = Path(__file__).with_name(asset_names[0])
        raise FileNotFoundError(f"스프라이트 시트를 찾을 수 없습니다: {expected_path}")

    sheet_width, sheet_height, rows = _decode_png(sheet_path)
    sheet_edges = [
        tuple(rows[y][x * 3:x * 3 + 3])
        for y in range(40, sheet_height - 40)
        for x in (0, 1, sheet_width - 2, sheet_width - 1)
    ]
    sheet_background = Counter(sheet_edges).most_common(1)[0][0]
    animations = []
    for animation_name, regions in FRAME_REGIONS.items():
        frames = []
        for frame_index, region in enumerate(regions):
            frame_path = Path(temp_directory) / f"{animation_name}_{frame_index}.png"
            frame_width, frame_height = _extract_frame(rows, sheet_width, sheet_background, region, frame_path)
            frames.append((load_image(str(frame_path)), frame_width, frame_height))
        animations.append((animation_name, frames))
    return animations


def _quit_requested():
    for event in get_events():
        if event.type == SDL_QUIT:
            return True
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return True
    return False


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        with tempfile.TemporaryDirectory(prefix="ninja_turtle_frames_") as temp_path:
            temp_directory = Path(temp_path)
            animations = _load_animations(temp_directory)

            while True:
                should_quit = False
                for _, frames in animations:
                    for _ in range(REPEAT_COUNT):
                        for image, frame_width, frame_height in frames:
                            if _quit_requested():
                                should_quit = True
                                break

                            scale = min(
                                CANVAS_WIDTH * 0.68 / frame_width,
                                CANVAS_HEIGHT * 0.62 / frame_height,
                            )
                            clear_canvas()
                            image.draw(
                                CANVAS_WIDTH / 2,
                                CANVAS_HEIGHT / 2,
                                frame_width * scale,
                                frame_height * scale,
                            )
                            update_canvas()
                            delay(FRAME_DELAY)
                        if should_quit:
                            break
                    if should_quit:
                        break
                    delay(PAUSE_SECONDS)
                if should_quit:
                    break
    finally:
        close_canvas()


if __name__ == "__main__":
    main()

