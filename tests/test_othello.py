import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
import pygame
from pygame.locals import *
from unittest import TestCase, main, mock

from othello import Board, Cursor, Disk, Piece, Player, \
    Othello, Opponent, Status, Images, Point


class TestUtils:

    def get_disk(self, color):
        disk = mock.create_autospec(
            spec=Disk,
            instance=True,
            color=color)
        return disk

    def reset_mocks(self, *mocks):
        for m in mocks:
            m.reset_mock()


class OthelloTestCase(TestCase, TestUtils):

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
            'othello.Players.create_sounds',
            'othello.pygame.time.Clock'
        ]
        for target in targets:
            mock.patch(target).start()

        mock.patch('othello.pygame.USEREVENT', 0).start()
        self.othello = Othello()

    def tearDown(self):
        mock.patch.stopall()

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

    def test_place_disk(self):
        with mock.patch('othello.Opponent.place') as mock_place, \
                mock.patch('othello.Othello.set_timer') as mock_timer:
            self.othello.place_disk()
            mock_place.assert_called_once()
            mock_timer.assert_called_once_with(1)

    def test_reverse_disks(self):
        tests = [
            [True, 2],
            [False, 5]
        ]
        with mock.patch('othello.Players.reverse') as mock_reverse, \
                mock.patch('othello.Othello.calc_score') as mock_calc, \
                mock.patch('othello.Othello.set_timer') as mock_timer:
            for test, expect in tests:
                with self.subTest():
                    mock_calc.return_value = test
                    self.othello.reverse_disks()
                    mock_reverse.assert_called_once()
                    mock_timer.assert_called_once_with(expect)
                    self.reset_mocks(mock_reverse, mock_calc, mock_timer)

    def test_pass_turn(self):
        self.othello.board.status = Status.PASS

        with mock.patch('othello.Othello.set_timer') as mock_timer:
            self.othello.pass_turn()
            self.assertEqual(self.othello.board.status, Status.PLAY)
            mock_timer.assert_called_once_with(2)

    def test_take_turns(self):
        tests = [
            [(True, False), Images.WHITE_DISPLAY],
            [(False, True), Images.BLACK_DISPLAY]
        ]
        with mock.patch('othello.Board.set_turn') as mock_turn, \
                mock.patch('othello.Othello.set_timer') as mock_timer:
            for (player, opponent), expect in tests:
                with self.subTest((player, opponent)):
                    self.othello.player.turn = player
                    self.othello.opponent.turn = opponent
                    self.othello.take_turns()
                    mock_turn.assert_called_once_with(expect)
                    mock_timer.assert_called_once_with(3)
                    self.reset_mocks(mock_turn, mock_timer)

    def test_guess_placeable_set_timer(self):
        self.othello.player.turn = False
        self.othello.opponent.turn = True
        self.othello.board.status = Status.PLAY

        effects = [[True], [False, False], [False, True]]
        expects = [0, 5, 4]

        with mock.patch('othello.GameLogic.has_placeables') as mock_placeables, \
                mock.patch('othello.Othello.set_timer') as mock_timer:
            for i, (effect, expect) in enumerate(zip(effects, expects)):
                with self.subTest(effect):
                    mock_placeables.side_effect = effect
                    self.othello.guess_placeable()
                    mock_timer.assert_called_once_with(expect)
                    if i == len(effects) - 1:
                        self.assertEqual(self.othello.board.status, Status.PASS)
                    self.reset_mocks(mock_placeables, mock_timer)

    def test_guess_placeable_not_set_timer(self):
        self.othello.player.turn = True
        self.othello.opponent.turn = False
        self.othello.board.status = Status.PLAY

        with mock.patch('othello.GameLogic.has_placeables') as mock_placeables, \
                mock.patch('othello.Othello.set_timer') as mock_timer:
            mock_placeables.return_value = True
            self.othello.guess_placeable()
            mock_timer.assert_not_called()

    def test_game_over_draw(self):
        self.othello.board.status = self.othello.status = Status.PLAY
        self.othello.board.black_score = self.othello.board.white_score = 32

        with mock.patch('othello.Board.set_turn') as mock_turn:
            self.othello.game_over()
            self.assertEqual(self.othello.board.status, Status.DRAW)
            self.assertEqual(self.othello.status, Status.GAMEOVER)
            mock_turn.assert_not_called()

    def test_game_over_win(self):
        scores = [[40, 24], [24, 40]]
        expects = [Images.BLACK_DISPLAY, Images.WHITE_DISPLAY]

        with mock.patch('othello.Board.set_turn') as mock_turn:
            for (black, white), expect in zip(scores, expects):
                with self.subTest((black, white)):
                    self.othello.board.status = self.othello.status = Status.PLAY
                    self.othello.board.black_score = black
                    self.othello.board.white_score = white
                    self.othello.game_over()
                    self.assertEqual(self.othello.board.status, Status.WIN)
                    self.assertEqual(self.othello.status, Status.GAMEOVER)
                    mock_turn.assert_called_once_with(expect)
                    mock_turn.reset_mock()


if __name__ == '__main__':
    main()