"""Synthetic guard patrol tests; never open a terminal or puzzle input."""

import importlib.util
import random
import sys
import types
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import patch

from bruhanimate import Buffer, Playback


def load(name="test_2024_day06", filename="animate.py"):
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).with_name(filename)
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


animation = load()


def oracle(rows, start, heading, obstacle=None):
    """Independent finite-state simulator using a direction dictionary."""
    movement = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}
    x, y = start
    visited, states = set(), set()
    while True:
        if (x, y, heading) in states:
            return visited, True
        states.add((x, y, heading))
        visited.add((x, y))
        dx, dy = movement[heading]
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= len(rows[0]) or ny >= len(rows):
            return visited, False
        if rows[ny][nx] == "#" or (nx, ny) == obstacle:
            heading = (heading + 1) % 4
        else:
            x, y = nx, ny


class GuardTests(unittest.TestCase):
    def test_import_is_inert(self):
        with (
            patch("pathlib.Path.read_text", side_effect=AssertionError("input read")),
            patch(
                "bruhanimate.Screen.open", side_effect=AssertionError("terminal opened")
            ),
        ):
            load("day06_animate")

    def test_validation(self):
        for text in ("", "...", "^\n..", "^^", "^x", "^\n\n."):
            with self.subTest(text=text), self.assertRaises(ValueError):
                animation.parse(text)
        for part in (0, 3):
            with self.assertRaises(ValueError):
                list(animation.snapshots(animation.parse("^"), part))

    def test_all_initial_headings(self):
        for char in "^>v<":
            board = animation.parse(f"...\n.{char}.\n...")
            result = list(animation.snapshots(board, 1))[-1]
            self.assertEqual(result.answer, 2)
            self.assertTrue(result.patrol.exited)

    def test_guard_on_boundary_and_blocked_rotations(self):
        self.assertEqual(
            list(animation.snapshots(animation.parse("^"), 1))[-1].answer, 1
        )
        board = animation.parse("###\n#^#\n###")
        states = list(animation.snapshots(board, 1))
        self.assertTrue(states[-1].patrol.looped)
        self.assertEqual(states[-1].answer, 1)
        self.assertLess(len(states), 10)

    def test_looping_baseline_tests_unvisited_floor(self):
        board = animation.parse("#####\n#^###\n#####\n#...#\n#####")
        final = list(animation.snapshots(board))[-1]
        self.assertEqual(final.candidates, 3)
        self.assertEqual(final.answer, 3)

    def test_random_boards_match_exhaustive_placement_oracle(self):
        rng = random.Random(6006)
        for _ in range(80):
            width, height = rng.randrange(2, 7), rng.randrange(2, 7)
            start = rng.randrange(width), rng.randrange(height)
            heading = rng.randrange(4)
            rows = [
                ["#" if rng.random() < 0.28 else "." for _ in range(width)]
                for _ in range(height)
            ]
            rows[start[1]][start[0]] = "^>v<"[heading]
            board = animation.parse("\n".join("".join(row) for row in rows))
            visited, _ = oracle(board.rows, start, heading)
            self.assertEqual(
                list(animation.snapshots(board, 1))[-1].answer, len(visited)
            )
            expected = {
                (x, y)
                for y, row in enumerate(board.rows)
                for x, char in enumerate(row)
                if char == "."
                and (x, y) != start
                and oracle(board.rows, start, heading, (x, y))[1]
            }
            self.assertEqual(list(animation.snapshots(board, 2))[-1].loops, expected)

    def test_detailed_and_compact_have_identical_answers(self):
        board = animation.parse(".....\n.#.#.\n..^#.\n.#...\n.....")
        compact = list(animation.snapshots(board))
        detailed = list(animation.snapshots(board, show_steps=True))
        self.assertEqual(compact[-1], detailed[-1])
        self.assertGreater(len(detailed), len(compact))

    def test_immutable_lazy_snapshots_and_pure_clipped_draw(self):
        source = animation.snapshots(animation.parse("....\n.^#.\n...."), 1)
        first = next(source)
        later = next(source)
        with self.assertRaises(FrozenInstanceError):
            first.phase = "changed"
        self.assertEqual(first.patrol.visited, {(1, 1)})
        for height, width in ((1, 1), (4, 3), (20, 60)):
            left, right = Buffer(height, width), Buffer(height, width)
            animation.draw(later, left)
            animation.draw(later, right)
            self.assertEqual(
                [[left.get_char(x, y) for x in range(width)] for y in range(height)],
                [[right.get_char(x, y) for x in range(width)] for y in range(height)],
            )
        source.close()

    def test_playback_pause_step_completion(self):
        player = Playback(
            animation.snapshots(animation.parse("^"), 1),
            animation.draw,
            steps_per_second=10,
        )
        player.start()
        player.update(0)
        original = player.state
        player.pause()
        player.update(10)
        self.assertIs(player.state, original)
        player.step()
        player.update(0)
        self.assertIsNot(player.state, original)
        player.resume()
        for _ in range(20):
            player.update(0.1)
        self.assertTrue(player.finished)
        self.assertEqual(player.state.answer, 1)
        player.close()
        player.close()

    def test_main_anchors_default_and_supplies_common_options(self):
        with (
            patch("pathlib.Path.read_text", return_value="^"),
            patch.object(animation, "run_animation", return_value=7) as run,
        ):
            self.assertEqual(animation.main(["--no-background", "--frames", "2"]), 7)
            self.assertFalse(run.call_args.kwargs["background"])
            self.assertEqual(run.call_args.kwargs["frames"], 2)
        parser = animation.argument_parser("test", animation.__file__, "datasmall")
        self.assertEqual(
            parser.parse_args([]).input, Path(animation.__file__).with_name("datasmall")
        )

    def test_legacy_command_resolves_sibling_after_other_animate_import(self):
        other = types.ModuleType("animate")
        other.main = lambda argv: self.fail("Imported an unrelated animate module")
        with (
            patch.dict(sys.modules, {"animate": other}),
            patch("pathlib.Path.read_text", side_effect=AssertionError("input read")),
            patch(
                "bruhanimate.Screen.open", side_effect=AssertionError("terminal opened")
            ),
        ):
            forwarding = load("test_day06_forward", "animated.py")
            with self.assertRaises(SystemExit) as caught:
                forwarding.main(["--help"])
            self.assertEqual(caught.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
