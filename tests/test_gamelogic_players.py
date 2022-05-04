import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from pygame.locals import *
from unittest import TestCase, main, mock

from othello import Board, GameLogic, Piece, Disk, Players, \
    Player, Images, Point, Opponent


class TestUtils:

    def get_disks(self, black_pos, white_pos, black, white):
        disks = [[None for _ in range(8)] for _ in range(8)]

        for r, c in black_pos:
            disks[r][c] = black
        for r, c in white_pos:
            disks[r][c] = white
        return disks

    def get_disk_instance(self, color):
        disk = mock.create_autospec(
            spec=Disk,
            instance=True,
            color=color
        )
        return disk

    def get_gameover_disks(self, black, white):
        disks = [[white for _ in range(8)] for _ in range(8)]
        disks[0][0] = None
        for r, c in [(0, 1), (1, 0), (1, 1)]:
            disks[r][c] = black
        return disks

    def get_board_instance(self, disks):
        board = mock.create_autospec(
            spec=Board,
            instance=True,
            disks=disks,
            grid_num=8
        )
        return board


class GameLogicTestCase(TestCase, TestUtils):
    """Tests for Board class
    """

    def setUp(self):
        self.game_logic = GameLogic()
        black_pos = [(2, 2), (3, 3), (3, 4), (4, 4)]
        white_pos = [(4, 3), (5, 3), (5, 4), (5, 5)]
        self.piece_disks = self.get_disks(
            black_pos,
            white_pos,
            Piece.BLACK,
            Piece.WHITE
        )
        self.sprite_disks = self.get_disks(
            black_pos,
            white_pos,
            self.get_disk_instance(Piece.BLACK),
            self.get_disk_instance(Piece.WHITE)
        )

    def test_reverse_check(self):
        tests = [
            [(self.piece_disks, Piece.BLACK.value, 5, 3, -1, 0), 2],
            [(self.piece_disks, Piece.BLACK.value, 5, 3, -1, -1), None],
            [(self.piece_disks, Piece.BLACK.value, 5, 3, -1, 1), 1],
            [(self.piece_disks, Piece.WHITE.value, 3, 4, 1, 0), 2],
            [(self.piece_disks, Piece.WHITE.value, 3, 4, 1, -1), 1],
            [(self.piece_disks, Piece.WHITE.value, 5, 5, 0, -1), 0],
            [(self.piece_disks, Piece.WHITE.value, 2, 2, -1, 0), None],
            [(self.sprite_disks, Piece.BLACK, 5, 3, -1, 0), 2],
            [(self.sprite_disks, Piece.BLACK, 5, 3, -1, -1), None],
            [(self.sprite_disks, Piece.BLACK, 5, 3, -1, 1), 1],
            [(self.sprite_disks, Piece.WHITE, 3, 4, 1, 0), 2],
            [(self.sprite_disks, Piece.WHITE, 3, 4, 1, -1), 1],
            [(self.sprite_disks, Piece.WHITE, 5, 5, 0, -1), 0],
            [(self.sprite_disks, Piece.WHITE, 2, 2, -1, 0), None]
        ]
        for test, expect in tests:
            with self.subTest(test):
                result = self.game_logic.reverse_check(*test)
                self.assertEqual(result, expect)

    def test_is_placeable(self):
        tests = [
            [(0, 2, self.piece_disks, Piece.BLACK.value), False],
            [(6, 3, self.piece_disks, Piece.WHITE.value), False],
            [(2, 2, self.piece_disks, Piece.BLACK.value), False],
            [(3, 4, self.piece_disks, Piece.WHITE.value), False],
            [(6, 3, self.piece_disks, Piece.BLACK.value), True],
            [(2, 5, self.piece_disks, Piece.WHITE.value), True],
            [(0, 2, self.sprite_disks, Piece.BLACK), False],
            [(6, 3, self.sprite_disks, Piece.WHITE), False],
            [(2, 2, self.sprite_disks, Piece.BLACK), False],
            [(3, 4, self.sprite_disks, Piece.WHITE), False],
            [(6, 3, self.sprite_disks, Piece.BLACK), True],
            [(2, 5, self.sprite_disks, Piece.WHITE), True],
        ]
        for test, expect in tests:
            with self.subTest(test):
                result = self.game_logic.is_placeable(*test)
                self.assertEqual(result, expect)

    def test_get_reversibles(self):
        expect = [(3, 4), (4, 3), (5, 2)]
        result = [pos for pos in self.game_logic.get_reversibles(3, 4, 1, -1, 3)]
        self.assertEqual(result, expect)

    def test_find_reversibles(self):
        tests = [
            [(6, 3, self.piece_disks, Piece.BLACK.value), [(5, 3), (4, 3)]],
            [(1, 1, self.piece_disks, Piece.WHITE.value), [(2, 2), (3, 3), (4, 4)]],
            [(2, 3, self.piece_disks, Piece.WHITE.value), [(3, 3)]],
            [(6, 3, self.sprite_disks, Piece.BLACK), [(5, 3), (4, 3)]],
            [(1, 1, self.sprite_disks, Piece.WHITE), [(2, 2), (3, 3), (4, 4)]],
            [(2, 3, self.sprite_disks, Piece.WHITE), [(3, 3)]]
        ]
        for test, expect in tests:
            result = [pos for pos in self.game_logic.find_reversibles(*test)]
            self.assertEqual(result, expect)

    def test_has_placeables_true(self):
        tests = [
            (self.piece_disks, Piece.WHITE.value),
            (self.piece_disks, Piece.BLACK.value),
            (self.sprite_disks, Piece.WHITE),
            (self.sprite_disks, Piece.BLACK)
        ]
        for test in tests:
            with self.subTest():
                result = self.game_logic.has_placeables(*test)
                self.assertTrue(result)

    def test_has_placeables_false(self):
        piece_disks = self.get_gameover_disks(Piece.BLACK, Piece.WHITE)
        sprite_disks = self.get_gameover_disks(
            self.get_disk_instance(Piece.BLACK), self.get_disk_instance(Piece.WHITE))
        tests = [
            (piece_disks, Piece.BLACK.value),
            (sprite_disks, Piece.BLACK)
        ]
        for test in tests:
            with self.subTest(test):
                result = self.game_logic.has_placeables(*test)
                self.assertFalse(result)


class PlayersTestCase(TestCase):
    """Tests for Players class
    """

    def setUp(self):
        self.mock_sound = mock.MagicMock()
        mock_mixier = mock.patch('othello.pygame.mixer.Sound').start()
        mock_mixier.return_value = self.mock_sound

        self.disks = [[None for _ in range(8)] for _ in range(8)]
        self.mock_board = mock.create_autospec(
            spec=Board, instance=True, disks=self.disks)
        self.players = Players(self.mock_board, Piece.BLACK)

    def tearDown(self):
        mock.patch.stopall()

    def test_set_color(self):
        self.players.set_color(Piece.WHITE)
        self.assertEqual(
            self.players.display_disk, Images.WHITE_DISPLAY)

    def test_reverse(self):
        positions = [(2, 3), (3, 3), (4, 3)]
        calls = [mock.call(r, c, Piece.BLACK) for r, c in positions]
        self.players.clicked = (1, 3)

        def find_reversibles():
            for pos in positions:
                yield pos

        with mock.patch('othello.GameLogic.find_reversibles') as mock_find:
            mock_find.return_value = find_reversibles()
            self.players.reverse()

            self.mock_sound.play.assert_called_once()
            mock_find.assert_called_once_with(1, 3, self.disks, Piece.BLACK)
            self.assertEqual(self.mock_board.reverse.call_args_list, calls)

    def test_click(self):
        self.players.click(5, 4)
        self.mock_sound.play.assert_called_once_with()
        self.mock_board.place.assert_called_once_with(5, 4, Piece.BLACK)


# class PlayerCommon(TestCase):

#     def setUp(self):
#         mock.patch('othello.pygame.mixer.Sound').start()
#         self.disks = [[None for _ in range(8)] for _ in range(8)]
#         self.mock_board = mock.create_autospec(
#             spec=Board, instance=True, disks=self.disks, grid_num=8)
#         self.player = Player(self.mock_board, Piece.BLACK)

#     def tearDown(self):
#         mock.patch.stopall()

class PlayerTestCase(TestCase, TestUtils):
    """Tests for Player class
    """

    def setUp(self):
        mock.patch('othello.pygame.mixer.Sound').start()
        black_pos = [(2, 2), (3, 3), (3, 4), (4, 4)]
        white_pos = [(4, 3), (5, 3), (5, 4), (5, 5)]
        self.disks = self.get_disks(
            black_pos,
            white_pos,
            self.get_disk_instance(Piece.BLACK),
            self.get_disk_instance(Piece.WHITE)
        )
        self.mock_board = self.get_board_instance(self.disks)
        self.player = Player(self.mock_board, Piece.BLACK)

    def tearDown(self):
        mock.patch.stopall()

    def test_place_true(self):
        pt = Point(397, 512)
        pos = (6, 1)
        self.mock_board.find_position.return_value = pos

        with mock.patch('othello.GameLogic.is_placeable') as mock_placeable, \
                mock.patch('othello.Players.click') as mock_click:
            mock_placeable.return_value = True

            result = self.player.place(pt)
            self.assertTrue(result)
            self.mock_board.find_position.assert_called_once_with(pt.x, pt.y)
            mock_placeable.assert_called_once_with(*pos, self.disks, Piece.BLACK)
            mock_click.assert_called_once_with(*pos)

    def test_place_false(self):
        pt = Point(397, 512)
        pos = (6, 1)
        self.mock_board.find_position.return_value = pos

        with mock.patch('othello.GameLogic.is_placeable') as mock_placeable, \
                mock.patch('othello.Players.click') as mock_click:
            mock_placeable.return_value = False

            result = self.player.place(pt)
            self.assertFalse(result)
            self.mock_board.find_position.assert_called_once_with(pt.x, pt.y)
            mock_placeable.assert_called_once_with(*pos, self.disks, Piece.BLACK)
            mock_click.assert_not_called()


class OpponentTestCase(TestCase, TestUtils):
    """Tests for Opponent class
    """

    def setUp(self):
        mock.patch('othello.pygame.mixer.Sound').start()
        self.disks = [[None for _ in range(8)] for _ in range(8)]
        self.mock_board = self.get_board_instance(self.disks)
        self.opponent = Opponent(self.mock_board, Piece.WHITE)

    def tearDown(self):
        mock.patch.stopall()

    def test_get_placeables(self):
        black_pos = [(2, 2), (3, 3), (3, 4), (4, 4)]
        white_pos = [(4, 3), (5, 3), (5, 4), (5, 5)]
        disks = self.get_disks(black_pos, white_pos, Piece.BLACK, Piece.WHITE)
        expects = [(1, 1), (2, 3), (2, 4), (2, 5), (3, 5), (4, 5)]
        result = [pos for pos in self.opponent.get_placeables(disks, Piece.WHITE)]
        self.assertEqual(result, expects)

    def test_find_corners(self):
        grids = ((0, 3), (0, 7), (5, 6), (7, 0), (7, 1))
        expect = (0, 7)
        result = self.opponent.find_corners(grids)
        self.assertEqual(result, expect)

    def test_counter_corners(self):
        black_pos = [(7, 7)]
        white_pos = [(0, 7), (7, 0), (0, 0)]
        disks = self.get_disks(black_pos, white_pos, Piece.BLACK, Piece.WHITE)

        tests = [
            [Piece.BLACK, (3, 1)],
            [Piece.WHITE, (1, 3)]
        ]
        for color, expect in tests:
            with self.subTest(color):
                self.opponent.color = color
                result = self.opponent.counter(disks, self.opponent._corners)
                self.assertEqual(result, expect)

    def test_counter_non_corners(self):
        black_pos = [(7, 7), (1, 0), (3, 2), (5, 3)]
        white_pos = [(0, 7), (7, 6), (4, 3)]
        disks = self.get_disks(black_pos, white_pos, Piece.BLACK, Piece.WHITE)

        tests = [
            [Piece.BLACK, (2, 3)],
            [Piece.WHITE, (3, 2)]
        ]
        for color, expect in tests:
            with self.subTest(color):
                self.opponent.color = color
                result = self.opponent.counter(disks, self.opponent._non_corners)
                self.assertEqual(result, expect)

    def test_counter_around_corners(self):
        black_pos = [(1, 0), (3, 2), (1, 7)]
        white_pos = [(0, 7), (7, 6), (6, 6), (6, 7), (4, 3)]
        disks = self.get_disks(black_pos, white_pos, Piece.BLACK, Piece.WHITE)

        tests = [
            [Piece.BLACK, (3, 1)],
            [Piece.WHITE, (1, 3)]
        ]
        for color, expect in tests:
            with self.subTest(color):
                self.opponent.color = color
                corners = [None, Piece.WHITE, None, None]
                result = self.opponent.counter(
                    disks, lambda: self.opponent._around_corners(corners))
                self.assertEqual(result, expect)

    def test_counter_sides(self):
        black_pos = [(1, 0), (3, 2), (1, 7)]
        white_pos = [(0, 7), (7, 6), (6, 6), (4, 3)]
        disks = self.get_disks(black_pos, white_pos, Piece.BLACK, Piece.WHITE)

        tests = [
            [Piece.BLACK, (1, 2)],
            [Piece.WHITE, (2, 1)]
        ]
        for color, expect in tests:
            with self.subTest(color):
                self.opponent.color = color
                result = self.opponent.counter(disks, self.opponent._sides)
                self.assertEqual(result, expect)


if __name__ == '__main__':
    main()