import pygame
import sys
from pygame.locals import *


class Board:

    def __init__(self):
        self.grid_size = 70
        self.rows = 8
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

    def grid_center(self, row, col):
        pass




class Othello:

    def __init__(self, screen, board, cursor):
        self.screen = screen
        self.board = board
        self.cursor = cursor

    def update(self):
        self.board.draw(self.screen)

    def click(self, x, y):
        if self.board.left <= x <= self.board.right and \
                self.board.top <= y <= self.board.bottom:
            col = int((x - self.board.left) / self.board.grid_size)
            row = int((y - self.board.top) / self.board.grid_size)

            print(row, col)

    def cursor(self, x, y):
        pass



class Stone(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__(self.containers)
        self.image = pygame.image.load('igo_white.png').convert_alpha()
        # self.image = pygame.transform.scale(self.image, (100, 70))
        self.image = pygame.transform.scale(self.image, (99, 90))
        self.rect = self.image.get_rect()
        self.rect.centerx = 385
        self.rect.centery = 365


class Mouse(pygame.sprite.Sprite):

    def __init__(self, board):
        super().__init__(self.containers)
        self.image = pygame.image.load('cursor.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.visible = False
        self.board = board

    def appear(self):
        pygame.mouse.set_visible(False)
        self.image = self.scale.transform(self.image, (50, 50))

    def move(self, x, y):
        self.rect.centerx = x + 3
        self.rect.top = y



def main():
    pygame.init
    screen = pygame.display.set_mode((700, 800))
    pygame.display.set_caption('Othello game board')
    pygame.mouse.set_visible(False)
    stones = pygame.sprite.RenderUpdates()
    cursor = pygame.sprite.RenderUpdates()
    Stone.containers = stones
    Mouse.containers = cursor

    clock = pygame.time.Clock()
    board = Board()
    finger = Mouse(board)
    othello = Othello(screen, board, finger)

    _ = Stone()

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
                # cursor.move(x, y)
                # print(f'cursor x: {x}, y: {y}')

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if finger.visible:
                    othello.click(*event.pos)

        pygame.display.update()


if __name__ == '__main__':
    main()
