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
        self.grid_num = 8
        self.left = 70
        self.top = 120
        self.right = self.left + self.grid_num * self.grid_size
        self.bottom = self.top + self.grid_num * self.grid_size
        self.disks = {}

    def draw(self, screen):
        x, y = self.left, self.top

        for i in range(self.grid_num + 1):
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

    def place(self, row, col, color):
        self.disks[(row, col)] = Disk(color, self.grid_center(row, col))

    def reverse(self, row, col, color):
        self.disks[(row, col)].kill()
        self.place(row, col, color)


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


class GameLogic:

    def __init__(self, disks, board, color):
        self.disks = disks
        self.board = board
        self.color = color

    def is_placeable(self, row, col):
        if not self.disks[row][col]:
            for r in range(-1, 2):
                for c in range(-1, 2):
                    if r == 0 and c == 0:
                        continue
                    if row + r < 0 or row + r >= self.board.grid_num or \
                            col + c < 0 or col + c >= self.board.grid_num:
                        continue
                    if not self.disks[row + r][col + c]:
                        continue
                    if self.disks[row + r][col + c] == self.color:
                        continue
                    if self.reverse_check(row + r, col + c, r, c, 0):
                        return True
        return False

    def reverse_check(self, row, col, r, c, cnt=0):
        if 0 <= row < self.board.grid_num and 0 <= col < self.board.grid_num:
            if color := self.disks[row][col]:
                if color != self.color:
                    cnt += 1
                    return self.reverse_check(row + r, col + c, r, c, cnt)
                else:
                    return cnt

    def _reverse(self, row, col, r, c, cnt):
        for i in range(cnt):
            target_row = row + r * i
            target_col = col + c * i
            self.disks[target_row][target_col] = self.color
            self.board.reverse(target_row, target_col, self.color)

    def reverse(self, row, col):
        for r in range(-1, 2):
            for c in range(-1, 2):
                if r == 0 and c == 0:
                    continue
                if row + r < 0 or row + r >= self.board.grid_num or \
                        col + c < 0 or col + c >= self.board.grid_num:
                    continue
                if not self.disks[row + r][col + c]:
                    continue
                if self.disks[row + r][col + c] == self.color:
                    continue
                if cnt := self.reverse_check(row + r, col + c, r, c):
                    self._reverse(row + r, col + c, r, c, cnt)

    def place(self, row, col):
        self.disks[row][col] = self.color
        self.board.place(row, col, self.color)
        self.reverse(row, col)


class Player(GameLogic):

    def __init__(self, disks, board, cursor):
        super().__init__(disks, board, Piece.BLACK)
        self.cursor = cursor

    def click(self, pos):
        if self.cursor.visible:
            row, col = self.board.find_position(*pos)
            if self.is_placeable(row, col):
                print(f'click: row: {row}, col{col}')
                self.place(row, col)


class Opponent(GameLogic):
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
        self.disks = [[None for _ in range(self.board.grid_num)] for _ in range(self.board.grid_num)]
        self.player = Player(self.disks, self.board, self.cursor)
        self.setup()

    def setup(self):
        for r in range(3, 5):
            for c in range(3, 5):
                if r == c:
                    color = Piece.WHITE
                else:
                    color = Piece.BLACK
                self.disks[r][c] = color
                disk = Disk(color, self.board.grid_center(r, c))
                self.board.disks[(r, c)] = disk

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
                        self.player.click(Point(*event.pos))

            pygame.display.update()


if __name__ == '__main__':
    game = Othello()
    game.run()
