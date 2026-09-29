# 실습 과제 진행
import math
from pico2d import *

open_canvas(800, 600)

character = load_image("character.png")


def draw_circle():
    print("CIRCLE")
    for deg in range(0, 360, 1):
        rad = math.radians(deg)
        x = 400 + 200 * math.cos(rad)
        y = 400 + 200 * math.sin(rad)
        draw_character(x, y)
    pass


def draw_top():
    print('TOP')
    for x in range(50, 750, 10):
        draw_character(x, 550)

def draw_character(x, y):
    clear_canvas()
    character.draw(x, y)
    update_canvas()
    delay(0.1)

def draw_right():
    print('RIGHT')
    for y in range(550, 50, -10):
        draw_character(750, y)
    pass

def draw_bottom():
    print('BOTTOM')
    for x in range(750, 50, -10):
        draw_character(x, 50)
    pass

def draw_left():
    print('LEFT')
    pass

def draw_rectangle():
    print("RECTANGLE")
    draw_top()
    draw_right()
    draw_bottom()
    draw_left()
    pass

def draw_triangle():
    print("TRIANGLE")
    pass

while True:
    #draw_circle()
    draw_rectangle()
    draw_triangle()
    break
    pass

close_canvas()