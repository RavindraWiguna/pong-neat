from .colorData import WHITE
from pygame import draw
from random import randint, choice

class Ball:
    def __init__(self, x, y, radius, init_vel) -> None:
        self.init_x = x
        self.init_y = y
        self.init_vel = init_vel
        self.x = x
        self.y = y
        self.radius = radius
        self.vel = init_vel
    
    def render(self, win):
        draw.circle(win, WHITE, (self.x, self.y), self.radius)
    
    def move(self):
        self.x += self.vel[0] 
        self.y += self.vel[1]

    def reset(self):
        # reset the ball to the center-ish of the sreen with random direction velocity
        self.x = self.init_x
        self.y = self.init_y + randint(-50, 50)
        self.vel[0] = self.init_vel[0] * choice((-1, 1))
        self.vel[1] = self.init_vel[1] * choice((-1, 1))