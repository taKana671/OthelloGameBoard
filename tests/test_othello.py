import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
import pygame
from pygame.locals import *
from unittest import TestCase, main, mock

from othello import Board, Cursor, Disk, Piece, Player, \
    Othello, Opponent, Status, Images, Point


class OthelloTestCase(TestCase):

    def setUp(self):
        targets = [
            'othello.pygame.init',
            'othello.pygame.display.set_mode',
            'othello.pygame.display.set_caption',
            'othello.pygame.sprite.RenderUpdates',
            'othello.pygame.sprite.GroupSingle',
            'othello.Board.set_displays',
            'othello.pygame.image.load',
            'othello.pygame.transform.scale',
            'othello.Players.create_sounds'
        ]
        for target in targets:
            mock.patch(target).start()

        mock.patch('othello.pygame.USEREVENT', 0).start()
        self.othello = Othello()

    def tearDown(self):
        mock.patch.stopall()

    def get_disk(self, color):
        disk = mock.create_autospec(
            spec=Disk,
            instance=True,
            color=color)
        return disk

    def test_calc_score_true(self):
        for r, c in [(2, 3), (3, 5), (3, 6)]:
            self.othello.disks[r][c] = self.get_disk(Piece.BLACK)
        for r, c in [(0, 1), (0, 2), (0, 3), (7, 0)]:
            self.othello.disks[r][c] = self.get_disk(Piece.WHITE)

        with mock.patch('othello.Board.set_score') as mock_set:
            result = self.othello.calc_score()
            mock_set.assert_called_once_with(3, 4)
            self.assertEqual(result, True)

    def test_calc_score_false(self):
        for r in range(8):
            for c in range(8):
                if r <= 3:
                    self.othello.disks[r][c] = self.get_disk(Piece.BLACK)
                else:
                    self.othello.disks[r][c] = self.get_disk(Piece.WHITE)

        with mock.patch('othello.Board.set_score') as mock_set:
            result = self.othello.calc_score()
            mock_set.assert_called_once_with(32, 32)
            self.assertEqual(result, False)

    def test_change_first_player(self):
        calls = [mock.call(Piece.WHITE), mock.call(Piece.BLACK)]

        with mock.patch('othello.Players.set_color') as mock_set:
            self.othello.change_first_player()
            self.assertEqual(mock_set.call_args_list, calls)

    def test_start(self):
        self.othello.timer = 10
        self.othello.status = Status.GAMEOVER

        with mock.patch('othello.Board.setup') as mock_setup, \
                mock.patch('othello.Board.set_turn') as mock_setturn:
            self.othello.start()
            self.assertEqual(self.othello.status, Status.PLAY)
            self.assertEqual(self.othello.timer, 0)
            mock_setup.assert_called_once()
            mock_setturn.assert_called_once_with(Images.BLACK_DISPLAY)

    def test_set_timer(self):
        event = mock.MagicMock()
        self.othello.status = Status.PLAY

        with mock.patch('othello.pygame.event.Event') as mock_event:
            self.othello.set_timer(event, 10)
            self.assertEqual(self.othello.status, Status.SET_TIMER)
            self.assertEqual(self.othello.timer, 10)
            mock_event.assert_called_once_with(event)

    def test_current_player(self):
        tests = [
            [True, self.othello.player],
            [False, self.othello.opponent],
        ]
        for test, expect in tests:
            self.othello.player.turn = test
            self.assertEqual(self.othello.current_player, expect)

    def test_next_player(self):
        tests = [
            [True, self.othello.opponent],
            [False, self.othello.player],
        ]
        for test, expect in tests:
            self.othello.player.turn = test
            self.assertEqual(self.othello.next_player, expect)

    def test_player_click(self):
        self.othello.player.turn = True
        self.othello.cursor.visible = True

        with mock.patch('othello.GameLogic.has_placeables') as mock_placeables, \
                mock.patch('othello.Player.place') as mock_place, \
                mock.patch('othello.Othello.set_timer') as mock_timer:
            mock_placeables.return_value = True
            mock_place.return_value = True
            self.othello.player_click((250, 150))
            mock_placeables.assert_called_once_with(self.othello.disks, Piece.BLACK)
            mock_place.assert_called_once_with(Point(250, 150))
            mock_timer.assert_called_once_with(1)

    def test_player_not_click_1(self):
        self.othello.player.turn = True
        self.othello.cursor.visible = False

        with mock.patch('othello.GameLogic.has_placeables') as mock_placeables, \
                mock.patch('othello.Player.place') as mock_place, \
                mock.patch('othello.Othello.set_timer') as mock_timer:
            self.othello.player_click((250, 150))
            mock_placeables.assert_not_called()
            mock_place.assert_not_called()
            mock_timer.assert_not_called()

    def test_player_not_click_2(self):
        self.othello.player.turn = True
        self.othello.cursor.visible = True

        with mock.patch('othello.GameLogic.has_placeables') as mock_placeables, \
                mock.patch('othello.Player.place') as mock_place, \
                mock.patch('othello.Othello.set_timer') as mock_timer:
            mock_placeables.return_value = False
            self.othello.player_click((250, 150))
            mock_placeables.assert_called_once_with(self.othello.disks, Piece.BLACK)
            mock_place.assert_not_called()
            mock_timer.assert_not_called()

    def test_player_not_click_3(self):
        self.othello.player.turn = True
        self.othello.cursor.visible = True

        with mock.patch('othello.GameLogic.has_placeables') as mock_placeables, \
                mock.patch('othello.Player.place') as mock_place, \
                mock.patch('othello.Othello.set_timer') as mock_timer:
            mock_placeables.return_value = True
            mock_place.return_value = False
            self.othello.player_click((250, 150))
            mock_placeables.assert_called_once_with(self.othello.disks, Piece.BLACK)
            mock_place.assert_called_once_with(Point(250, 150))
            mock_timer.assert_not_called()


if __name__ == '__main__':
    main()