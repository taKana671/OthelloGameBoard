import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from pygame.locals import *
from unittest import TestCase, main, mock

from othello import (Piece, Images, Sounds, Disk, Point,
    DisplayDisk, Button, Othello, Status)


class PieceTestCase(TestCase):
    """Tests for Piece class
    """

    def test_color(self):
        expects = [0, 1]
        for piece, expect in zip(Piece.__members__.values(), expects):
            with self.subTest(piece):
                self.assertEqual(piece.color, expect)

    def test_filepath(self):
        expects = [
            Path('images', 'black.png'),
            Path('images', 'white.png')
        ]
        for piece, expect in zip(Piece.__members__.values(), expects):
            with self.subTest(piece):
                self.assertEqual(piece.filepath, expect)


class ImageTestCase(TestCase):
    """Tests for Images class
    """

    def test_filepath(self):
        expects = [
            Path('images', 'black_display.png'),
            Path('images', 'white_display.png'),
            Path('images', 'cursor.png'),
            Path('images', 'button.png'),
        ]

        for image, expect in zip(Images.__members__.values(), expects):
            with self.subTest(image):
                self.assertEqual(image.filepath, expect)

    def test_get_image(self):
        tests = [Piece.WHITE, Piece.BLACK]
        expects = [Images.WHITE_DISPLAY, Images.BLACK_DISPLAY]

        for piece, expect in zip(tests, expects):
            with self.subTest(piece):
                image = Images.get_image(piece)
                self.assertEqual(image, expect)


class SoundsTestCase(TestCase):
    """Tests for Sounds clas
    """

    def test_filepath(self):
        expect = Path('sounds', 'disk.wav')
        self.assertEqual(Sounds.DISK.filepath, expect)


class OthelloTest(TestCase):

    def setUp(self):
        mock.patch('othello.pygame.sprite.Sprite').start()
        rect = Rect(0, 0, 80, 50)
        self.mock_image = mock.MagicMock()
        self.mock_image.get_rect.return_value = rect

    def tearDown(self):
        mock.patch.stopall()


class DiskTestCase(OthelloTest):
    """Tests for Disk class
    """

    def test_initialization(self):
        Disk.containers = mock.MagicMock()
        color = Piece.BLACK
        pt = Point(200, 300)

        with mock.patch('othello.pygame.image.load'),\
                mock.patch('othello.pygame.transform.scale') as mock_scale:
            mock_scale.return_value = self.mock_image
            disk = Disk(color, pt)

        self.assertEqual(disk.color, color)
        self.assertEqual((disk.rect.centerx, disk.rect.centery), pt)


class DisplayDiskTestCase(OthelloTest):
    """Tests for DisplayDisk class
    """

    def test_initialization(self):
        DisplayDisk.containers = mock.MagicMock()
        with mock.patch('othello.pygame.image.load'), \
                mock.patch('othello.pygame.transform.scale') as mock_scale:
            mock_scale.return_value = self.mock_image
            display_disk = DisplayDisk('test.png')

        self.assertEqual(
            (display_disk.rect.centerx, display_disk.rect.centery), (80, 180))


class ButtonTestCase(OthelloTest):
    """Tests for Button class
    """

    def setUp(self):
        Button.containers = mock.MagicMock()
        super().setUp()
        self.pt = Point(200, 300)
        self.file = 'test.png'

    def get_game(self, status=None):
        mock_board = mock.MagicMock(player_color=Piece.WHITE)
        mock_player = mock.MagicMock(color=Piece.BLACK)
        game = mock.create_autospec(
            spec=Othello,
            instance=True,
            status=status,
            board=mock_board,
            player=mock_player
        )
        return game

    def test_constractor(self):
        mock_convert = mock.MagicMock()
        mock_convert.convert_alpha.return_value = self.mock_image
        game = self.get_game()

        with mock.patch('othello.pygame.image.load') as mock_load:
            mock_load.return_value = mock_convert
            button = Button(self.file, self.pt, game)

        self.assertEqual((button.rect.centerx, button.rect.centery), self.pt)
        self.assertEqual(button.left, 160)
        self.assertEqual(button.right, 240)
        self.assertEqual(button.top, 275)
        self.assertEqual(button.bottom, 325)

    def test_click(self):
        game = self.get_game(Status.PLAY)

        with mock.patch('othello.pygame.image.load'):
            button = Button(self.file, self.pt, game)
            button.click()
        game.board.clear.assert_called_once()
        game.start.assert_called_once()
        game.change_first_player.assert_not_called()
        self.assertEqual(game.board.player_color, Piece.WHITE)

    def test_click_gameover(self):
        game = self.get_game(Status.GAMEOVER)

        with mock.patch('othello.pygame.image.load'):
            button = Button(self.file, self.pt, game)
            button.click()
        game.board.clear.assert_called_once()
        game.start.assert_called_once()
        game.change_first_player.assert_called_once()
        self.assertEqual(game.board.player_color, Piece.BLACK)


if __name__ == '__main__':
    main()