import math
import time

from pico2d import load_image
from transitions import Machine


class Boy:
    states = [
        {'name': 'IDLE', 'on_enter': 'restart_idle_timer'},
        {'name': 'RUN', 'on_enter': 'enter_run'},
        {'name': 'SLEEP', 'on_enter': 'enter_sleep'},
    ]

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        now = time.monotonic()
        self.frame_time = now
        self.idle_since = now
        self.last_update = now
        self.face_dir = 1
        self.held_directions = []
        self.run_speed = 200
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(
            model=self,
            states=Boy.states,
            initial='IDLE',
            transitions=[
                {'trigger': 'go_to_sleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'start_running', 'source': 'IDLE', 'dest': 'RUN'},
                {'trigger': 'start_running', 'source': 'SLEEP', 'dest': 'RUN'},
                {'trigger': 'stop_running', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'wake_up', 'source': 'SLEEP', 'dest': 'IDLE'},
            ],
        )

    def restart_idle_timer(self):
        now = time.monotonic()
        self.idle_since = now
        self.frame_time = now

    def enter_run(self):
        self.frame = 0
        self.frame_time = time.monotonic()

    def enter_sleep(self):
        self.frame = 0

    def wake_up_from_space(self):
        if self.state == 'SLEEP':
            self.wake_up()

    def press_direction(self, direction):
        if direction in self.held_directions:
            self.held_directions.remove(direction)
        self.held_directions.append(direction)
        self.face_dir = direction
        if self.state in ('IDLE', 'SLEEP'):
            self.start_running()

    def release_direction(self, direction):
        if direction in self.held_directions:
            self.held_directions.remove(direction)
        if self.state == 'RUN':
            if self.held_directions:
                self.face_dir = self.held_directions[-1]
            else:
                self.stop_running()

    def update(self):
        now = time.monotonic()
        dt = now - self.last_update
        self.last_update = now

        if self.state == 'IDLE':
            if now - self.idle_since >= 5.0:
                self.go_to_sleep()
            elif now - self.frame_time >= 0.12:
                self.frame = (self.frame + 1) % 8
                self.frame_time = now
        elif self.state == 'RUN':
            self.x = max(50, min(750, self.x + self.face_dir * self.run_speed * dt))
            if now - self.frame_time >= 0.12:
                self.frame = (self.frame + 1) % 8
                self.frame_time = now

    def draw(self):
        if self.state == 'SLEEP':
            # Rotate the standing sprite onto its side to show the boy lying down.
            idle_row = 300 if self.face_dir == 1 else 200
            sleep_angle = self.face_dir * math.pi / 2
            self.image.clip_composite_draw(
                0, idle_row, 100, 100, sleep_angle, '', self.x, self.y - 25, 100, 100
            )
            return

        if self.state == 'RUN':
            row = 100 if self.face_dir == 1 else 0
            self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)
        elif self.face_dir == 1:
            self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
        else:
            self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
