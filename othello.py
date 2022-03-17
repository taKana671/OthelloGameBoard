import pygame
import sys
from pygame.locals import *


SQUARE_SIZE = 70


class Othello:

    def __init__(self, screen):
        self.screen = screen

    def create_board(self):
        left = x = 70
        top = y = 120
        right = x + 8 * SQUARE_SIZE
        bottom = y + 8 * SQUARE_SIZE

        for i in range(9):
            pygame.draw.line(self.screen, (0, 0, 0), (left, y), (right, y), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (x, top), (x, bottom), 2)
            x += SQUARE_SIZE
            y += SQUARE_SIZE

    def update(self):
        self.create_board()

    def click(self, x, y):
        # ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


class Stone(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__(self.containers)
        self.image = pygame.image.load('igo_white.png').convert_alpha()
        # self.image = pygame.transform.scale(self.image, (100, 70))
        self.image = pygame.transform.scale(self.image, (99, 90))
        self.rect = self.image.get_rect()
        self.rect.centerx = 385
        self.rect.centery = 365



def main():
    pygame.init
    screen = pygame.display.set_mode((700, 800))
    pygame.display.set_caption('Othello game board')
    stones = pygame.sprite.RenderUpdates()
    Stone.containers = stones

    clock = pygame.time.Clock()
    othello = Othello(screen)

    _ = Stone()

    while True:
        clock.tick(60)
        screen.fill((0, 100, 0))
        othello.update()
        stones.update()
        stones.draw(screen)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                othello.click(*event.pos)

        pygame.display.update()


if __name__ == '__main__':
    main()
