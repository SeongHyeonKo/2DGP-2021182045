# 실습 과제 진행
import math
from pico2d import *

open_canvas(800, 600)

character = load_image("character.png")

def draw_character(x, y):
    clear_canvas()
    character.draw(x, y)
    update_canvas()
    delay(0.1)

def draw_circle():
    print("CIRCLE")
    for deg in range(0, 360, 10):
        rad = math.radians(deg)
        x = 400 + 200 * math.cos(rad)
        y = 400 + 200 * math.sin(rad)
        draw_character(x, y)
    pass

def draw_top():
    print('TOP')
    for x in range(50, 750, 10):
        draw_character(x, 550)

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
    for y in range(50, 550, 10):
        draw_character(50, y)
    pass

A = (100, 100)
B = (700, 100)
C = (400, 500)

def move_A_to_B():
    print('move_A_to_B')
    for x in range (100, 700, 10):
        draw_character(x, 100)
    pass

def move_B_to_C():
    print('move_B_to_C')
    y = 100
    for x in range(700, 400, -10):
        draw_character(x, y)
        y += 13.33
    pass

def move_C_to_A():
    print('move_C_to_A')
    y = 500
    for x in range(400, 100, -10):
        draw_character(x, y)
        y -= 13.33
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
    move_A_to_B()
    move_B_to_C()
    pass

while True:
    draw_circle()
    draw_rectangle()
    draw_triangle()
    break
    pass

close_canvas()