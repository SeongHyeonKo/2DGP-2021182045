import math
import os

from pico2d import *

open_canvas(800, 600)

character = load_image(os.path.join(os.path.dirname(__file__), "character.png"))


def draw_character(x, y):
    clear_canvas()
    character.draw(x, y)
    update_canvas()
    delay(0.01)


def draw_circle():
    for degree in range(0, 360, 5):
        angle = math.radians(degree)
        x = 400 + 200 * math.cos(angle)
        y = 300 + 200 * math.sin(angle)
        draw_character(x, y)


def draw_segment(start, end):
    distance = math.hypot(end[0] - start[0], end[1] - start[1])
    steps = max(1, math.ceil(distance / 10))
    for step in range(steps + 1):
        t = step / steps
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t
        draw_character(x, y)


def draw_rectangle():
    corners = [(50, 50), (750, 50), (750, 550), (50, 550), (50, 50)]
    for start, end in zip(corners, corners[1:]):
        draw_segment(start, end)


while True:
    draw_circle()
    draw_rectangle()
