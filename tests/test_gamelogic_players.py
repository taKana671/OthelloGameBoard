import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from pygame.locals import *
from unittest import TestCase, main, mock

from othello import Board, GameLogic, Piece, Disk


class GameLogicTestCase(TestCase):
    """Tests for Board class
    """

    def setUp(self):
        self.game_logic = GameLogic()
        self.piece_disks = self.get_disks(Piece.BLACK, Piece.WHITE)
        self.sprite_disks = self.get_disks(
            self.get_disk_instance(Piece.BLACK), self.get_disk_instance(Piece.WHITE))

    def get_disks(self, black, white):
        black_pos = [(2, 2), (3, 3), (3, 4), (4, 4)]
        white_pos = [(4, 3), (5, 3), (5, 4), (5, 5)]
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

    def get_gameover_disks(self, black, white):
        disks = [[white for _ in range(8)] for _ in range(8)]
        disks[0][0] = None
        for r, c in [(0, 1), (1, 0), (1, 1)]:
            disks[r][c] = black
        return disks

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


if __name__ == '__main__':
    main()