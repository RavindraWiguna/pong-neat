from .colorData import WHITE
from pygame import draw

'''
A Class for paddle in ping ponng
'''
class Paddle:
    COLOR = WHITE
    # the y velocity of the paddle
    VEL = 4
    def __init__(self, x, y, width, height, max_height) -> None:
        # x and y here are the left and top coordinate of the rectangle
        self.init_x = x
        self.init_y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # the maximum value for y for the paddle (so that it wont go off the sreen)
        self.max_height = max_height
        # to prevent to bouncy ass ball bug
        self.just_collide = False
    
    def render(self, win):
        draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        # returned value used to measure nn fitness
        isMoved = True
        if(up):
            self.y -= self.VEL
        else:
            self.y += self.VEL
        
        # fix the coordinate
        if(self.y < 0):
            self.y = 0
            isMoved=False
        elif(self.y > self.max_height):
            self.y = self.max_height
            isMoved = False
        
        return isMoved
    
    def reset(self):
        # set the paddle coordinate to where it started
        self.x = self.init_x
        self.y = self.init_y