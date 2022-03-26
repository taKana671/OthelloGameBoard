import pygame
from collections import namedtuple
from enum import Enum, auto
from pathlib import Path
from pygame.locals import *


SCREEN = Rect(0, 0, 840, 700)


Point = namedtuple('Point', 'x y')
Clicked = namedtuple('Clicked', 'row col')

DARK_GREEN = (0, 70, 0)
GREEN = (0, 100, 0)
BROWN = (76, 38, 0)


class Status(Enum):
    pass


class Files(Enum):

    @property
    def filepath(self):
        return Path('images', f'{self.name.lower()}.png')


class Piece(Files):

    BLACK = 0
    WHITE = 1


class Images(Files):

    BLACK_DISPLAY = auto()
    WHITE_DISPLAY = auto()
    CURSOR = auto()


class Disk(pygame.sprite.Sprite):

    def __init__(self, disk, center):
        super().__init__(self.containers)
        self.image = pygame.image.load(disk.filepath).convert_alpha()
        self.image = pygame.transform.scale(self.image, (99, 90))
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = center
        self.color = disk


class DisplayDisk(pygame.sprite.Sprite):

    def __init__(self, file_path):
        super().__init__(self.containers)
        self.image = pygame.image.load(file_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (150, 105))
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = Point(80, 180)


class Board:

    def __init__(self, display_group):
        self.grid_size = 70
        self.grid_num = 8
        self.left = 220
        self.top = 70
        self.side = self.grid_num * self.grid_size
        self.right = self.left + self.side
        self.bottom = self.top + self.side
        self.clicked = None
        self.disks = {}
        self.display_group = display_group
        self.title_font = pygame.font.SysFont(None, 50)

    def draw_background(self, screen):
        pygame.draw.rect(
            screen,
            BROWN,
            (self.left - 20, self.top - 20, self.side + 40, self.side + 40)
        )
        pygame.draw.rect(
            screen,
            GREEN,
            (self.left, self.top, self.side, self.side)
        )

    def draw_turn_display(self, screen):
        pygame.draw.rect(screen, GREEN, (40, self.top + 70, 80, 100))
        pygame.draw.ellipse(screen, DARK_GREEN, Rect(50, 220, 60, 10), width=0)
        text = self.title_font.render('TURN', True, (0, 0, 0))
        screen.blit(text, (40, self.top))

    def set_turn_display(self, disk):
        disk = DisplayDisk(disk.filepath)
        self.display_group.add(disk)

    def draw(self, screen):
        self.draw_background(screen)
        self.draw_turn_display(screen)

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

    def reverse(self):
        row, col = self.board.clicked
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

    def place_disk(self, row, col):
        self.disks[row][col] = self.color
        self.board.place(row, col, self.color)


class Player(GameLogic):

    def __init__(self, disks, board):
        super().__init__(disks, board, Piece.BLACK)
        self.turn = True
        self.display_disk = Images.BLACK_DISPLAY

    def has_placeables(self):
        for r in range(self.board.grid_num):
            for c in range(self.board.grid_num):
                if not self.disks[r][c]:
                    if self.is_placeable(r, c):
                        return True

    def place(self, pos):
        row, col = self.board.find_position(*pos)
        if self.is_placeable(row, col):
            self.board.clicked = Clicked(row, col)
            self.place_disk(row, col)
            return True


class Opponent(GameLogic):

    def __init__(self, disks, board):
        super().__init__(disks, board, Piece.WHITE)
        self.turn = False
        self.display_disk = Images.WHITE_DISPLAY

    def get_placeables(self):
        for r in range(self.board.grid_num):
            for c in range(self.board.grid_num):
                if not self.disks[r][c]:
                    if self.is_placeable(r, c):
                        yield r, c

    def find_corners(self, grids):
        for r in [0, 7]:
            for c in [0, 7]:
                if (r, c) in grids:
                    return (r, c)

    def place(self):
        grids = tuple(pos for pos in self.get_placeables())
        if corner := self.find_corners(grids):
            self.board.clicked = Clicked(*corner)
            self.place_disk(*corner)
        else:
            self.board.clicked = Clicked(*grids[0])
            self.place_disk(*grids[0])
        # return True


class Othello:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN.size)
        pygame.display.set_caption('Othello game board')
        self.disk_group = pygame.sprite.RenderUpdates()
        self.cursor_group = pygame.sprite.RenderUpdates()
        self.display_group = pygame.sprite.GroupSingle()
        Disk.containers = self.disk_group
        Cursor.containers = self.cursor_group
        DisplayDisk.containers = self.display_group
        self.status = None
        self.board = Board(self.display_group)
        self.cursor = Cursor(self.board)
        self.disks = [[None for _ in range(self.board.grid_num)] for _ in range(self.board.grid_num)]
        self.player = Player(self.disks, self.board)
        self.opponent = Opponent(self.disks, self.board)
        self.setup()

    def setup(self):
        for r in range(3, 5):
            for c in range(3, 5):
                if r == c:
                    color = Piece.WHITE
                else:
                    color = Piece.BLACK
                self.disks[r][c] = color
                self.board.place(r, c, color)

    def change_order(self):
        self.player.turn = not self.player.turn
        self.opponent.turn = not self.opponent.turn
        next_player = self.player if self.player.turn else self.opponent
        self.board.set_turn_display(next_player.display_disk)

    def run(self):
        clock = pygame.time.Clock()
        place_disk = pygame.USEREVENT + 1
        reverse_disks = pygame.USEREVENT + 2
        pass_turn = pygame.USEREVENT + 3

        self.board.set_turn_display(self.player.display_disk)
        running = True

        while running:
            clock.tick(60)
            self.screen.fill((221, 221, 221))   #(0,70, 0))
            self.board.draw(self.screen)
            self.disk_group.update()
            self.disk_group.draw(self.screen)
            self.display_group.update()
            self.display_group.draw(self.screen)

            if self.cursor.visible:
                self.cursor_group.update()
                self.cursor_group.draw(self.screen)

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == MOUSEMOTION:
                    x, y = event.pos
                    self.cursor.move(Point(*event.pos))

                if event.type == reverse_disks:
                    pygame.time.set_timer(reverse_disks, 0)
                    if self.player.turn:
                        self.player.reverse()
                        pygame.time.set_timer(place_disk, 2000)
                    else:
                        self.opponent.reverse()
                    self.change_order()
                if event.type == place_disk:
                    pygame.time.set_timer(place_disk, 0)
                    self.opponent.place()
                    pygame.time.set_timer(reverse_disks, 2000)

                # if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if event.type == MOUSEBUTTONUP and event.button == 1:
                    if self.player.turn and self.cursor.visible:
                        if self.player.has_placeables():
                            if self.player.place(Point(*event.pos)):
                                pygame.time.set_timer(reverse_disks, 2000)
                        else:
                            pass
                            # pygame.time.set_timer(event, millis)

            pygame.display.update()


if __name__ == '__main__':
    game = Othello()
    game.run()