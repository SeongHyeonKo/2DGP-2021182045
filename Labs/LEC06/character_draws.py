# 실습 과제 진행
import math
from pico2d import *

open_canvas(800, 600)

character = load_image("character.png")


def move_circle():
    print("CIRCLE")
    for deg in range(0, 360, 1):
        rad = math.radians(deg)
        x = 400 + 200 * math.cos(rad)
        y = 400 + 200 * math.sin(rad)
    clear_canvas()
    character.draw(x, y)
    update_canvas()
    delay(0.1)
    pass

def move_rectangle():
    print("RECTANGLE")
    pass

def move_triangle():
    print("TRIANGLE")
    pass

while True:
    move_circle()
    move_rectangle()
    move_triangle()
    pass

close_canvas()