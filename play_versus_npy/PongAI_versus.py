from time import time
from turtle import right
import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np
import sys
# import os
# os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
font = pygame.font.SysFont('arial', 25)
WIDTH, HEIGHT = 700, 500

FPS = 60

y_final = 0

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7

SCORE_FONT = pygame.font.SysFont("comicsans", 50)
RESET_FONT = pygame.font.SysFont("arial", 20)
WINNING_SCORE = 3

class Paddle:
    COLOR = WHITE
    VEL = 4

    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height

    def draw(self, win):
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
        self.x_vel = self.MAX_VEL
        self.bounces = 0

class PongAI:

    def __init__(self, w=WIDTH, h=HEIGHT, vis=True):
        self.w = w
        self.h = h
        self.vis = vis
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
        self.won = False
        self.lwin = False
        self.rwin = False
        self.reset()


    def reset(self):
        global y_final
        # init game state
        self.MAX_X = WIDTH
        self.left_paddle = Paddle(10, HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT //
                            2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)
        self.ball.bounces = 0

        self.left_score = 0
        self.right_score = 0

        self.frame_iteration = 0
        self.won = False
        self.lwin = False
        self.rwin = False

    def play_step(self, action_left, action_right):
        if not self.won:
            if self.vis:
                # 5. update ui and clock
                self.draw(self.WIN, [self.left_paddle, self.right_paddle], self.left_score, self.right_score)
                self.clock.tick(FPS)

            if self.left_score >= WINNING_SCORE:
                self.won = True
                win_text = "Left Player Won!"
                self.lwin = True
            elif self.right_score >= WINNING_SCORE:
                self.won = True
                win_text = "Right Player Won!"
                self.rwin = True

        if self.won:
            if self.vis:
                text = SCORE_FONT.render(win_text, 1, WHITE)
                self.WIN.blit(text, (WIDTH//2 - text.get_width() //
                                2, HEIGHT//2 - text.get_height()//2))
                reset_text = RESET_FONT.render("Presiona cualquier tecla para reiniciar", 1, WHITE)
                self.WIN.blit(reset_text, (WIDTH//2 - reset_text.get_width() //
                                2, HEIGHT//2 - reset_text.get_height()//2 + 60))
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
                self.ball.reset()
            elif self.ball.x > WIDTH:
                self.left_score += 1
                self.ball.reset()

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

        left_score_text = SCORE_FONT.render(f"{left_score}", 1, WHITE)
        right_score_text = SCORE_FONT.render(f"{right_score}", 1, WHITE)
        win.blit(left_score_text, (WIDTH//4 - left_score_text.get_width()//2, 20))
        win.blit(right_score_text, (WIDTH * (3/4) -
                                    right_score_text.get_width()//2, 20))

        for paddle in paddles:
            paddle.draw(win)

        for i in range(10, HEIGHT, HEIGHT//20):
            if i % 2 == 1:
                continue
            pygame.draw.rect(win, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//20))

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