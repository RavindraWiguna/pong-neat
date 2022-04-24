import pygame
from colorData import WHITE, GRAY
from paddle import Paddle
from ball import Ball
from random import randint
from math import sqrt
#=========================================SETUP PHASE=====================
# Initialize pygame
pygame.init()

# Set windows dimensions
WIDTH, HEIGHT = 640, 480
HALF_W, HALF_H = WIDTH//2, HEIGHT//2
# Create pygame window object
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
# Set the window's name
pygame.display.set_caption("PING PONG")
# Set desired fps
FPS = 60

# Game setup
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 80
X_OFFSET = 0
BALL_RADIUS = 10
BALL_INIT_VEL = (3, 3)
# BALL_INIT_VEL = [3, 3]
SCORE_FONT = pygame.font.SysFont('comicsans', 50)
#==========================================================================

def score_handler(left_score, right_score, ball:Ball, left_paddle:Paddle, right_paddle:Paddle):
    if(ball.x <= 0):
        right_score+=1
        ball.x = HALF_W
        ball.y = HALF_H + randint(-20, 20)
        ball.vel = list(BALL_INIT_VEL)
    elif(ball.x >= WIDTH):
        left_score+=1
        ball.x = HALF_W
        ball.y = HALF_H + randint(-20, 20)
        ball.vel = list(BALL_INIT_VEL)
    return left_score, right_score

def circleRect(cx, cy, radius, rx, ry, rw, rh):

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



def ball_collision_handler(ball:Ball, left_paddle:Paddle, right_paddle:Paddle):
    # Check collision against border (up and down)

    if( (ball.y + ball.radius >= HEIGHT) or (ball.y - ball.radius <= 0)):
        ball.vel[1] *= -1
    
    # Check collision against paddle
    left_hit = circleRect(ball.x, ball.y, ball.radius, left_paddle.x, left_paddle.y, left_paddle.width, left_paddle.height)
    right_hit = circleRect(ball.x, ball.y, ball.radius, right_paddle.x, right_paddle.y, right_paddle.width, right_paddle.height)
    
    if(left_hit):
        if(not left_paddle.just_collide):
            ball.vel[0] *= -1
            left_paddle.just_collide = True
    else:
        left_paddle.just_collide = False
    
    if(right_hit):
        if(not right_paddle.just_collide):
            ball.vel[0] *= -1
            right_paddle.just_collide = True
    else:
        right_paddle.just_collide=False
    



def handle_paddle_movement(keys, left_paddle:Paddle, right_paddle:Paddle):
    if(keys[pygame.K_w]):
        left_paddle.move(up=True)
    if(keys[pygame.K_s]):
        left_paddle.move(up=False)

    if(keys[pygame.K_UP]):
        right_paddle.move(up=True)
    if(keys[pygame.K_DOWN]):
        right_paddle.move(up=False)

def draw(win:pygame.surface.Surface, paddles, ball, left_score, right_score):
    # Fill the background color
    win.fill(GRAY)
    # Draw scores
    left_score_text = SCORE_FONT.render(f'{left_score}', 1, WHITE)
    right_score_text = SCORE_FONT.render(f'{right_score}', 1, WHITE)
    win.blit(left_score_text,(WIDTH//4 - left_score_text.get_width()//2, 20))
    win.blit(right_score_text,(3*WIDTH//4 - right_score_text.get_width()//2, 20))

    # Draw the paddles
    for paddle in paddles:
        paddle.render(win)
    # Draw the ball
    ball.render(win)

    # Draw separator dash line
    for i in range(10, HEIGHT, HEIGHT//10):
        if(i % 2 == 0):
            pygame.draw.rect(win, WHITE, (HALF_W, i, 10, 30))
    pygame.display.update()         # Update the frame showed

def main():
    isRunning = True                # Boolean to trigger when should we end the game
    clock = pygame.time.Clock()     # Clock to maintain FPS
    # paddles
    left_paddle = Paddle(X_OFFSET, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT, HEIGHT-PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - X_OFFSET - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT, HEIGHT-PADDLE_HEIGHT)
    # ball
    ball = Ball(HALF_W, HALF_H, BALL_RADIUS, list(BALL_INIT_VEL))

    # Scores
    left_score = 0
    right_score = 0

    # Main game loop
    while isRunning:
        # Ensure the loop running at desired fps
        clock.tick(FPS)

        # Iterate through every pygame events
        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                isRunning = False
                break
        # Get list of boolean for each key
        keys = pygame.key.get_pressed()
        if(keys[pygame.K_q]):
            isRunning = False
            break
        # move the paddle (if needed)
        handle_paddle_movement(keys, left_paddle, right_paddle)
        # Ball movement stuff
        ball_collision_handler(ball, left_paddle, right_paddle)
        ball.move()
        # Update score
        left_score, right_score = score_handler(left_score, right_score, ball, left_paddle, right_paddle)
        
        # Render game's frame
        draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score)

    pygame.quit()


if __name__ == "__main__":
    main()
    # ve2 = pygame.Vector2((2, 2))
    # surfaceNormal = pygame.Vector2((-1, 0))
    # print(ve2)
    # print(ve2.length())
    # print(surfaceNormal)
    # print(surfaceNormal.length())

    # dotProduct = surfaceNormal.dot(ve2)
    # print(dotProduct)
    # surfaceNormal.scale_to_length(2*dotProduct)
    # print(surfaceNormal)
    # # ve2.scale_to_length(dotProduct)
    # print(ve2 - surfaceNormal)