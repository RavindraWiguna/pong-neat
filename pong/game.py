import pygame
from .colorData import WHITE, GRAY
from .paddle import Paddle
from .ball import Ball
from random import randint
from math import sqrt
#=========================================SETUP PHASE=====================
# Initialize pygame
pygame.init()

class GameInformation:
    def __init__(self, left_hits, right_hits, left_score, right_score):
        self.left_hits = left_hits
        self.right_hits = right_hits
        self.left_score = left_score
        self.right_score = right_score

class Game:
    # Game setup
    PADDLE_WIDTH, PADDLE_HEIGHT = 20, 80
    X_OFFSET = 0
    BALL_RADIUS = 10
    BALL_INIT_VEL = [3, 3]
    SCORE_FONT = pygame.font.SysFont('comicsans', 50)
    
    def __init__(self, window, window_width, window_height) -> None:
        self.window = window
        self.window_width = window_width
        self.window_height = window_height

        # Create paddle
        self.left_paddle = Paddle(
            self.X_OFFSET, self.window_height//2 - self.PADDLE_HEIGHT//2, 
            self.PADDLE_WIDTH, self.PADDLE_HEIGHT, self.window_height-self.PADDLE_HEIGHT)
        self.right_paddle = Paddle(
            self.window_width - self.X_OFFSET - self.PADDLE_WIDTH, 
            self.window_height//2 - self.PADDLE_HEIGHT//2, self.PADDLE_WIDTH, self.PADDLE_HEIGHT, self.window_height-self.PADDLE_HEIGHT)
        # Create ball
        self.ball = Ball(self.window_width//2, self.window_height//2, self.BALL_RADIUS, self.BALL_INIT_VEL)

        # Store scores and hits
        self.left_score = 0
        self.right_score = 0
        self.left_hits = 0
        self.right_hits = 0
    
    def score_handler(self):
        if(self.ball.x <= 0):
            self.right_score+=1
            self.ball.reset()
        elif(self.ball.x >= self.window_width):
            self.left_score+=1
            self.ball.reset()

    def _paddle_collision_handler(self, paddle:Paddle):
        rx = paddle.x
        ry = paddle.y
        rw = paddle.width
        rh = paddle.height
        cx = self.ball.x
        cy = self.ball.y
        radius = self.ball.radius
        # temporary variables to set edges for testing
        testX = cx
        testY = cy
        # msg = ("left", "right", "top", "bottom", "nothing")
        # m_id = 4
        # which edge is closest?
        if (cx < rx):
            # m_id = 0
            testX = rx          # test left edge
        elif (cx > rx+rw):
            # m_id = 1
            testX = rx+rw       # right edge
    
        if (cy < ry):
            # m_id = 2
            testY = ry          # top edge
        elif (cy > ry+rh):
            # m_id = 3
            testY = ry+rh     # bottom edge

        # get distance from closest edges
        distX = cx-testX
        distY = cy-testY
        distance = sqrt( (distX*distX) + (distY*distY) )

        # if the distance is less than the radius, collision!
        if (distance <= radius):
            return True
        return False

    def _ball_collision_handler(self):
        # Check collision against border (up and down)

        if( (self.ball.y + self.ball.radius >= self.window_height) or 
            (self.ball.y - self.ball.radius <= 0) ):
            self.ball.vel[1] *= -1
        
        # Check collision against paddle
        left_hit = self._paddle_collision_handler(self.left_paddle)
        right_hit = self._paddle_collision_handler(self.right_paddle)
        
        if(left_hit):
            if(not self.left_paddle.just_collide):
                self.ball.vel[0] *= -1
                self.left_paddle.just_collide = True
                self.left_hits+=1
        else:
            self.left_paddle.just_collide = False
        
        if(right_hit):
            if(not self.right_paddle.just_collide):
                self.ball.vel[0] *= -1
                self.right_paddle.just_collide = True
                self.right_hits+=1
        else:
            self.right_paddle.just_collide=False

    def _paddle_movement_handler(self, control_left=True, move_up=True):
        if(control_left):
            return self.left_paddle.move(move_up)
        else:
            return self.right_paddle.move(move_up)


    def _draw_score(self):
        # Draw scores
        left_score_text = self.SCORE_FONT.render(f'{self.left_score}', 1, WHITE)
        right_score_text = self.SCORE_FONT.render(f'{self.right_score}', 1, WHITE)
        self.window.blit(left_score_text,(self.window_width//4 - left_score_text.get_width()//2, 20))
        self.window.blit(right_score_text,(3*self.window_width//4 - right_score_text.get_width()//2, 20))


    def _draw_paddle(self):
        self.left_paddle.render(self.window)
        self.right_paddle.render(self.window)

    def _draw_ball(self):
        self.ball.render(self.window)

    def _draw_divider(self):
        # Draw separator dash line
        for i in range(10, self.window_height, self.window_height//10):
            if(i % 2 == 0):
                pygame.draw.rect(self.window, WHITE, (self.window_width//2, i, 10, 30))

    def draw(self, isDrawScore=True):
        # Fill the background color
        self.window.fill(GRAY)

        if(isDrawScore):
            self._draw_score()

        self._draw_paddle()
        self._draw_ball()
        self._draw_divider()
        
        # pygame.display.update()         # Update the frame showed

    def loop(self):
        """
        Executes a single game loop.
        :returns: GameInformation instance stating score 
                  and hits of each paddle.
        """
        self.ball.move()
        self._ball_collision_handler()

        self.score_handler()

        game_info = GameInformation(
            self.left_hits, self.right_hits, self.left_score, self.right_score)

        return game_info

    def reset(self):
        """Resets the entire game."""
        self.ball.reset()
        self.left_paddle.reset()
        self.right_paddle.reset()
        self.left_score = 0
        self.right_score = 0
        self.left_hits = 0
        self.right_hits = 0
