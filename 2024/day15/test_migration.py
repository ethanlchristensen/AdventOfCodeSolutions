"""Synthetic warehouse checks; never read a puzzle input or open a terminal."""

import importlib.util
import random
import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import animate as animation  # noqa: E402
from bruhanimate import Buffer  # noqa: E402

SMALL = "#####\n#@O.#\n#...#\n#####\n\n>v<^\n"


def reference(rows, moves, part):
    """Independent mutable cell-grid oracle, including both box halves."""
    mapping = {"#": "##", "O": "[]", ".": "..", "@": "@."}
    grid = [
        list("".join(mapping[c] for c in row) if part == 2 else row) for row in rows
    ]
    width, height = len(grid[0]), len(grid)
    for move in moves:
        robot = next(
            (x, y) for y, row in enumerate(grid) for x, c in enumerate(row) if c == "@"
        )
        dx, dy = animation.DIRECTIONS[move]
        cells = set()

        def collect(x, y):
            if not (0 <= x < width and 0 <= y < height) or grid[y][x] == "#":
                return False
            if grid[y][x] == "." or (x, y) in cells:
                return True
            cells.add((x, y))
            if grid[y][x] in "[]":
                mate = x + (1 if grid[y][x] == "[" else -1)
                if not collect(mate, y):
                    return False
            return collect(x + dx, y + dy)

        if collect(*robot):
            original = [row[:] for row in grid]
            for x, y in cells:
                grid[y][x] = "."
            for x, y in cells:
                grid[y + dy][x + dx] = original[y][x]
        yield tuple("".join(row) for row in grid)


def render_board(board):
    rows = [["."] * board.width for _ in range(board.height)]
    for x, y in board.walls:
        rows[y][x] = "#"
    for x, y in board.boxes:
        rows[y][x] = "O" if board.box_width == 1 else "["
        if board.box_width == 2:
            rows[y][x + 1] = "]"
    rows[board.robot[1]][board.robot[0]] = "@"
    return tuple("".join(row) for row in rows)


class WarehouseTests(unittest.TestCase):
    def test_multiline_moves_are_not_truncated(self):
        rows, moves = animation.parse("#####\n#@O.#\n#####\n\n>\n >\t<\n^ v\n")
        self.assertEqual(moves, ">><^v")
        for part in (1, 2):
            states = list(animation.snapshots((rows, moves), part))
            self.assertEqual(states[-1].index, 5)
            self.assertEqual(len(states), 7)

    def test_validation(self):
        for text in (
            "",
            "@",
            "\n@\n\n>",
            "##\n@\n\n>",
            "@@\n\n>",
            ".\n\n>",
            "@X\n\n>",
            "@\n\nR",
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                animation.parse(text)

    def test_small_known_scores_and_completion(self):
        parsed = animation.parse(SMALL)
        self.assertEqual(list(animation.snapshots(parsed, 1))[-1].warehouse.score, 103)
        self.assertEqual(list(animation.snapshots(parsed, 2))[-1].warehouse.score, 104)
        empty = list(animation.snapshots(animation.parse("@.\n\n"), 1))
        self.assertEqual([s.phase for s in empty], ["ready", "complete"])

    def test_open_edges_block_without_negative_wraparound(self):
        states = list(animation.snapshots(animation.parse("@O\n\n<^^>"), 1))
        self.assertTrue(all(s.warehouse.robot == (0, 0) for s in states))
        self.assertEqual(states[-1].failures, 4)

    def test_horizontal_wide_chain_and_part_scaling(self):
        parsed = animation.parse("########\n#@OO...#\n########\n\n>>>>")
        narrow = list(animation.snapshots(parsed, 1))[-1].warehouse
        wide = list(animation.snapshots(parsed, 2))[-1].warehouse
        self.assertEqual(narrow.boxes, frozenset(((5, 1), (6, 1))))
        self.assertEqual(wide.boxes, frozenset(((7, 1), (9, 1))))
        self.assertEqual((narrow.width, wide.width), (8, 16))

    def fanout(self):
        walls = frozenset(
            (x, y) for y in range(6) for x in range(9) if x in (0, 8) or y in (0, 5)
        )
        return animation.Warehouse(
            9, 6, walls, frozenset(((3, 3), (2, 2), (4, 2))), (3, 4), 2
        )

    def test_vertical_wide_push_fans_out_atomically(self):
        board = self.fanout()
        result, pushed, blocked = animation.attempt(board, "^")
        self.assertFalse(blocked)
        self.assertEqual(result.robot, (3, 3))
        self.assertEqual(result.boxes, frozenset(((3, 2), (2, 1), (4, 1))))
        self.assertEqual(pushed, result.boxes)
        self.assertEqual(board.boxes, frozenset(((3, 3), (2, 2), (4, 2))))

    def test_one_blocked_fanout_branch_cancels_every_box(self):
        board = replace(self.fanout(), walls=self.fanout().walls | {(5, 1)})
        result, pushed, blocked = animation.attempt(board, "^")
        self.assertIs(result, board)
        self.assertEqual(pushed, board.boxes)
        self.assertEqual(blocked, frozenset(((5, 1),)))

    def test_random_sequences_match_cell_grid_reference_and_preserve_invariants(self):
        rows = (
            "#########",
            "#..O....#",
            "#.OO.O..#",
            "#...@...#",
            "#.O.O...#",
            "#.......#",
            "#########",
        )
        randomizer = random.Random(15)
        for part in (1, 2):
            for _ in range(5):
                moves = "".join(randomizer.choice("<>^v") for _ in range(200))
                states = animation.snapshots((rows, moves), part)
                initial = next(states).warehouse
                for state, expected in zip(
                    states, reference(rows, moves, part), strict=False
                ):
                    board = state.warehouse
                    self.assertEqual(render_board(board), expected)
                    self.assertEqual(board.walls, initial.walls)
                    self.assertEqual(len(board.boxes), len(initial.boxes))
                    self.assertEqual(len(board.occupancy()), len(board.boxes) * part)
                    self.assertFalse(board.walls & board.occupancy().keys())
                    self.assertNotIn(board.robot, board.occupancy())

    def test_snapshots_frozen_lazy_and_bounded_trail(self):
        parsed = animation.parse("######\n#@...#\n######\n\n" + "><" * 100)
        states = animation.snapshots(parsed, 1)
        with patch.object(animation, "attempt", wraps=animation.attempt) as attempt:
            first = next(states)
            attempt.assert_not_called()
            with self.assertRaises(FrozenInstanceError):
                first.index = 2
            next(states)
            self.assertEqual(attempt.call_count, 1)
        final = list(states)[-1]
        self.assertLessEqual(len(final.trail), 16)
        self.assertEqual(first.warehouse.robot, (1, 1))

    def test_draw_is_pure_and_clipped_including_small_buffers(self):
        state = list(animation.snapshots(animation.parse(SMALL), 2))[2]
        before = hash(state)
        for height, width in ((1, 1), (4, 2), (8, 4), (20, 60)):
            left, right = Buffer(height, width), Buffer(height, width)
            animation.draw(left, state)
            animation.draw(right, state)
            self.assertEqual(left.buffer, right.buffer)
            self.assertEqual(len(left.buffer), height)
            self.assertTrue(all(len(row) == width for row in left.buffer))
        self.assertEqual(hash(state), before)

    def test_import_legacy_cli_name_is_inert(self):
        spec = importlib.util.spec_from_file_location(
            "day15_animate", animation.__file__
        )
        module = importlib.util.module_from_spec(spec)
        with (
            patch.dict(sys.modules, {spec.name: module}),
            patch.object(Path, "read_text", side_effect=AssertionError("input read")),
            patch(
                "animation_support.play", side_effect=AssertionError("terminal opened")
            ),
        ):
            spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))

    def test_following_camera_keeps_robot_visible_and_headers_clear(self):
        board = animation.Warehouse(80, 40, frozenset(), frozenset(), (75, 35), 2)
        state = animation.Snapshot(board, "ready", 0, 0, "")
        buffer = Buffer(12, 20)
        animation.draw(buffer, state)
        self.assertTrue(
            any(animation.ink("@", 51) in row for row in buffer.buffer[3:10])
        )
        self.assertEqual(buffer.buffer[:2], [[" "] * 20, [" "] * 20])
        self.assertEqual(buffer.buffer[-1], [" "] * 20)

    def test_default_input_is_beside_script(self):
        parser = animation.argument_parser("test", animation.__file__, "datasmall4")
        self.assertEqual(
            parser.parse_args([]).input,
            Path(animation.__file__).resolve().with_name("datasmall4"),
        )

    def test_main_anchors_default_and_delegates_to_shared_player(self):
        with (
            patch.object(Path, "read_text", return_value=SMALL) as read,
            patch.object(animation, "run_animation", return_value=123) as run,
        ):
            self.assertEqual(
                animation.main(
                    ["--part", "1", "--no-background", "--exit-on-complete"]
                ),
                123,
            )
        read.assert_called_once_with(encoding="utf-8")
        args, options = run.call_args
        self.assertEqual(list(args[0])[-1].warehouse.box_width, 1)
        self.assertFalse(options["background"])
        self.assertEqual(options["on_complete"], "exit")

    def test_real_main_player_draw_completion_and_cleanup(self):
        from bruhanimate import Screen

        player_module = importlib.import_module("bruhanimate.player")
        real_player = player_module.Player
        source = animation.snapshots
        original_draw = animation.draw
        closed, phases = [], []

        class ScreenStub:
            width, height = 50, 15

            def __init__(self):
                self.batches = self.closes = 0

            def get_event(self):
                return None

            def has_resized(self):
                return False

            def begin_frame(self):
                pass

            def flush_frame(self):
                self.batches += 1

            def print_at(self, text, x, y, width):
                pass

            def close(self):
                self.closes += 1

        class Clock:
            now = 0.0

            def __call__(self):
                return self.now

            def sleep(self, seconds):
                self.now += seconds

        def tracked_source(*args, **kwargs):
            try:
                yield from source(*args, **kwargs)
            finally:
                closed.append(True)

        def tracked_draw(buffer, state):
            phases.append(state.phase)
            original_draw(buffer, state)

        screen, clock = ScreenStub(), Clock()

        def make_player(*args, **kwargs):
            return real_player(*args, **kwargs, clock=clock, sleep=clock.sleep)

        with (
            patch.object(Path, "read_text", return_value=SMALL),
            patch.object(Screen, "open", return_value=screen),
            patch.object(player_module, "Player", side_effect=make_player),
            patch.object(animation, "snapshots", side_effect=tracked_source),
            patch.object(animation, "draw", side_effect=tracked_draw),
        ):
            frames = animation.main(
                [
                    "--no-background",
                    "--exit-on-complete",
                    "--frames",
                    "100",
                    "--steps-per-second",
                    "60",
                ]
            )
        self.assertGreater(frames, 1)
        self.assertLess(frames, 100)
        self.assertEqual(screen.batches, frames)
        self.assertEqual(screen.closes, 1)
        self.assertEqual(closed, [True])
        self.assertIn("complete", phases)


if __name__ == "__main__":
    unittest.main()
