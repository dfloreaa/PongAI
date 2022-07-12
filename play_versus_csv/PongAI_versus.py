from time import time
from turtle import right
import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np
import sys
import os
# os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
font = pygame.font.SysFont('arial', 25)
WIDTH, HEIGHT = 700, 500

FPS = 60

y_final = 0

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
RED = (255, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7

SCORE_FONT = pygame.font.SysFont("comicsans", 50)
RESET_FONT = pygame.font.SysFont("arial", 20)

WINNING_SCORE = 5
SUDDEN_DEATH_TIME = 20
SUDDEN_DEATH_DELTA = 0.3

IMAGE_ALPHA = 64

class Paddle:
    COLOR = WHITE
    VEL = 4

    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height
        self.skin = None

    def draw(self, win):
        if self.skin is not None:
            rect = self.skin.get_rect()
            if self.x > WIDTH//2:
                rect = rect.move((WIDTH//2, 0))
            else:
                rect = rect.move((0, 0))
            win.blit(self.skin, rect)

        pygame.draw.rect(
            win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y


class Ball:
    global y_final
    MAX_VEL = 5
    COLOR = WHITE

    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL * random.choice([-1, 1])
        self.y_vel = random.uniform(-2.5, 2.5)
        self.bounces = 0

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.radius)
        # pygame.draw.circle(win, (255,0,0), (WIDTH - 30, y_final), 3)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = 0
        self.x_vel = self.MAX_VEL * random.choice([-1, 1])
        self.bounces = 0

class PongAI:

    def __init__(self, w=WIDTH, h=HEIGHT, vis=True):
        self.w = w
        self.h = h
        self.vis = vis
        self.start = True
        if self.vis:   
            self.WIN = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Pong")
            pygame.init()
            # init display
            self.display = pygame.display.set_mode((self.w, self.h))
            pygame.display.set_caption('PongAI')
            self.clock = pygame.time.Clock()
        self.score = 0
        self.left_score = 0
        self.right_score = 0
        self.hitpoint = 0
        self.won = True
        self.lwin = False
        self.rwin = False
        self.left_username = "Player 1"
        self.right_username = "Player 2"
        self.left_paddle_skin = None
        self.right_paddle_skin = None
        self.start_time = time()
        self.reset()

    def set_usernames(self, left, right):
        self.left_username = left
        if os.path.isfile(f"data/images/{left}.png"):
            self.left_paddle_skin = f"data/images/{left}.png"
        elif os.path.isfile(f"data/images/{left}.jpg"):
            self.left_paddle_skin = f"data/images/{left}.jpg"
        elif os.path.isfile(f"data/images/{left}.jpeg"):
            self.left_paddle_skin = f"data/images/{left}.jpeg"

        self.right_username = right
        if os.path.isfile(f"data/images/{right}.png"):
            self.right_paddle_skin = f"data/images/{right}.png"
        elif os.path.isfile(f"data/images/{right}.jpg"):
            self.right_paddle_skin = f"data/images/{right}.jpg"
        elif os.path.isfile(f"data/images/{right}.jpeg"):
            self.right_paddle_skin = f"data/images/{right}.jpeg"
        
    def set_skins(self):
        if self.left_paddle_skin:
            self.left_paddle.skin = pygame.image.load(self.left_paddle_skin)
            self.left_paddle.skin = pygame.transform.scale(self.left_paddle.skin, (WIDTH//2, HEIGHT))
            self.left_paddle.skin.set_alpha(IMAGE_ALPHA)
        if self.right_paddle_skin:
            self.right_paddle.skin = pygame.image.load(self.right_paddle_skin)
            self.right_paddle.skin = pygame.transform.scale(self.right_paddle.skin, (WIDTH//2, HEIGHT))
            self.right_paddle.skin.set_alpha(IMAGE_ALPHA)

    def reset(self):
        global y_final
        # init game state
        self.MAX_X = WIDTH
        self.left_paddle = Paddle(10, HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT //
                            2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.set_skins()
        self.ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)
        self.ball.bounces = 0

        self.left_score = 0
        self.right_score = 0

        self.frame_iteration = 0
        self.won = False
        self.lwin = False
        self.rwin = False
        self.start_time = time()

    def play_step(self, action_left, action_right):
        if not self.won:
            if self.vis:
                # 5. update ui and clock
                self.draw(self.WIN, [self.left_paddle, self.right_paddle], self.left_score, self.right_score)
                self.clock.tick(FPS)

            if self.left_score >= WINNING_SCORE:
                self.won = True
                win_text = f"{self.left_username} Player Won!"
                self.lwin = True
            elif self.right_score >= WINNING_SCORE:
                self.won = True
                win_text = f"{self.right_username} Player Won!"
                self.rwin = True

        if self.start:
            self.won = True
            self.start = False
            win_text = "Bienvenid@s a PongAI"

        if self.won:
            if self.vis:
                text = SCORE_FONT.render(win_text, 1, WHITE)
                pygame.draw.rect(self.WIN, GRAY, (WIDTH//2 - text.get_width()//2 - 20, HEIGHT//2 - text.get_height(), text.get_width() + 40, text.get_height() * 3))
                self.WIN.blit(text, (WIDTH//2 - text.get_width() //
                                2, HEIGHT//2 - text.get_height()//2))
                reset_text = RESET_FONT.render("Presiona cualquier tecla para reiniciar", 1, WHITE)
                self.WIN.blit(reset_text, (WIDTH//2 - reset_text.get_width() //
                                2, HEIGHT//2 - reset_text.get_height()//2 + 40))
                pygame.display.update()
                pygame.event.clear()

                while self.won:
                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        self.reset()

        if not self.won:

            self.frame_iteration += 1
            # 1. collect user input
            if self.vis:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()

            # 2. move
            self._move_left(action_left) # update the head
            self._move_right(action_right) # update the head
            self.ball.move()
            if self.handle_collision():
                self.reset()

            if self.ball.x < 0:
                self.right_score += 1
                self.start_time = time()
                self.ball.reset()
            elif self.ball.x > WIDTH:
                self.left_score += 1
                self.start_time = time()
                self.ball.reset()

            if self.ball.x_vel < 0:
                delta_time = time() - self.start_time
                if delta_time > SUDDEN_DEATH_TIME:
                    self.ball.x_vel = -self.ball.MAX_VEL - (delta_time - SUDDEN_DEATH_TIME) * SUDDEN_DEATH_DELTA
            else:
                delta_time = time() - self.start_time
                if delta_time > SUDDEN_DEATH_TIME:
                    self.ball.x_vel = self.ball.MAX_VEL + (delta_time - SUDDEN_DEATH_TIME) * SUDDEN_DEATH_DELTA

        reward = 0
        game_over = False
        past_score = 0

        # 6. return game over and score
        # print(self.score)
        return reward, game_over, past_score 

    def handle_collision(self):
        if self.ball.y + self.ball.radius >= HEIGHT:
            self.ball.y = HEIGHT - self.ball.radius
            self.ball.y_vel *= -1
            self.ball.bounces += 1
        elif self.ball.y - self.ball.radius <= 0:
            self.ball.y = 0 + self.ball.radius
            self.ball.y_vel *= -1
            self.ball.bounces += 1

        if self.ball.x_vel < 0:
            if self.ball.y >= self.left_paddle.y and self.ball.y <= self.left_paddle.y + self.left_paddle.height:
                if self.ball.x - self.ball.radius <= self.left_paddle.x + self.left_paddle.width:

                    self.ball.x_vel *= -1

                    middle_y = self.left_paddle.y + self.left_paddle.height / 2
                    difference_in_y = middle_y - self.ball.y
                    reduction_factor = (self.left_paddle.height / 2) / self.ball.MAX_VEL
                    y_vel = difference_in_y / reduction_factor + random.uniform(-1.5, 1.5)
                    if y_vel > 5:
                        y_vel = 5
                    elif y_vel < -5:
                        y_vel = -5
                    self.ball.y_vel = -1 * y_vel
                    self.ball.bounces = 0

        else:
            if self.ball.y >= self.right_paddle.y and self.ball.y <= self.right_paddle.y + self.right_paddle.height:
                if self.ball.x + self.ball.radius >= self.right_paddle.x:

                    self.ball.x_vel *= -1

                    middle_y = self.right_paddle.y + self.right_paddle.height / 2
                    difference_in_y = middle_y - self.ball.y
                    reduction_factor = (self.right_paddle.height / 2) / self.ball.MAX_VEL
                    y_vel = difference_in_y / reduction_factor + random.uniform(-1.5, 1.5)
                    if y_vel > 5:
                        y_vel = 5
                    elif y_vel < -5:
                        y_vel = -5
                    self.ball.y_vel = -1 * y_vel
                    self.ball.bounces = 0
        return False
    
    def draw(self, win, paddles, left_score, right_score):
        win.fill(BLACK)

        for paddle in paddles:
            paddle.draw(win)

        left_score_text = SCORE_FONT.render(f"{left_score}", 1, WHITE)
        right_score_text = SCORE_FONT.render(f"{right_score}", 1, WHITE)
        user1 = RESET_FONT.render(self.left_username, 1, WHITE)
        user2 = RESET_FONT.render(self.right_username, 1, WHITE)
        win.blit(left_score_text, (WIDTH//4 - left_score_text.get_width()//2, 50))
        win.blit(right_score_text, (WIDTH * (3/4) -
                                    right_score_text.get_width()//2, 50))
        win.blit(user1, (WIDTH//4 - user1.get_width()//2, 20))
        win.blit(user2, (WIDTH * (3/4) - user2.get_width()//2, 20))

        for i in range(10, HEIGHT, HEIGHT//20):
            if i % 2 == 1:
                continue
            pygame.draw.rect(win, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//20))

        if time() - self.start_time > SUDDEN_DEATH_TIME:
            sudden_death_text = RESET_FONT.render(f"SUDDEN DEATH", 1, RED)
            sudden_death_percentage = RESET_FONT.render(f"{int(abs(self.ball.x_vel/self.ball.MAX_VEL) * 100)}%", 1, RED)
            pygame.draw.rect(self.WIN, BLACK, (WIDTH//2 - sudden_death_text.get_width()//2 - 10, 0 + 20, sudden_death_text.get_width() + 20, sudden_death_text.get_height() + 20))
            win.blit(sudden_death_text, (WIDTH//2 - sudden_death_text.get_width()//2, 20))
            win.blit(sudden_death_percentage, (WIDTH//2 - sudden_death_percentage.get_width()//2, 40))

        self.ball.draw(win)
        pygame.display.update()

    def _move_left(self, action):
        if action == 0 and self.left_paddle.y - self.left_paddle.VEL >= 0: # Hacia arriba
            self.left_paddle.move(up=True)
        if action == 2 and self.left_paddle.y + self.left_paddle.VEL + self.left_paddle.height <= HEIGHT: #Hacia abajo
            self.left_paddle.move(up=False)


    def _move_right(self, action):
        if action == 0 and self.right_paddle.y - self.right_paddle.VEL >= 0: # Hacia arriba
            self.right_paddle.move(up=True)
        if action == 2 and self.right_paddle.y + self.right_paddle.VEL + self.right_paddle.height <= HEIGHT: #Hacia abajo
            self.right_paddle.move(up=False)