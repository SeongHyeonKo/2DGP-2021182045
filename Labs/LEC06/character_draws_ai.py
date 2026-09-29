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


while True:
    draw_circle()

