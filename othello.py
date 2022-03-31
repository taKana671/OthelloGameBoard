import pygame
from collections import namedtuple
from enum import Enum, auto
from pathlib import Path
from pygame.locals import *

import random

SCREEN = Rect(0, 0, 840, 700)


Point = namedtuple('Point', 'x y')
Candidate = namedtuple('Candidate', 'diff row col')

DARK_GREEN = (0, 70, 0)
GREEN = (0, 100, 0)
BROWN = (76, 38, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)


class Status(Enum):
    PLAY = auto()
    GAMEOVER = auto()
    SET_TIMER = auto()


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

    grid_num = 8

    def __init__(self, disks, display_group):
        self.grid_size = 70
        self.left = 220
        self.top = 70
        self.side = self.grid_num * self.grid_size
        self.right = self.left + self.side
        self.bottom = self.top + self.side
        self.show_pass = False
        self.disks = disks
        self.display_group = display_group
        self.set_displays()
        self.black_score = self.white_score = ''

    def set_displays(self):
        _ = Disk(Piece.BLACK, Point(80, 390))
        _ = Disk(Piece.WHITE, Point(80, 455))
        title_font = pygame.font.SysFont(None, 50)
        self.text_turn = title_font.render('TURN', True, BLACK)
        self.text_score = title_font.render('SCORE', True, BLACK)
        text_font = pygame.font.SysFont(None, 30)
        self.text_pass = text_font.render('PASS', True, RED)
        self.score_font = pygame.font.SysFont(None, 40)

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
        screen.blit(self.text_turn, (35, self.top + 10))
        if self.show_pass:
            screen.blit(self.text_pass, (130, 180))

    def set_turn(self, disk):
        disk = DisplayDisk(disk.filepath)
        self.display_group.add(disk)

    def draw_score_display(self, screen):
        pygame.draw.rect(screen, GREEN, (40, self.top + 280, 80, 150))
        screen.blit(self.text_score, (25, self.top + 220))
        black_score = self.score_font.render(self.black_score, True, BLACK)
        white_score = self.score_font.render(self.white_score, True, BLACK)
        screen.blit(black_score, Point(140, 380))
        screen.blit(white_score, Point(140, 445))

    def draw(self, screen):
        self.draw_background(screen)
        self.draw_turn_display(screen)
        self.draw_score_display(screen)

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
        self.clicked = (row, col)
        self.disks[row][col] = Disk(color, self.grid_center(row, col))

    def reverse(self, row, col, color):
        disk = self.disks[row][col]
        self.disks[row][col] = disk.kill()
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

    def __init__(self, board, color):
        self.board = board
        self.color = color

    def has_placeables(self):
        for r in range(self.board.grid_num):
            for c in range(self.board.grid_num):
                if self.is_placeable(r, c):
                    return True
        return False

    def is_placeable(self, row, col):
        if not self.board.disks[row][col]:
            for r in range(-1, 2):
                for c in range(-1, 2):
                    if r == 0 and c == 0:
                        continue
                    if row + r < 0 or row + r >= self.board.grid_num or \
                            col + c < 0 or col + c >= self.board.grid_num:
                        continue
                    if not self.board.disks[row + r][col + c]:
                        continue
                    if self.board.disks[row + r][col + c].color == self.color:
                        continue
                    if self.reverse_check(row + r, col + c, r, c, 0):
                        return True
        return False

    def reverse_check(self, row, col, r, c, cnt=0):
        if 0 <= row < self.board.grid_num and 0 <= col < self.board.grid_num:
            if disk := self.board.disks[row][col]:
                if disk.color != self.color:
                    cnt += 1
                    return self.reverse_check(row + r, col + c, r, c, cnt)
                else:
                    return cnt

    def get_reversibles(self, row, col, r, c, cnt):
        for i in range(cnt):
            target_row = row + r * i
            target_col = col + c * i

            yield (target_row, target_col)

    def find_reversibles(self, row, col):
        for r in range(-1, 2):
            for c in range(-1, 2):
                if r == 0 and c == 0:
                    continue
                if row + r < 0 or row + r >= self.board.grid_num or \
                        col + c < 0 or col + c >= self.board.grid_num:
                    continue
                if not self.board.disks[row + r][col + c]:
                    continue
                if self.board.disks[row + r][col + c] == self.color:
                    continue
                if cnt := self.reverse_check(row + r, col + c, r, c):
                    yield from self.get_reversibles(row + r, col + c, r, c, cnt)

    def reverse(self):
        for row, col in self.find_reversibles(*self.board.clicked):
            self.board.reverse(row, col, self.color)


class Player(GameLogic):

    def __init__(self, board):
        super().__init__(board, Piece.BLACK)
        self.turn = True
        self.display_disk = Images.BLACK_DISPLAY

    def place(self, pos):
        row, col = self.board.find_position(*pos)
        if self.is_placeable(row, col):
            self.board.place(row, col, self.color)
            return True


class OtherPlayer(GameLogic):

    def __init__(self, board):
        super().__init__(board, Piece.WHITE)
        self.turn = False
        self.display_disk = Images.WHITE_DISPLAY
        self.weights = [
            [30, -12, 0, -1, -1, 0, -12, 30],
            [-12, -15, -3, -3, -3, -3, -15, -12],
            [0, -3, 0, -1, -1, 0, -3, 0],
            [-1, -3, -1, -1, -1, -1, -3, -1],
            [-1, -3, -1, -1, -1, -1, -3, -1],
            [0, -3, 0, -1, -1, 0, -3, 0],
            [-12, -15, -3, -3, -3, -3, -15, -12],
            [30, -12, 0, -1, -1, 0, -12, 30]
        ]

    def get_placeables(self):
        for r in range(self.board.grid_num):
            for c in range(self.board.grid_num):
                if not self.board.disks[r][c]:
                    if self.is_placeable(r, c):
                        yield r, c

    def find_corners(self, grids):
        for r in [0, 7]:
            for c in [0, 7]:
                if (r, c) in grids:
                    return (r, c)

    def calc_weights(self):
        black = white = 0
        for r in range(self.board.grid_num):
            for c in range(self.board.grid_num):
                if disk := self.board.disks[r][c]:
                    if disk.color == Piece.BLACK:
                        black += self.weights[r][c]
                    else:
                        white += self.weights[r][c]
        return black, white

    def find_candidates(self, grids):
        b, w = self.calc_weights()

        for r, c in grids:
            # print(r, c)
            black = b
            white = w + self.weights[r][c]
            for row, col in self.find_reversibles(r, c):
                weight = self.weights[row][col]
                black -= weight
                white += weight
            # print(black, white)
            yield Candidate(white - black, r, c)

    def place(self):
        grids = tuple(pos for pos in self.get_placeables())
        candidate = max(
            (cand for cand in self.find_candidates(grids)),
            key=lambda x: x.diff
        )
        self.board.place(candidate.row, candidate.col, self.color)


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
        self.timer = 0
        self.event = None
        self.status = Status.PLAY
        self.disks = [[None for _ in range(Board.grid_num)] for _ in range(Board.grid_num)]
        self.board = Board(self.disks, self.display_group)
        self.cursor = Cursor(self.board)
        self.player = Player(self.board)
        self.other = OtherPlayer(self.board)
        self.create_events()
        self.setup()

    def create_events(self):
        self._place = pygame.USEREVENT + 0
        self._reverse = pygame.USEREVENT + 1
        self._change = pygame.USEREVENT + 2
        self._guess = pygame.USEREVENT + 3
        self._pass = pygame.USEREVENT + 4

    def setup(self):
        for r in range(3, 5):
            for c in range(3, 5):
                if r == c:
                    color = Piece.WHITE
                else:
                    color = Piece.BLACK
                self.board.place(r, c, color)

    def calc_score(self):
        black_score = sum(sum(
            disk.color == Piece.BLACK for disk in row if disk) for row in self.disks)
        white_score = sum(sum(
            disk.color == Piece.WHITE for disk in row if disk) for row in self.disks)
        self.board.white_score = str(white_score)
        self.board.black_score = str(black_score)
        if black_score + white_score == 64:
            return False
        return True

    def set_timer(self, event_type, t=40):
        """Using pygame.set_timer resulted in program crash, but no errors
           were raised.
        """
        self.status = Status.SET_TIMER
        self.event = pygame.event.Event(event_type)
        self.timer = t

    def click(self, click_pos):
        if self.player.turn and self.cursor.visible:
            if self.player.has_placeables():
                if self.player.place(Point(*click_pos)):
                    self.set_timer(self._reverse)

    def place_disk(self):
        self.other.place()
        self.set_timer(self._reverse)

    def reverse_disks(self):
        current_player = self.player if self.player.turn else self.other
        current_player.reverse()
        if self.calc_score():
            self.set_timer(self._change)
        else:
            self.satus = Status.GAMEOVER

    def pass_turn(self):
        self.board.show_pass = False
        pygame.event.post(pygame.event.Event(self._change))
        self.set_timer(self._change)

    def change_players(self):
        self.player.turn = not self.player.turn
        self.other.turn = not self.other.turn
        next_player = self.player if self.player.turn else self.other
        self.board.set_turn(next_player.display_disk)
        self.set_timer(self._guess)

    def guess_placeable(self):
        current_player = self.player if self.player.turn else self.other
        if not current_player.has_placeables():
            self.board.show_pass = True
            self.set_timer(self._pass)
        else:
            if self.other.turn:
                self.set_timer(self._place)

    def run(self):
        clock = pygame.time.Clock()
        self.board.set_turn(self.player.display_disk)
        running = True

        while running:
            if self.status == Status.SET_TIMER:
                self.timer -= 1
                if self.timer == 0:
                    self.status = Status.PLAY
                    pygame.event.post(self.event)

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
                if self.status == Status.PLAY:
                    if event.type == self._reverse:
                        self.reverse_disks()
                    if event.type == self._place:
                        self.place_disk()
                    if event.type == self._change:
                        self.change_players()
                    if event.type == self._guess:
                        self.guess_placeable()
                    if event.type == self._pass:
                        self.pass_turn()
                    # if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if event.type == MOUSEBUTTONUP and event.button == 1:
                        self.click(event.pos)

            pygame.display.update()


if __name__ == '__main__':
    game = Othello()
    game.run()