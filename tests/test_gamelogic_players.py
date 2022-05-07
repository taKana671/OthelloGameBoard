import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from pygame.locals import *
from unittest import TestCase, main, mock

from othello import Board, GameLogic, Piece, Disk, Players, \
    Player, Images, Point, Opponent, Candidate


class TestUtils:

    def get_disks(self, black_pos, white_pos, black=None, white=None):
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

    def find_best_move(self, cands):
        for cand in cands:
            yield cand

    def get_placeables(self, positions):
        for pos in positions:
            yield pos


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
        tests = [Piece.WHITE, Piece.BLACK]
        expects = [
            (Piece.WHITE, Piece.BLACK, Images.WHITE_DISPLAY),
            (Piece.BLACK, Piece.WHITE, Images.BLACK_DISPLAY),
        ]
        for test, (color, opposite, display) in zip(tests, expects):
            with self.subTest(test):
                self.players.set_color(test)
                self.assertEqual(self.players.color, color)
                self.assertEqual(self.players.opposite_color, opposite)
                self.assertEqual(self.players.display_disk, display)

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


class PlayerCommon(TestCase, TestUtils):

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

    def tearDown(self):
        mock.patch.stopall()


class PlayerTestCase(PlayerCommon):
    """Tests for Player class
    """

    def setUp(self):
        super().setUp()
        self.player = Player(self.mock_board, Piece.BLACK)

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


class OpponentTestCase(PlayerCommon):
    """Tests for Opponent class
    """

    def setUp(self):
        super().setUp()
        self.opponent = Opponent(self.mock_board, Piece.WHITE)

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
        black_pos = [(1, 0), (3, 2), (1, 7), (0, 2), (0, 3), (4, 0)]
        white_pos = [(0, 7), (7, 6), (6, 6), (4, 3), (7, 4), (4, 7)]
        disks = self.get_disks(black_pos, white_pos, Piece.BLACK, Piece.WHITE)

        tests = [
            [Piece.BLACK, (2, 3)],
            [Piece.WHITE, (3, 2)]
        ]
        for color, expect in tests:
            with self.subTest(color):
                self.opponent.color = color
                result = self.opponent.counter(disks, self.opponent._sides)
                self.assertEqual(result, expect)

    def test_copy_currnet_board(self):
        result = self.opponent.copy_current_board()

        for r in range(8):
            for c in range(8):
                with self.subTest((r, c)):
                    if item := self.opponent.board.disks[r][c]:
                        self.assertEqual(item.color, result[r][c])
                    else:
                        self.assertTrue(result[r][c] is None)

    def test_simulate(self):
        white_pos = [(0, 4), (1, 4), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (4, 2), (5, 1)]
        black_pos = [(3, 2), (3, 3), (3, 4), (4, 3), (4, 4), (4, 5), (5, 5), (6, 5)]
        disks = self.get_disks(black_pos, white_pos, Piece.BLACK, Piece.WHITE)
        tests = [Piece.BLACK, Piece.WHITE]
        expects = [(0, 4, 1), (0, 1, 0)]

        for test, expect in zip(tests, expects):
            with self.subTest():
                result = self.opponent.simulate(disks, test)
                self.assertEqual(result, expect)

    def test_evaluate(self):
        white_pos = [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)]
        black_pos = [(0, 5), (1, 2), (1, 3), (1, 4), (2, 2), (2, 3), (3, 2), (3, 3)]
        disks = self.get_disks(black_pos, white_pos, Piece.BLACK, Piece.WHITE)
        result = self.opponent.evaluate(disks)
        self.assertEqual(result, 34)

    def test_find_best_move(self):
        grids = [(2, 4), (4, 1)]
        disks = self.get_disks([], [])
        expect = [
            Candidate(evaluation=10, row=2, col=4, corners=1, arounds=2, sides=3),
            Candidate(evaluation=20, row=4, col=1, corners=4, arounds=5, sides=6)
        ]

        def find_reversibles(li):
            for r, c in li:
                yield (r, c)

        with mock.patch('othello.GameLogic.find_reversibles') as mock_find, \
                mock.patch('othello.Opponent.evaluate') as mock_evaluate, \
                mock.patch('othello.Opponent.simulate') as mock_simulate:
            mock_find.side_effect = [find_reversibles([(3, 4), (4, 4)]), find_reversibles([(4, 2), (4, 3)])]
            mock_evaluate.side_effect = [10, 20]
            mock_simulate.side_effect = [(1, 2, 3), (4, 5, 6)]
            result = [cand for cand in self.opponent.find_best_move(grids, disks, Piece.WHITE)]
            self.assertEqual(result, expect)

    def test_guess_choice(self):
        cands = [Candidate(0, 2, 4, 0, 0, 0), Candidate(0, 3, 4, 0, 0, 0), Candidate(0, 3, 5, 0, 0, 0)]

        with mock.patch('othello.Opponent.find_best_move') as mock_best_move, \
                mock.patch('othello.random.choice') as mock_choice:
            mock_best_move.return_value = self.find_best_move(cands)
            mock_choice.return_value = cands[1]
            result = self.opponent.guess(mock.MagicMock(), mock.MagicMock())
            mock_choice.assert_called_once()
            self.assertEqual(result, (3, 4))

    def test_guess(self):
        tests = [
            [Candidate(10, 2, 4, 0, 0, 0), Candidate(20, 3, 4, 0, 3, 0), Candidate(20, 3, 5, 0, 2, 0)],
            [Candidate(10, 2, 4, 0, 3, 5), Candidate(10, 3, 4, 0, 2, 5), Candidate(10, 3, 5, 0, 1, 5)],
            [Candidate(10, 2, 4, 0, 0, 0), Candidate(20, 3, 4, 0, 0, 0), Candidate(30, 3, 5, 0, 0, 0)],
            [Candidate(10, 2, 4, 0, 0, 1), Candidate(30, 3, 4, 0, 0, 5), Candidate(30, 3, 5, 0, 0, 4)],
            [Candidate(30, 2, 4, 1, 3, 0), Candidate(30, 3, 4, 1, 2, 0), Candidate(30, 3, 5, 2, 0, 0)],
            [Candidate(30, 2, 4, 1, 3, 2), Candidate(30, 3, 4, 1, 3, 1), Candidate(30, 3, 5, 1, 2, 1)],
            [Candidate(20, 2, 4, 1, 0, 0), Candidate(30, 3, 4, 2, 0, 0), Candidate(30, 3, 5, 1, 0, 0)],
            [Candidate(20, 2, 4, 2, 0, 1), Candidate(20, 3, 4, 2, 0, 2), Candidate(10, 3, 5, 1, 0, 1)]
        ]
        expects = [(3, 4), (2, 4), (3, 5), (3, 5), (2, 4), (3, 4), (3, 5), (2, 4)]

        with mock.patch('othello.Opponent.find_best_move') as mock_best_move:
            for test, expect in zip(tests, expects):
                with self.subTest(test):
                    mock_best_move.return_value = self.find_best_move(test)
                    result = self.opponent.guess(mock.MagicMock(), mock.MagicMock())
                    self.assertEqual(result, (expect))

    def test_place_corner(self):
        positions = [(0, 0), (0, 7)]

        with mock.patch('othello.Opponent.get_placeables') as mock_placeables, \
                mock.patch('othello.Opponent.guess') as mock_guess, \
                mock.patch('othello.Players.click') as mock_click:
            mock_placeables.return_value = self.get_placeables(positions)
            self.opponent.place()
            mock_click.assert_called_once_with(*positions[0])
            mock_guess.assert_not_called()

    def test_place_filtered(self):
        black_pos = [(2, 2), (3, 3), (3, 4), (4, 4)]
        white_pos = [(4, 3), (5, 3), (5, 4), (5, 5)]
        disks = self.get_disks(
            black_pos, white_pos, Piece.BLACK, Piece.WHITE)
        positions = [(0, 1), (1, 0), (2, 3), (3, 4), (4, 5)]
        filtered = [(2, 3), (3, 4), (4, 5)]
        guessed = (1, 3)

        with mock.patch('othello.Opponent.get_placeables') as mock_placeables, \
                mock.patch('othello.Opponent.guess') as mock_guess, \
                mock.patch('othello.Players.click') as mock_click:
            mock_placeables.return_value = self.get_placeables(positions)
            mock_guess.return_value = guessed
            self.opponent.place()

            mock_placeables.assert_called_once_with(disks, Piece.WHITE)
            mock_guess.assert_called_once_with(filtered, disks)
            mock_click.assert_called_once_with(*guessed)

    def test_place_no_filtered(self):
        black_pos = [(2, 2), (3, 3), (3, 4), (4, 4)]
        white_pos = [(4, 3), (5, 3), (5, 4), (5, 5)]
        disks = self.get_disks(
            black_pos, white_pos, Piece.BLACK, Piece.WHITE)
        positions = [(0, 1), (1, 0), (1, 1)]
        guessed = (1, 3)

        with mock.patch('othello.Opponent.get_placeables') as mock_placeables, \
                mock.patch('othello.Opponent.guess') as mock_guess, \
                mock.patch('othello.Players.click') as mock_click:
            mock_placeables.return_value = self.get_placeables(positions)
            mock_guess.return_value = guessed
            self.opponent.place()

            mock_placeables.assert_called_once_with(disks, Piece.WHITE)
            mock_guess.assert_called_once_with(positions, disks)
            mock_click.assert_called_once_with(*guessed)


if __name__ == '__main__':
    main()