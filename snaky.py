#!/usr/bin/env python2
""" Snaky: a snake game using pygame """
import pygame
import random

game_size = game_width, game_height = 80, 60

UP = (0, -1)
DOWN = (0, 1)
RIGHT = (1, 0)
LEFT = (-1, 0)

RUNNING = 0
PAUSED = 1
GAME_OVER = 2

food_color = 249, 38, 114
part_color = 135, 175, 215
font_color = 255, 255, 211
background = 28, 28, 28


class Part():
    """ Snake body part class """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y

    def draw(self, screen):
        screen.fill(part_color, rect=(self.x * 4, self.y * 4, 4, 4))

    def update_pos(self, x, y):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x = x
        self.y = y

    def get_pos(self):
        return (self.x, self.y)


class Snake():
    """ Snake class """
    def __init__(self):
        self.parts = [Part(40, 29), Part(40, 30), Part(40, 31), Part(40, 32)]
        self.motion_x = 0
        self.motion_y = -1

    def draw(self, screen):
        for part in self.parts:
            part.draw(screen)

    def check_dead(self):
        # are we inside the game?
        if not 0 < self.parts[0].x < game_width or not 0 < self.parts[0].y < game_height:
            return True

        # check if we are overlapping
        tmp_pos = []
        for part in self.parts[1:]:
            tmp_pos.append((part.x, part.y))
        if (self.parts[0].x, self.parts[0].y) in tmp_pos:
            return True

        return False

    def tick(self):
        self.parts[0].update_pos(self.parts[0].x + self.motion_x,
                self.parts[0].y + self.motion_y)

        for i in range(1, len(self.parts)):
            self.parts[i].update_pos(self.parts[i - 1].prev_x,
                    self.parts[i - 1].prev_y)

        return self.check_dead()

    def set_motion(self, (x, y)):
        self.motion_x = x
        self.motion_y = y

    def get_motion(self):
        return (self.motion_x, self.motion_y)

    def add_part(self):
        x, y = self.parts[-1].prev_x, self.parts[-1].prev_y
        self.parts.append(Part(x, y))


class Game():
    """ Snake game """
    def __init__(self):
        pygame.init()

        # Setup texts
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 60)
        self.game_over_surface = self.font.render("Game Over", True,
                font_color)
        self.pause_surf = self.font.render("Paused", True,
                font_color)
        self.game_over_size = self.font.size("Game Over")
        self.pause_size = self.font.size("Paused")

        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 20)
        self.press_return_surf = self.font.render("Press Return to start a new game",
                True, font_color)
        self.press_return_size = self.font.size("Press Return to start a new game")
        del self.font

        self.size = game_width * 4, game_height * 4  # 80 x 60
        self.state = RUNNING

        self.snake = Snake()
        self.food = -1, -1
        self.set_food()

        self.screen = pygame.display.set_mode(self.size)

        pygame.time.set_timer(pygame.USEREVENT, 60)

        self.do_loop()

    def do_loop(self):
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif self.state == RUNNING and event.type == pygame.USEREVENT:
                    if self.snake.tick():
                        self.game_over()
                    if self.check_food_eaten(self.snake.parts[0].get_pos()):
                        self.set_food()
                        self.snake.add_part()
                elif event.type == pygame.KEYDOWN:
                    self.process_keys(event.key)

            self.screen.fill(background)
            self.snake.draw(self.screen)
            self.draw_food()
            if self.state == GAME_OVER:
                self.draw_game_over()
            elif self.state == PAUSED:
                self.draw_pause()
            pygame.display.flip()

    def game_over(self):
        self.state = GAME_OVER

    def process_keys(self, key):
        if self.state != GAME_OVER:
            if key == pygame.K_UP and self.snake.get_motion() != DOWN:
                self.snake.set_motion(UP)
            elif key == pygame.K_DOWN and self.snake.get_motion() != UP:
                self.snake.set_motion(DOWN)
            elif key == pygame.K_RIGHT and self.snake.get_motion() != LEFT:
                self.snake.set_motion(RIGHT)
            elif key == pygame.K_LEFT and self.snake.get_motion() != RIGHT:
                self.snake.set_motion(LEFT)
            elif key == pygame.K_SPACE:
                if self.state == RUNNING:
                    self.state = PAUSED
                elif self.state == PAUSED:
                    self.state = RUNNING
        else:
            if key == pygame.K_RETURN:
                self.snake = Snake()
                self.set_food()
                self.state = RUNNING

    def draw_pause(self):
        w, h = self.pause_size
        self.screen.blit(self.pause_surf, ((game_width * 4) / 2 - w / 2,
            ((game_height - 20) * 4) / 2 - h / 2, w, h))

    def draw_game_over(self):
        w, h = self.game_over_size
        self.screen.blit(self.game_over_surface, ((game_width * 4) / 2 - w / 2,
            ((game_height - 20) * 4) / 2 - h / 2, w, h))
        w, h = self.press_return_size
        self.screen.blit(self.press_return_surf, ((game_width * 4) / 2 - w / 2,
            (game_height * 4) / 2 - h / 2, w, h))

    def check_food_eaten(self, (x, y)):
        if self.food == (x, y):
            return True
        return False

    def check_valid_food(self, (x, y)):
        tmp_pos = []
        for part in self.snake.parts:
            tmp_pos.append(part.get_pos())
        if tmp_pos.count((x, y)):
            return False

        return True

    def draw_food(self):
        if self.food != (-1, -1):
            self.screen.fill(food_color, (self.food[0] * 4, self.food[1] * 4, 4, 4))

    def set_food(self):
        while True:
            x, y = random.randint(1, game_width - 1), random.randint(1, game_height - 1)
            if self.check_valid_food((x, y)):
                self.food = x, y
                break


if __name__ == '__main__':
    Game()
