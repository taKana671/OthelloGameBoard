import pygame
import random
import sys
from collections import namedtuple
from enum import Enum, auto
from pathlib import Path
from pygame.locals import *


SCREEN = Rect(0, 0, 840, 700)

DARK_GREEN = (0, 70, 0)
GREEN = (0, 100, 0)
BROWN = (76, 38, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (221, 221, 221)


Point = namedtuple('Point', 'x y')
Candidate = namedtuple('Candidate', 'evaluation row col corners arounds sides')


class Status(Enum):

    PLAY = auto()
    SET_TIMER = auto()
    DRAW = auto()
    PASS = auto()
    WIN = auto()
    GAMEOVER = auto()


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

    @classmethod
    def opposite(cls, piece):
        for member in cls.__members__.values():
            if member.value != piece.value:
                return member


class Images(Files):

    BLACK_DISPLAY = 0
    WHITE_DISPLAY = 1
    CURSOR = 2
    BUTTON = 3

    @classmethod
    def get_image(cls, piece):
        for member in cls.__members__.values():
            if member.value == piece.value:
                return member


class Sounds(Files):

    DISK = auto()

    @property
    def filepath(self):
        return Path('sounds', f'{self.name.lower()}.wav')


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
        self.rect.centerx, self.rect.centery = 80, 180


class Button(pygame.sprite.Sprite):

    def __init__(self, file_path, center, game):
        super().__init__(self.containers)
        self.image = pygame.image.load(file_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = center
        self.left = self.rect.left
        self.right = self.rect.left + self.rect.width
        self.top = self.rect.top
        self.bottom = self.rect.top + self.rect.height
        self.game = game

    def click(self):
        if self.game.status == Status.GAMEOVER:
            self.game.change_first_player()
            self.game.board.player_color = self.game.player.color
        self.game.board.clear()
        self.game.start()


class Board:

    grid_num = 8

    def __init__(self, game, display_group):
        self.grid_size = 70
        self.left = 220
        self.top = 70
        self.side = self.grid_num * self.grid_size
        self.right = self.left + self.side
        self.bottom = self.top + self.side
        self.disks = game.disks
        self.display_group = display_group
        self.set_displays(game)
        self.player_color = None

    def setup(self):
        for r in range(3, 5):
            for c in range(3, 5):
                if r == c:
                    color = Piece.WHITE
                else:
                    color = Piece.BLACK
                self.place(r, c, color)

        self.black_score = self.white_score = ''
        self.status = Status.PLAY

    def clear(self):
        for r in range(self.grid_num):
            for c in range(self.grid_num):
                if disk := self.disks[r][c]:
                    self.disks[r][c] = disk.kill()

    def set_displays(self, game):
        _ = Disk(Piece.BLACK, (80, 390))
        _ = Disk(Piece.WHITE, (80, 455))
        self.button = Button(Images.BUTTON.filepath, (102, self.top + 510), game)
        title_font = pygame.font.SysFont(None, 50)
        self.text_turn = title_font.render('TURN', True, BLACK)
        self.text_score = title_font.render('SCORE', True, BLACK)
        text_font = pygame.font.SysFont(None, 30)
        self.text_pass = text_font.render('PASS', True, RED)
        self.text_win = text_font.render('WIN', True, RED)
        self.text_draw = text_font.render('DRAW', True, RED)
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
        if self.status == Status.PASS:
            screen.blit(self.text_pass, (130, 180))
        if self.status == Status.WIN:
            screen.blit(self.text_win, (130, 180))
        if self.status == Status.DRAW:
            screen.blit(self.text_draw, (130, 180))

    def set_turn(self, disk):
        disk = DisplayDisk(disk.filepath)
        self.display_group.add(disk)

    def set_score(self, black, white):
        self.black_score = str(black)
        self.white_score = str(white)

    def draw_score_display(self, screen):
        pygame.draw.rect(screen, GREEN, (40, self.top + 280, 80, 150))
        screen.blit(self.text_score, (25, self.top + 220))
        black_score = self.score_font.render(self.black_score, True, BLACK)
        white_score = self.score_font.render(self.white_score, True, BLACK)
        screen.blit(black_score, (140, 380))
        screen.blit(white_score, (140, 445))

    def draw_button(self, screen):
        pygame.draw.rect(screen, WHITE, (40, self.top + 490, 125, 40))

    def draw_grids(self, screen):
        x, y = self.left, self.top
        for i in range(self.grid_num + 1):
            pygame.draw.line(screen, BLACK, (self.left, y), (self.right, y), 2)
            pygame.draw.line(screen, BLACK, (x, self.top), (x, self.bottom), 2)
            x += self.grid_size
            y += self.grid_size

    def draw_players_color(self, screen):
        pygame.draw.circle(screen, BLACK, (500, 670), 8)
        if self.player_color == Piece.WHITE:
            pygame.draw.circle(screen, WHITE, (500, 670), 7)

    def draw(self, screen):
        self.draw_background(screen)
        self.draw_turn_display(screen)
        self.draw_score_display(screen)
        self.draw_button(screen)
        self.draw_grids(screen)
        self.draw_players_color(screen)

    def find_position(self, x, y):
        row = (y - self.top) // self.grid_size
        col = (x - self.left) // self.grid_size
        return row, col

    def grid_center(self, row, col):
        center_y = self.top + self.grid_size * row + self.grid_size // 2
        center_x = self.left + self.grid_size * col + self.grid_size // 2
        return Point(center_x, center_y)

    def place(self, row, col, color):
        self.disks[row][col] = Disk(color, self.grid_center(row, col))

    def reverse(self, row, col, color):
        disk = self.disks[row][col]
        self.disks[row][col] = disk.kill()
        self.place(row, col, color)


class Cursor(pygame.sprite.Sprite):

    def __init__(self, board):
        super().__init__(self.containers)
        self.image = pygame.image.load(Images.CURSOR.filepath).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.visible = False
        self.board = board

    def calc_distance(self, pt1, pt2):
        return ((pt2.x - pt1.x) ** 2 + (pt2.y - pt1.y) ** 2) ** 0.5

    def hover_button(self, cursor_pos):
        if self.board.button.left <= cursor_pos.x <= self.board.button.right and \
                self.board.button.top <= cursor_pos.y <= self.board.button.bottom:
            return True
        return False

    def hover_grid(self, cursor_pos):
        if self.board.left <= cursor_pos.x <= self.board.right and \
                self.board.top <= cursor_pos.y <= self.board.bottom:
            row, col = self.board.find_position(*cursor_pos)
            grid_center = self.board.grid_center(row, col)
            if self.calc_distance(cursor_pos, grid_center) <= 30:
                return True
        return False

    def show(self, cursor_pos):
        if self.hover_grid(cursor_pos) or self.hover_button(cursor_pos):
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


class Players(GameLogic):

    def __init__(self, board, color):
        self.board = board
        self.set_color(color)
        self.turn = None
        self.clicked = None
        self.create_sounds()

    def set_color(self, color):
        self.color = color
        self.opposite_color = Piece.opposite(self.color)
        self.display_disk = Images.get_image(self.color)

    def create_sounds(self):
        self.sound = pygame.mixer.Sound(Sounds.DISK.filepath)

    def reverse(self):
        self.sound.play()
        for row, col in self.find_reversibles(*self.clicked, self.board.disks, self.color):
            self.board.reverse(row, col, self.color)

    def click(self, *pos):
        self.clicked = pos
        self.sound.play()
        self.board.place(*self.clicked, self.color)

    def place(self):
        raise NotImplementedError()


class Player(Players):

    def __init__(self, board, piece):
        super().__init__(board, piece)

    def place(self, pos):
        row, col = self.board.find_position(*pos)
        if self.is_placeable(row, col, self.board.disks, self.color):
            self.click(row, col)
            return True


class Opponent(Players):

    def __init__(self, board, piece):
        super().__init__(board, piece)

        self.around_corners = [
            (0, 1), (1, 0), (1, 1),
            (0, 6), (1, 6), (1, 7),
            (6, 0), (6, 1), (7, 1),
            (6, 6), (6, 7), (7, 6)
        ]
        self.corners = [(0, 0), (0, 7), (7, 0), (7, 7)]

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

    def _corners(self):
        for r, c in self.corners:
            yield (r, c)

    def _non_corners(self):
        for r in range(self.board.grid_num):
            for c in range(self.board.grid_num):
                if (r, c) in self.corners:
                    continue
                yield (r, c)

    def _around_corners(self, corners):
        start = 0

        for corner in corners:
            around_corner = self.around_corners[start: start + 3]
            start += 3
            if not corner:
                for r, c in around_corner:
                    yield (r, c)

    def _sides(self):
        for r in range(self.board.grid_num):
            for c in range(self.board.grid_num):
                if (r, c) in self.corners or (r, c) in self.around_corners:
                    continue
                if r in (0, 7) or c in (0, 7):
                    yield (r, c)

    def counter(self, disks, grids):
        opponent = own = 0

        for r, c in grids():
            if not disks[r][c]:
                continue
            if disks[r][c] == self.color:
                own += 1
            else:
                opponent += 1

        return opponent, own

    def copy_current_board(self):
        disks = [[None for _ in range(self.board.grid_num)] for _ in range(self.board.grid_num)]

        for r in range(self.board.grid_num):
            for c in range(self.board.grid_num):
                if disk := self.board.disks[r][c]:
                    disks[r][c] = disk.color
        return disks

    def simulate(self, disks, color):
        empty_corners = [(r, c) for r, c in self.corners if not disks[r][c]]
        empty_around = [(r, c) for r, c in self.around_corners if not disks[r][c]]
        empty_sides = [(r, c) for (r, c) in self._sides() if not disks[r][c]]

        corners = arounds = sides = 0

        for r, c in self.get_placeables(disks, color):
            temp = [line[:] for line in disks]
            temp[r][c] = color
            for row, col in self.find_reversibles(r, c, temp, color.value):
                temp[row][col] = color

            corners += sum(1 for r, c in empty_corners if temp[r][c] == color)
            arounds += sum(1 for r, c in empty_around if temp[r][c] == color)
            sides += sum(1 for r, c in empty_sides if temp[r][c] == color)

        return corners, arounds, sides

    def evaluate(self, disks):
        corner_opponent, corner_own = self.counter(disks, self._corners)
        not_corner_opponent, not_corner_own = self.counter(disks, self._non_corners)
        corners = (disks[r][c] for r, c in self.corners)
        around_opponent, around_own = self.counter(disks, lambda: self._around_corners(corners))
        side_opponent, side_own = self.counter(disks, self._sides)

        evaluation = (corner_own - corner_opponent) \
            - (not_corner_own - not_corner_opponent) \
            + 21 * (corner_own - corner_opponent) \
            + 8 * (side_own - side_opponent) \
            - 10 * (around_own - around_opponent)

        return evaluation

    def find_best_move(self, grids, disks, color):
        for r, c in grids:
            temp = [line[:] for line in disks]
            temp[r][c] = color
            for row, col in self.find_reversibles(r, c, temp, color.value):
                temp[row][col] = color
            evaluation = self.evaluate(temp)
            corners, arounds, sides = self.simulate(temp, self.opposite_color)
            yield Candidate(evaluation, r, c, corners, arounds, sides)

    def guess(self, grids, disks):
        candidates = [cand for cand in self.find_best_move(grids, disks, self.color)]

        if all(c.evaluation == c.corners == c.arounds == c.sides == 0 for c in candidates):
            cand = random.choice(candidates)
        elif filtered := [c for c in candidates if c.corners == 0 and c.arounds > 0 and c.sides == 0]:
            filtered.sort(key=lambda x: (-x.evaluation, -x.arounds))
            cand = filtered[0]
        elif filtered := [c for c in candidates if c.corners == 0 and c.arounds > 0]:
            filtered.sort(key=lambda x: (-x.evaluation, x.sides, -x.arounds))
            cand = filtered[0]
        elif filtered := [c for c in candidates if c.corners == 0 and c.sides == 0]:
            cand = max(filtered, key=lambda x: x.evaluation)
        elif filtered := [cand for cand in candidates if cand.corners == 0]:
            filtered.sort(key=lambda x: (-x.evaluation, x.sides))
            cand = filtered[0]
        elif filtered := [c for c in candidates if c.arounds > 0 and c.sides == 0]:
            filtered.sort(key=lambda x: (-x.evaluation, x.corners, -x.arounds))
            cand = filtered[0]
        elif filtered := [c for c in candidates if c.arounds > 0]:
            filtered.sort(key=lambda x: (-x.evaluation, x.corners, x.sides, -x.arounds))
            cand = filtered[0]
        elif filtered := [c for c in candidates if c.sides == 0]:
            filtered.sort(key=lambda x: (-x.evaluation, x.corners))
            cand = filtered[0]
        elif filtered := [c for c in candidates if c.sides > 0]:
            filtered.sort(key=lambda x: (-x.evaluation, x.corners, x.sides))
            cand = filtered[0]
        else:
            cand = max(candidates, key=lambda x: x.evaluation)

        return cand.row, cand.col

    def place(self):
        disks = self.copy_current_board()
        placeable_grids = [pos for pos in self.get_placeables(disks, self.color)]

        if not (pos := self.find_corners(placeable_grids)):
            if filtered := [grid for grid in placeable_grids if grid not in self.around_corners]:
                placeable_grids = filtered
            pos = self.guess(placeable_grids, disks)

        self.click(*pos)


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
        self.disks = [[None for _ in range(Board.grid_num)] for _ in range(Board.grid_num)]
        self.board = Board(self, self.display_group)
        self.cursor = Cursor(self.board)
        self.player = Player(self.board, Piece.BLACK)
        self.opponent = Opponent(self.board, Piece.WHITE)
        self.status = None
        self.create_events()

    def create_events(self):
        self._place = pygame.USEREVENT + 0
        self._reverse = pygame.USEREVENT + 1
        self._change = pygame.USEREVENT + 2
        self._guess = pygame.USEREVENT + 3
        self._pass = pygame.USEREVENT + 4
        self._gameover = pygame.USEREVENT + 5

    def calc_score(self):
        black = sum(sum(
            disk.color == Piece.BLACK for disk in row if disk) for row in self.disks)
        white = sum(sum(
            disk.color == Piece.WHITE for disk in row if disk) for row in self.disks)
        self.board.set_score(black, white)
        if black + white == 64:
            return False
        return True

    def change_first_player(self):
        for player in (self.player, self.opponent):
            color = Piece.opposite(player.color)
            player.set_color(color)

    def start(self):
        self.timer = 0
        self.event = None
        self.board.setup()
        self.player.turn = self.player.color == Piece.BLACK
        self.opponent.turn = self.opponent.color == Piece.BLACK
        self.status = Status.PLAY

        if self.player.turn:
            self.board.set_turn(self.player.display_disk)
        else:
            self.board.set_turn(self.opponent.display_disk)
            self.set_timer(self._place)

    def set_timer(self, event_type, t=40):
        """Using pygame.set_timer resulted in program crash, but no errors
           were raised.
        """
        self.status = Status.SET_TIMER
        self.event = pygame.event.Event(event_type)
        self.timer = t

    @property
    def current_player(self):
        return self.player if self.player.turn else self.opponent

    @property
    def next_player(self):
        return self.player if not self.player.turn else self.opponent

    def player_click(self, click_pos):
        if self.player.turn and self.cursor.visible:
            if self.player.has_placeables(self.disks, self.player.color):
                if self.player.place(Point(*click_pos)):
                    self.set_timer(self._reverse)

    def place_disk(self):
        self.opponent.place()
        self.set_timer(self._reverse)

    def reverse_disks(self):
        self.current_player.reverse()
        if self.calc_score():
            self.set_timer(self._change)
        else:
            self.set_timer(self._gameover)

    def pass_turn(self):
        self.board.status = Status.PLAY
        self.set_timer(self._change)

    def take_turns(self):
        self.player.turn = not self.player.turn
        self.opponent.turn = not self.opponent.turn
        self.board.set_turn(self.current_player.display_disk)
        self.set_timer(self._guess)

    def guess_placeable(self):
        if not self.current_player.has_placeables(self.disks, self.current_player.color):
            if not self.next_player.has_placeables(self.disks, self.next_player.color):
                self.set_timer(self._gameover)
            else:
                self.board.status = Status.PASS
                self.set_timer(self._pass)
        else:
            if self.opponent.turn:
                self.set_timer(self._place)

    def game_over(self):
        if self.board.black_score == self.board.white_score:
            self.board.status = Status.DRAW
        else:
            disk = Images.BLACK_DISPLAY\
                if self.board.black_score > self.board.white_score else Images.WHITE_DISPLAY
            self.board.set_turn(disk)
            self.board.status = Status.WIN
        self.status = Status.GAMEOVER

    def run(self):
        clock = pygame.time.Clock()
        self.start()

        while True:
            if self.status == Status.SET_TIMER:
                self.timer -= 1
                if self.timer == 0:
                    self.status = Status.PLAY
                    pygame.event.post(self.event)

            clock.tick(60)
            self.screen.fill(GRAY)
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
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEMOTION:
                    x, y = event.pos
                    self.cursor.show(Point(*event.pos))
                if event.type == self._reverse:
                    self.reverse_disks()
                if event.type == self._place:
                    self.place_disk()
                if event.type == self._change:
                    self.take_turns()
                if event.type == self._guess:
                    self.guess_placeable()
                if event.type == self._pass:
                    self.pass_turn()
                if event.type == self._gameover:
                    self.game_over()
                # if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if event.type == MOUSEBUTTONUP and event.button == 1:
                    if self.board.button.rect.collidepoint(*event.pos):
                        self.board.button.click()
                    else:
                        self.player_click(event.pos)

            pygame.display.update()


if __name__ == '__main__':
    game = Othello()
    game.run()
