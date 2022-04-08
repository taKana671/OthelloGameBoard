import copy
import pygame
from collections import namedtuple
from enum import Enum, auto
from pathlib import Path
from pygame.locals import *

import random

SCREEN = Rect(0, 0, 840, 700)


Point = namedtuple('Point', 'x y')
Candidate = namedtuple('Candidate', 'value row col')
Simulate = namedtuple('Simulate', 'corners arounds sides')
# Candidate = namedtuple('Candidate', 'evaluation row col corners arounds sides')

DARK_GREEN = (0, 70, 0)
GREEN = (0, 100, 0)
BROWN = (76, 38, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


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

    @property
    def color(self):
        return self.value


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


class Button(pygame.sprite.Sprite):

    def __init__(self, file_path, center):
        super().__init__(self.containers)
        self.image = pygame.image.load(file_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = center


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
        self.button = Button('images/button.png', Point(102, self.top + 510))
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

    def draw_button(self, screen):
        pygame.draw.rect(screen, WHITE, (40, self.top + 490, 125, 40))

    def draw(self, screen):
        self.draw_background(screen)
        self.draw_turn_display(screen)
        self.draw_score_display(screen)
        self.draw_button(screen)

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

    def has_placeables(self, disks, color):
        for r in range(Board.grid_num):
            for c in range(Board.grid_num):
                if self.is_placeable(r, c, disks, color):
                    return True
        return False

    # def has_placeables(self):
    #     for r in range(Board.grid_num):
    #         for c in range(Board.grid_num):
    #             if self.is_placeable(r, c, ):
    #                 return True
    #     return False

    def is_placeable(self, row, col, disks, color):
        if not disks[row][col]:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    if row + i < 0 or row + i >= Board.grid_num or \
                            col + j < 0 or col + j >= Board.grid_num:
                        continue
                    if not disks[row + i][col + j]:
                        continue
                    if disks[row + i][col + j].color == color:
                        continue
                    if self.reverse_check(disks, color, row + i, col + j, i, j, 0):
                        return True
        return False

    def reverse_check(self, disks, color, row, col, r, c, cnt=0):
        if 0 <= row < Board.grid_num and 0 <= col < Board.grid_num:
            if disk := disks[row][col]:
                if disk.color != color:
                    cnt += 1
                    return self.reverse_check(disks, color, row + r, col + c, r, c, cnt)
                else:
                    return cnt

    def get_reversibles(self, row, col, r, c, cnt):
        for i in range(cnt):
            target_row = row + r * i
            target_col = col + c * i

            yield (target_row, target_col)

    def find_reversibles(self, row, col, disks, color):
        for r in range(-1, 2):
            for c in range(-1, 2):
                if r == 0 and c == 0:
                    continue
                if row + r < 0 or row + r >= Board.grid_num or \
                        col + c < 0 or col + c >= Board.grid_num:
                    continue
                if not disks[row + r][col + c]:
                    continue
                if disks[row + r][col + c].color == color:
                    continue
                if cnt := self.reverse_check(disks, color, row + r, col + c, r, c):
                    yield from self.get_reversibles(row + r, col + c, r, c, cnt)

    def reverse(self, disks, color, pos):
        for row, col in self.find_reversibles(*pos, disks, color):
            self.board.reverse(row, col, color)


class Player(GameLogic):

    def __init__(self, board):
        self.board = board
        self.color = Piece.BLACK
        self.turn = True
        self.display_disk = Images.BLACK_DISPLAY

    def place(self, pos):
        row, col = self.board.find_position(*pos)
        if self.is_placeable(row, col, self.board.disks, self.color):
            self.board.place(row, col, self.color)
            return True


class OtherPlayer(GameLogic):

    def __init__(self, board):
        self.board = board
        self.color = Piece.WHITE
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
        self.around_corners = [
            [(0, 1), (1, 0), (1, 1)],
            [(0, 6), (1, 6), (1, 7)],
            [(6, 0), (6, 1), (7, 1)],
            [(6, 6), (6, 7), (7, 6)]
        ]
        self.corners = [(0, 0), (0, 7), (7, 0), (7, 7)]

        self.around_corners2 = [
            (0, 1), (1, 0), (1, 1),
            (0, 6), (1, 6), (1, 7),
            (6, 0), (6, 1), (7, 1),
            (6, 6), (6, 7), (7, 6)
        ]

    def get_placeables(self, disks, color):
        for r in range(self.board.grid_num):
            for c in range(self.board.grid_num):
                if not disks[r][c]:
                    if self.is_placeable(r, c, disks, color.value):
                        yield r, c

    def find_corners(self, grids):
        for pos in grids:
            if pos in self.corners:
                return pos

    def calc_weights(self, disks):
        black = white = 0
        for r in range(Board.grid_num):
            for c in range(Board.grid_num):
                if not disks[r][c]:
                    continue
                if disks[r][c] == Piece.BLACK:
                    black += self.weights[r][c]
                else:
                    white += self.weights[r][c]
        return black, white

    def find_candidates_with_weight(self, grids, disks, color):
        for r, c in grids:
            temp = copy.deepcopy(disks)
            temp[r][c] = Piece.WHITE
            for row, col in self.find_reversibles(r, c, disks, color.value):
                temp[row][col] = color
            black, white = self.calc_weights(temp)
            yield Candidate(white - black, r, c)

    def measure_openness(self, row, col, disks, *pos):
        total = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if row + i < 0 or row + i >= self.board.grid_num or \
                        col + j < 0 or col + j >= self.board.grid_num:
                    continue
                if (row + i, col + j) == pos:
                    continue
                if not disks[row + i][col + j]:
                    total += 1
        return total

    def find_candidates_with_openness(self, grids, disks):
        grids = [pos for pos in grids if pos not in self.corner_grids]

        for r, c in grids:
            total = 0
            for row, col in self.find_reversibles(r, c):
                total += self.measure_openness(row, col, disks, r, c)
            if total == 0:
                yield Candidate(total, r, c)

    def _corners(self, disks):
        corner_black = corner_white = 0

        for r, c in self.corners:
            if not disks[r][c]:
                continue
            if disks[r][c] == self.color:
                corner_white += 1
            else:
                corner_black += 1

        return corner_black, corner_white

    def _non_corners(self, disks):
        not_corner_black = not_corner_white = 0

        for r in range(Board.grid_num):
            for c in range(Board.grid_num):
                if (r, c) in self.corners:
                    continue
                if not disks[r][c]:
                    continue
                if disks[r][c] == self.color:
                    not_corner_white += 1
                else:
                    not_corner_black += 1
        return not_corner_black, not_corner_white

    def _around_corners(self, disks):
        around_black = around_white = 0

        for (row, col), around_corners in zip(self.corners, self.around_corners):
            if not disks[row][col]:
                for r, c in around_corners:
                    if not disks[r][c]:
                        continue
                    if disks[r][c] == self.color:
                        around_white += 1
                    else:
                        around_black += 1

        return around_black, around_white

    def copy_current_board(self):
        disks = [[None for _ in range(self.board.grid_num)] for _ in range(self.board.grid_num)]

        for r in range(self.board.grid_num):
            for c in range(self.board.grid_num):
                if disk := self.board.disks[r][c]:
                    disks[r][c] = disk.color
        return disks

    def simulate(self, disks, color):
        """四隅：空だったところに白がおかれないようにする。
           四隅の回り：白がおかれるようにする。
           周囲: 白がおかれないようにする。
        """
        # print(disks)
        empty_corners = [(r, c) for r, c in self.corners if not disks[r][c]]
        empty_around = [(r, c) for r, c in self.around_corners2 if not disks[r][c]]
        empty_sides = [(r, c) for r in range(self.board.grid_num) for c in range(self.board.grid_num) \
                       if (r in (0, 7) or c in (0, 7)) and not disks[r][c]]
        corners = arounds = sides = 0

        grids = tuple(pos for pos in self.get_placeables(disks, color))
        for r, c in grids:

            temp = copy.deepcopy(disks)
            temp[r][c] = color
            for row, col in self.find_reversibles(r, c, temp, color.value):
                temp[row][col] = color

            corners += sum(1 for r, c in empty_corners if temp[r][c] == color)
            arounds += sum(1 for r, c in empty_around if temp[r][c] == color)
            sides += sum(1 for r, c in empty_sides if temp[r][c] == color)
        return Simulate(corners, arounds, sides)

    def evaluate(self, disks):
        corner_black, corner_white = self._corners(disks)
        not_corner_black, not_corner_white = self._non_corners(disks)
        around_black, around_white = self._around_corners(disks)
        evaluation = (corner_white - corner_black) - (not_corner_white - not_corner_black) \
            + 21 * (corner_white - corner_black) - 10 * (corner_white - around_black)

        return evaluation

    def find_best_move(self, grids, disks, color):
        for r, c in grids:
            temp = copy.deepcopy(disks)
            temp[r][c] = color
            for row, col in self.find_reversibles(r, c, temp, color.value):
                temp[row][col] = color
            evaluation = self.evaluate(temp)
            simulation = self.simulate(temp, Piece.BLACK)
            # print(simulation)
            yield (Candidate(evaluation, r, c), simulation)

    def count_disks(self):
        return sum(1 for grids in self.board.disks for grid in grids if not grid)

    def guess(self, grids, disks):
        candidates = [candidate for candidate in self.find_best_move(grids, disks, self.color)]

        if filtered := [cand for cand, simu in candidates if simu.corners == 0 and simu.arounds > 0 and simu.sides == 0]:
            return max(filtered, key=lambda x: x.value)
        if filtered := [cand for cand, simu in candidates if simu.corners == 0 and simu.sides == 0]:
            return max(filtered, key=lambda x: x.value)
        if filtered := [cand for cand, simu in candidates if simu.corners == 0]:
            return max(filtered, key=lambda x: x.value)
        if filtered := [cand for cand, simu in candidates if simu.sides == 0]:
            return max(filtered, key=lambda x: x.value)
        if filtered := [cand for cand, simu in candidates if simu.arounds > 0]:
            return max(filtered, key=lambda x: x.value)
        
        candidates = [cand for cand, _ in candidates]
        return max(candidates, key=lambda x: x.value)

    def place(self):
        disks = self.copy_current_board()
        placeable_grids = tuple(pos for pos in self.get_placeables(disks, self.color))
        print(placeable_grids)

        if pos := self.find_corners(placeable_grids):
            self.board.place(*pos, self.color)
        else:
            if filtered := [pos for pos in placeable_grids if pos not in self.around_corners]:
                pos = self.guess(filtered, disks)
            else:
                pos = self.guess(placeable_grids, disks)
            
            self.board.place(pos.row, pos.col, self.color)


            # candidates = [cand for cand in self.find_best_move(grids, disks, self.color)]
            # print(candidates)

            # if filtered := [cand for cand in candidates if (cand.row, cand.col) not in self.around_corners]:
            #     pos = max(filtered, key=lambda x: x.value)
            # else:
            #     pos = max(candidates, key=lambda x: x.value)
            # self.board.place(pos.row, pos.col, self.color)

        # elif candidates := [cand for cand in self.find_candidates_with_openness(grids)]:
        #     pos = min(candidates, key=lambda x: x.value)
        #     print('openness', pos)
        #     self.board.place(pos.row, pos.col, self.color)
        # elif candidates := [cand for cand in self.find_candidates_with_weight(grids)]:
        #     if filtered := [cand for cand in candidates if (cand.row, cand.col) not in self.corner_grids]:
        #         pos = max(filtered, key=lambda x: x.value)
        #     else:
        #         pos = max(candidates, key=lambda x: x.value)
        #     self.board.place(pos.row, pos.col, self.c olor)


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
        Button.containers = self.disk_group
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

    def delete_disks(self):
        for r in range(Board.grid_num):
            for c in range(Board.grid_num):
                if disk := self.disks[r][c]:
                    self.disks[r][c] = disk.kill()

    def restart_game(self):
        self.timer = 0
        self.event = None
        self.delete_disks()
        self.setup()
        self.board.black_score = self.board.white_score = ''
        self.board.set_turn(self.player.display_disk)

    def set_timer(self, event_type, t=40):
        """Using pygame.set_timer resulted in program crash, but no errors
           were raised.
        """
        self.status = Status.SET_TIMER
        self.event = pygame.event.Event(event_type)
        self.timer = t

    def click(self, click_pos):
        if self.board.button.rect.collidepoint(*click_pos):
            self.restart_game()
        else:
            if self.player.turn and self.cursor.visible:
                if self.player.has_placeables(self.disks, self.player.color):
                    if self.player.place(Point(*click_pos)):
                        self.set_timer(self._reverse)

    def place_disk(self):
        self.other.place()
        self.set_timer(self._reverse)

    def reverse_disks(self):
        current_player = self.player if self.player.turn else self.other
        current_player.reverse(self.disks, current_player.color, self.board.clicked)
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
        if not current_player.has_placeables(self.disks, current_player.color):
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