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


