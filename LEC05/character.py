from pico2d import *

open_canvas(800, 600)

character = load_image('character.png')
##grass = load_image('grass.png')

##grass.draw(400, 30)
character.draw(400, 30)

x = 30
y = 30
while True:
    clear_canvas()
    ##grass.draw(400, 30)
    character.draw(x, y)
    if y == 30:
        x += 10

    if x == 770:
        y += 10

    if y == 550:
        x -= 10

    if x == 30:
        y -= 10

    update_canvas()

    delay(0.01)

close_canvas()

