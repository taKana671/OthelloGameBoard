import pygame
from collections import namedtuple
from enum import Enum, auto
from pathlib import Path
from pygame.locals import *


SCREEN = Rect(0, 0, 700, 800)


Point = namedtuple('Point', 'x y')


class Piece(Enum):

    BLACK = 0
    WHITE = 1

    @property
    def filepath(self):
        return Path('images', f'{self.name.lower()}.png')


class Disk(pygame.sprite.Sprite):

    def __init__(self, disk, center):
        super().__init__(self.containers)
        self.image = pygame.image.load(disk.filepath).convert_alpha()
        self.image = pygame.transform.scale(self.image, (99, 90))
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = center
        self.color = disk


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


class BaseLogic:

    def __init__(self, disks, color):
        self.disks = disks
        self.color = color

    def check_top(self, row, col, r):
        if r > 0:
            if self.disks[r][col] and self.disks[r][col].color != self.color:
                return self.check_top(row, col, r - 1)
            else:
                if row - r > 1:
                    return r

    # def check_top(self, row, col, color):
    #     if row - 1 > 0:
    #         for r in range(row - 1, 0, -1):
    #             if disk := self.disks[r][col]:
    #                 if disk.color != color:
    #                     continue
    #                 if r < row - 1:
    #                     return r
    #                 break
    #             break
    #     return None


class Player(BaseLogic):

    def __init__(self, disks, board, cursor):
        super().__init__(disks, Piece.BLACK)
        self.board = board
        self.cursor = cursor

    def place(self, pos):
        if self.cursor.visible:
            row, col = self.board.find_position(*pos)
            print(row, col)
            print(self.check_top(row, col, row - 1))
            # print(self.disks[3][3].disk)


class Opponent(BaseLogic):
    pass


class Othello:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN.size)
        pygame.display.set_caption('Othello game board')
        self.disk_group = pygame.sprite.RenderUpdates()
        self.cursor_group = pygame.sprite.RenderUpdates()
        Disk.containers = self.disk_group
        Cursor.containers = self.cursor_group
        self.board = Board()
        self.cursor = Cursor(self.board)
        self.disks = [[None for _ in range(self.board.cols)] for _ in range(self.board.rows)]
        self.player = Player(self.disks, self.board, self.cursor)
        self.setup()

    def setup(self):
        for r in range(3, 5):
            for c in range(3, 5):
                if r == c:
                    disk = Disk(Piece.WHITE, self.board.grid_center(r, c))
                else:
                    disk = Disk(Piece.BLACK, self.board.grid_center(r, c))
                self.disks[r][c] = disk

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(60)
            self.screen.fill((0, 100, 0))
            self.board.draw(self.screen)
            self.disk_group.update()
            self.disk_group.draw(self.screen)

            if self.cursor.visible:
                self.cursor_group.update()
                self.cursor_group.draw(self.screen)

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == MOUSEMOTION:
                    x, y = event.pos
                    self.cursor.move(Point(*event.pos))
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if self.cursor.visible:
                        self.player.place(Point(*event.pos))

            pygame.display.update()


if __name__ == '__main__':
    game = Othello()
    game.run()
