import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from pygame.locals import *
from unittest import TestCase, main, mock

from othello import Board, Othello, Piece, Status, Images, Point, Cursor, Button


class BoardTestCase(TestCase):
    """Tests for Board class
    """

    def setUp(self):
        mock.patch('othello.Button').start()
        self.mock_disk_class = mock.patch('othello.Disk').start()

        mock_font = mock.MagicMock()
        mock_font.render.side_effect = ['TURN', 'SCORE', 'PASS', 'WIN', 'DRAW']
        mock_sysfont = mock.patch('othello.pygame.font.SysFont').start()
        mock_sysfont.return_value = mock_font
        self.mock_screen = mock.MagicMock()
        self.mock_disk = mock.MagicMock()
        self.mock_disk.kill.return_value = None

        self.disks = [[None for _ in range(8)] for _ in range(8)]
        self.game = mock.create_autospec(
            spec=Othello,
            instance=True,
            disks=self.disks
        )
        self.mock_group = mock.MagicMock()
        self.board = Board(self.game, self.mock_group)

    def tearDown(self):
        mock.patch.stopall()

    def test_setup(self):
        calls = [
            mock.call(3, 3, Piece.WHITE),
            mock.call(3, 4, Piece.BLACK),
            mock.call(4, 3, Piece.BLACK),
            mock.call(4, 4, Piece.WHITE)
        ]

        with mock.patch('othello.Board.place') as mock_place:
            self.board.setup()
            mock_place.assert_has_calls(calls)

        self.assertEqual(self.board.status, Status.PLAY)
        self.assertTrue(self.board.black_score == self.board.white_score == '')

    def test_clear(self):
        disk_pos = [(1, 3), (2, 6), (3, 5), (3, 6), (5, 7), (6, 6)]

        for r, c in disk_pos:
            self.disks[r][c] = self.mock_disk

        self.board.clear()
        for row in self.disks:
            with self.subTest(row):
                self.assertTrue(not any(row))

    def test_draw_backgrond(self):
        calls = [
            mock.call(self.mock_screen, (76, 38, 0), (200, 50, 600, 600)),
            mock.call(self.mock_screen, (0, 100, 0), (220, 70, 560, 560)),
        ]

        with mock.patch('othello.pygame.draw.rect') as mock_draw:
            self.board.draw_background(self.mock_screen)
            mock_draw.assert_has_calls(calls)

    def test_draw_turn_display(self):
        tests = [Status.PASS, Status.WIN, Status.DRAW]
        expects = [
            [mock.call('TURN', (35, 80)), mock.call('PASS', (130, 180))],
            [mock.call('TURN', (35, 80)), mock.call('WIN', (130, 180))],
            [mock.call('TURN', (35, 80)), mock.call('DRAW', (130, 180))],
        ]
        with mock.patch('othello.pygame.draw.rect'), \
                mock.patch('othello.pygame.draw.ellipse'):
            for status, calls in zip(tests, expects):
                with self.subTest(status):
                    self.board.status = status
                    self.board.draw_turn_display(self.mock_screen)
                    self.mock_screen.blit.assert_has_calls(calls)
                self.mock_screen.reset_mock()

    def test_set_turn(self):
        mock_display_disk = mock.Mock()

        with mock.patch('othello.DisplayDisk') as mock_display:
            mock_display.return_value = mock_display_disk
            self.board.set_turn(Images.BLACK_DISPLAY)
            mock_display.assert_called_once_with(Path('images', 'black_display.png'))
            self.mock_group.add.assert_called_once_with(mock_display_disk)

    def test_set_score(self):
        self.board.black_score = self.board.white_score = ''
        self.board.set_score(20, 15)
        self.assertEqual(
            (self.board.black_score, self.board.white_score), ('20', '15'))

    def test_draw_grids(self):
        calls = []
        for i in range(9):
            calls.append(mock.call(self.mock_screen, (0, 0, 0), (220, 70 + i * 70), (780, 70 + i * 70), 2))
            calls.append(mock.call(self.mock_screen, (0, 0, 0), (220 + i * 70, 70), (220 + i * 70, 630), 2))

        with mock.patch('othello.pygame.draw.line') as mock_line:
            self.board.draw_grids(self.mock_screen)
            self.assertEqual(mock_line.call_args_list, calls)

    def test_draw_player_color(self):
        tests = [Piece.BLACK, Piece.WHITE]
        calls_list = [
            [mock.call(self.mock_screen, (0, 0, 0), (500, 670), 8)],
            [mock.call(self.mock_screen, (0, 0, 0), (500, 670), 8),
             mock.call(self.mock_screen, (255, 255, 255), (500, 670), 7)]
        ]
        with mock.patch('othello.pygame.draw.circle') as mock_circle:
            for color, calls in zip(tests, calls_list):
                self.board.player_color = color
                self.board.draw_players_color(self.mock_screen)
                self.assertEqual(mock_circle.call_args_list, calls)
                mock_circle.reset_mock()

    def test_find_position(self):
        tests = [
            [(392, 93), (0, 2)],
            [(613, 454), (5, 5)],
            [(397, 512), (6, 2)],
            [(674, 169), (1, 6)],
            [(375, 304), (3, 2)]
        ]
        for test, expect in tests:
            with self.subTest(test):
                pos = self.board.find_position(*test)
                self.assertEqual(pos, expect)

    def test_grid_center(self):
        tests = [
            [(0, 2), Point(395, 105)],
            [(5, 5), Point(605, 455)],
            [(6, 2), Point(395, 525)],
            [(1, 6), Point(675, 175)],
            [(3, 2), Point(395, 315)]
        ]
        for test, expect in tests:
            with self.subTest(test):
                center = self.board.grid_center(*test)
                self.assertEqual(center, expect)

    def test_place(self):
        tests = [
            (5, 5, Piece.BLACK),
            (6, 2, Piece.BLACK),
            (1, 6, Piece.WHITE),
            (3, 2, Piece.WHITE),
        ]
        self.mock_disk_class.side_effect = [mock.MagicMock(color=test[2]) for test in tests]
        calls = [
            mock.call(Piece.BLACK, Point(605, 455)),
            mock.call(Piece.BLACK, Point(395, 525)),
            mock.call(Piece.WHITE, Point(675, 175)),
            mock.call(Piece.WHITE, Point(395, 315)),
        ]
        for test in tests:
            self.board.place(*test)

        self.mock_disk_class.assert_has_calls(calls)
        for row, col, color in tests:
            with self.subTest():
                self.assertEqual(self.disks[row][col].color, color)

    def test_reverse(self):
        tests = [
            (2, 3, Piece.BLACK),
            (4, 5, Piece.BLACK),
            (0, 2, Piece.WHITE),
            (5, 6, Piece.WHITE)
        ]
        for row, col, _ in tests:
            self.disks[row][col] = self.mock_disk

        with mock.patch('othello.Board.place') as mock_place:
            for row, col, color in tests:
                with self.subTest():
                    self.board.reverse(row, col, color)
                    self.assertTrue(self.disks[row][col] is None)
                    mock_place.assert_called_once_with(row, col, color)
                    mock_place.reset_mock()


class CursorTestCase(TestCase):
    """Tests for Cursor class
    """

    def setUp(self):
        Cursor.containers = mock.MagicMock()
        mock.patch('othello.pygame.image.load').start()
        mock.patch('othello.pygame.sprite.Sprite').start()
        mock.patch('othello.Board.set_displays').start()
        rect = Rect(0, 0, 80, 50)
        mock_image = mock.MagicMock()
        mock_image.get_rect.return_value = rect
        mock_scale = mock.patch('othello.pygame.transform.scale').start()
        mock_scale.return_value = mock_image
        board = Board(mock.MagicMock(), mock.MagicMock())
        board.button = self.get_button()
        self.cursor = Cursor(board)

    def tearDown(self):
        mock.patch.stopall()

    def get_button(self):
        button = mock.create_autospec(
            spec=Button,
            instance=True,
            left=43,
            right=162,
            top=563,
            bottom=597
        )
        return button

    def test_calc_distance(self):
        tests = [
            [(Point(100, 200), Point(50, 80)), 130.0],
            [(Point(20, 5), Point(40, 20)), 25.0]
        ]
        for test, expect in tests:
            with self.subTest():
                result = self.cursor.calc_distance(*test)
                self.assertEqual(result, expect)

    def test_hover_button(self):
        tests = [
            [Point(43, 563), True],
            [Point(162, 597), True],
            [Point(85, 580), True],
            [Point(41, 570), False],
            [Point(120, 598), False],
            [Point(165, 602), False]
        ]
        for test, expect in tests:
            with self.subTest(test):
                result = self.cursor.hover_button(test)
                self.assertEqual(result, expect)

    def test_hover_grid(self):
        tests = [
            [Point(367, 284), False],
            [Point(391, 313), True],
            [Point(477, 214), False],
            [Point(532, 239), True],
            [Point(600, 284), False],
            [Point(680, 321), True]
        ]
        for test, expect in tests:
            with self.subTest(test):
                result = self.cursor.hover_grid(test)
                self.assertEqual(result, expect)

    def test_show_false(self):
        tests = [Point(367, 284), Point(41, 570), Point(20, 30)]

        with mock.patch('othello.pygame.mouse.set_visible') as mock_set_visible:
            for test in tests:
                self.cursor.visible = True
                with self.subTest(test):
                    self.cursor.show(test)
                    self.assertEqual(self.cursor.visible, False)
                    mock_set_visible.assert_called_once_with(True)
                    mock_set_visible.reset_mock()

    def test_show_true(self):
        tests = [Point(162, 597), Point(680, 321)]
        expects = [(165, 597), (683, 321)]

        with mock.patch('othello.pygame.mouse.set_visible') as mock_set_visible:
            for test, expect in zip(tests, expects):
                with self.subTest(test):
                    self.cursor.show(test)
                    self.assertEqual(self.cursor.visible, True)
                    mock_set_visible.assert_called_once_with(False)
                    self.assertEqual(
                        (self.cursor.rect.centerx, self.cursor.rect.top), expect)
                    mock_set_visible.reset_mock()


if __name__ == '__main__':
    main()