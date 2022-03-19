import pygame
import sys
from collections import namedtuple
from enum import Enum, auto
from pathlib import Path
from pygame.locals import *


Point = namedtuple('Point', 'x y')


class Disks(Enum):

    BLACK = 1
    WHITE = 2

    @property
    def file_path(self):
        return Path('images', self.name.lower())


class Board:

    def __init__(self):
        self.grid_size = 70
        self.rows = 8
        self.cols = 8
        self.left = 70
        self.top = 120
        self.right = self.left + self.rows * self.grid_size
        self.bottom = self.top + self.rows * self.grid_size

    def draw(self, screen):
        x, y = self.left, self.top

        for i in range(self.rows + 1):
            pygame.draw.line(screen, (0, 0, 0), (self.left, y), (self.right, y), 2)
            pygame.draw.line(screen, (0, 0, 0), (x, self.top), (x, self.bottom), 2)
            x += self.grid_size
            y += self.grid_size

    def find_position(self, x, y):
        row = (y - self.top) // self.grid_size
        col = (x - self.left) // self.grid_size
        return row, col

    def grid_center(self, row, col):
        center_y = self.top + self.grid_size * row + self.grid_size // 2
        center_x = self.left + self.grid_size * col + self.grid_size // 2
        return Point(center_x, center_y)


class Othello:

    def __init__(self, screen, board, cursor):
        self.screen = screen
        self.board = board
        self.cursor = cursor
        self.disks = [[None for _ in range(self.board.cols)] for _ in range(self.board.rows)]

    def Setup(self):
        pass

    def update(self):
        self.board.draw(self.screen)

    def place(self, pos):
        if self.cursor.visible:
            row, col = self.board.find_position(*pos)
            print(row, col)


class Disk(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__(self.containers)
        self.image = pygame.image.load('igo_black.png').convert_alpha()
        # self.image = pygame.transform.scale(self.image, (100, 70))
        self.image = pygame.transform.scale(self.image, (99, 90))
        self.rect = self.image.get_rect()
        self.rect.centerx = 385
        self.rect.centery = 365


class Cursor(pygame.sprite.Sprite):

    def __init__(self, board):
        super().__init__(self.containers)
        self.image = pygame.image.load('images/cursor.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.visible = False
        self.board = board

    def calc_distance(self, pt1, pt2):
        return ((pt2.x - pt1.x) ** 2 + (pt2.y - pt1.y) ** 2) ** 0.5

    def move(self, cursor_pos):
        if self.board.left <= cursor_pos.x <= self.board.right and \
                self.board.top <= cursor_pos.y <= self.board.bottom:
            row, col = self.board.find_position(*cursor_pos)
            grid_center = self.board.grid_center(row, col)
            if self.calc_distance(cursor_pos, grid_center) <= 30:
                self.visible = True
                pygame.mouse.set_visible(False)
                self.rect.centerx = cursor_pos.x + 3
                self.rect.top = cursor_pos.y
                return
        self.visible = False
        pygame.mouse.set_visible(True)


def main():
    pygame.init
    screen = pygame.display.set_mode((700, 800))
    pygame.display.set_caption('Othello game board')
    stones = pygame.sprite.RenderUpdates()
    cursor = pygame.sprite.RenderUpdates()
    Disk.containers = stones
    Cursor.containers = cursor

    clock = pygame.time.Clock()
    board = Board()
    finger = Cursor(board)
    othello = Othello(screen, board, finger)

    while True:
        clock.tick(60)
        screen.fill((0, 100, 0))
        othello.update()
        stones.update()
        stones.draw(screen)

        if finger.visible:
            cursor.update()
            cursor.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEMOTION:
                x, y = event.pos
                finger.move(Point(*event.pos))

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if finger.visible:
                    othello.place(Point(*event.pos))

        pygame.display.update()


if __name__ == '__main__':
    main()
