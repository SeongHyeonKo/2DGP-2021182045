import time

from pico2d import load_image
from transitions import Machine


class Boy:
    # The only state for now. Later states and transitions can be added here.
    states = ['IDLE']

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.frame_time = time.monotonic()
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(model=self, states=Boy.states, initial='IDLE')

    def update(self):
        if self.state == 'IDLE':
            now = time.monotonic()
            if now - self.frame_time >= 0.12:
                self.frame = (self.frame + 1) % 8
                self.frame_time = now

    def draw(self):
        if self.face_dir == 1:
            self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
        else:
            self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
