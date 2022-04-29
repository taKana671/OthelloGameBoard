import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from pygame.locals import *
from unittest import TestCase, main, mock

from othello import Board, Othello, Piece, Status


class BoardTestCase(TestCase):
    """Tests for Board class
    """

    def setUp(self):
        mock.patch('othello.Board.set_displays').start()
        self.disks = [[None for _ in range(8)] for _ in range(8)]
        self.game = mock.create_autospec(
            spec=Othello,
            instance=True,
            disks=self.disks
        )
        self.board = Board(self.game, mock.MagicMock())

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
        mock_disk = mock.MagicMock()
        mock_disk.kill.return_value = None
        disk_pos = [(1, 3), (2, 6), (3, 5), (3, 6), (5, 7), (6, 6)]

        for r, c in disk_pos:
            self.game.disks[r][c] = mock_disk

        self.board.clear()
        self.assertEqual(mock_disk.kill.call_count, len(disk_pos))

    def test_draw_backgrond(self):
        screen = mock.Mock()
        calls = [
            mock.call(screen, (76, 38, 0), (200, 50, 600, 600)),
            mock.call(screen, (0, 100, 0), (220, 70, 560, 560)),
        ]

        with mock.patch('othello.pygame.draw.rect') as mock_draw:
            self.board.draw_background(screen)
            mock_draw.assert_has_calls(calls)


if __name__ == '__main__':
    main()