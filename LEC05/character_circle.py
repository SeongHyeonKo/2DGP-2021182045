import math
from pico2d import *

open_canvas(800, 600)

character = load_image('character.png')

center_x = 400
center_y = 300
radius = 200
angle = 0.0

character.draw(400, 30)

while True:
    clear_canvas()
    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)
    character.draw(x, y)

    update_canvas()

    angle += 0.05

    delay(0.01)


close_canvas()
