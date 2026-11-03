import time


class AutoRun:
    """Behavior for the AUTO_RUN state: fast, enlarged, automatic movement."""

    DURATION = 5.0
    SPEED = 450.0
    SCALE = 1.6
    HALF_WIDTH = 50 * SCALE

    def __init__(self, boy):
        self.boy = boy
        self.started_at = 0.0

    def enter(self):
        self.started_at = time.monotonic()
        self.boy.frame = 0
        self.boy.frame_time = self.started_at

    def update(self, now, dt):
        if now - self.started_at >= self.DURATION:
            self.boy.finish_auto_run()
            return

        left = self.HALF_WIDTH
        right = 800 - self.HALF_WIDTH
        next_x = self.boy.x + self.boy.face_dir * self.SPEED * dt
        while next_x < left or next_x > right:
            if next_x > right:
                next_x = right - (next_x - right)
                self.boy.face_dir = -1
            elif next_x < left:
                next_x = left + (left - next_x)
                self.boy.face_dir = 1
        self.boy.x = next_x

        if now - self.boy.frame_time >= self.boy.FRAME_INTERVAL:
            self.boy.frame = (self.boy.frame + 1) % 8
            self.boy.frame_time = now

    def draw(self):
        self.boy.draw_running(scale=self.SCALE, y_offset=30)
