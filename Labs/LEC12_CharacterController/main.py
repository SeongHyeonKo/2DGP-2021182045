from pico2d import *

from boy import Boy
from grass import Grass


def handle_events():
    global running

    for event in get_events():
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                running = False
            elif event.key == SDLK_a:
                boy.start_auto_run_from_idle()
            elif event.key == SDLK_SPACE:
                boy.wake_up_from_space()
            elif event.key == SDLK_LEFT:
                boy.press_direction(-1)
            elif event.key == SDLK_RIGHT:
                boy.press_direction(1)
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LEFT:
                boy.release_direction(-1)
            elif event.key == SDLK_RIGHT:
                boy.release_direction(1)


def reset_world():
    global world, boy
    world = [Grass()]
    boy = Boy()
    world.append(boy)


def update_world():
    for game_object in world:
        game_object.update()


def render_world():
    clear_canvas()
    for game_object in world:
        game_object.draw()
    update_canvas()


running = True
open_canvas(800, 600)
reset_world()
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)
close_canvas()
