"""Synthetic height-map tests; no terminals or puzzle inputs."""

import importlib.util
import random
import re
import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import patch

from bruhanimate import Buffer, Playback


def load(name="test_2024_day10"):
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).with_name("animate.py")
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


animation = load()


def oracle(rows):
    """Independently enumerate short synthetic trails, keeping endpoint repeats."""
    score = rating = 0
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char != "0":
                continue
            endpoints = []

            def walk(x, y, height):
                if height == 9:
                    endpoints.append((x, y))
                    return
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if (
                        0 <= ny < len(rows)
                        and 0 <= nx < len(rows[0])
                        and rows[ny][nx] == str(height + 1)
                    ):
                        walk(nx, ny, height + 1)

            walk(x, y, 0)
            score += len(set(endpoints))
            rating += len(endpoints)
    return score, rating


class TrailTests(unittest.TestCase):
    def test_cursor_stays_boxed_and_visible_during_counting_and_trailhead_views(self):
        states = list(animation.snapshots(animation.parse("0123456789\n1234567899")))
        counting = next(state for state in states if state.processed == 1)
        trailhead = next(state for state in states if state.phase == "trailhead")
        ansi = re.compile(r"\x1b\[[0-9;]*m")
        for state in (counting, trailhead, states[-1]):
            buffer = Buffer(24, 80)
            animation.draw(state, buffer)
            cursor = [
                (x, y, cell)
                for y, row in enumerate(buffer.buffer)
                for x, cell in enumerate(row)
                if "48;5;" in cell
            ]
            self.assertEqual(len(cursor), 1)
            x, y, cell = cursor[0]
            self.assertEqual(
                ansi.sub("", cell), state.rows[state.current[1]][state.current[0]]
            )
            self.assertEqual(ansi.sub("", buffer.get_char(x - 1, y)), "[")
            self.assertEqual(ansi.sub("", buffer.get_char(x + 1, y)), "]")
            self.assertEqual(ansi.sub("", buffer.get_char(x, 3)), "v")
            self.assertEqual(ansi.sub("", buffer.get_char(0, y)), ">")
            self.assertEqual(ansi.sub("", buffer.get_char(79, y)), "<")
            # Brackets occupy spacing cells rather than erasing neighboring digits.
            if state is counting:
                self.assertEqual(ansi.sub("", buffer.get_char(x - 2, y)), "8")

    def test_cursor_and_pointers_follow_distant_cells_without_overwriting_headers(self):
        rows = ("7" * 100,) * 60
        state = animation.Snapshot(rows, 2, current=(90, 50), height=7, processed=1)
        for height, width in ((8, 8), (10, 20), (24, 80)):
            buffer = Buffer(height, width)
            buffer.put_at(0, 0, "HEADER")
            buffer.put_at(0, 1, "STATUS")
            buffer.put_at(0, height - 1, "FOOTER")
            animation.draw(state, buffer)
            self.assertEqual("".join(buffer.buffer[0][:6]), "HEADER")
            self.assertEqual("".join(buffer.buffer[1][:6]), "STATUS")
            self.assertEqual("".join(buffer.buffer[-1][:6]), "FOOTER")
            cursor = [
                (x, y)
                for y, row in enumerate(buffer.buffer)
                for x, cell in enumerate(row)
                if "48;5;" in cell
            ]
            self.assertEqual(len(cursor), 1)
            self.assertTrue(4 <= cursor[0][1] < height - 2)

    def test_import_is_inert(self):
        with (
            patch("pathlib.Path.read_text", side_effect=AssertionError("input read")),
            patch(
                "bruhanimate.Screen.open", side_effect=AssertionError("terminal opened")
            ),
        ):
            load("day10_animate")

    def test_validation(self):
        for text in ("", "01\n234", "x", "0\n\n1", "0 1"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                animation.parse(text)
        for part in (0, 3):
            with self.assertRaises(ValueError):
                list(animation.snapshots(("0",), part))

    def test_single_route(self):
        final = list(animation.snapshots(animation.parse("0123456789")))[-1]
        self.assertEqual((final.score, final.rating), (1, 1))
        self.assertEqual(final.phase, "complete")
        self.assertEqual(final.peaks, {(9, 0)})

    def test_branches_merge_without_losing_route_multiplicity(self):
        rows = animation.parse("0123456789\n1234567899")
        final = list(animation.snapshots(rows))[-1]
        self.assertEqual((final.score, final.rating), oracle(rows))
        self.assertGreater(final.rating, final.score)
        self.assertEqual(len(final.highlighted), 19)

    def test_unreachable_peaks_missing_heads_and_dots(self):
        for text in ("999\n...", "0.9", "...", "0", "012345678."):
            final = list(animation.snapshots(animation.parse(text)))[-1]
            self.assertEqual((final.score, final.rating), (0, 0))
            self.assertEqual(final.phase, "complete")

    def test_parts_select_distinct_score_and_total_routes(self):
        rows = animation.parse("0123456789\n1234567899")
        one = list(animation.snapshots(rows, 1))[-1]
        two = list(animation.snapshots(rows, 2))[-1]
        self.assertEqual(one.answer, one.score)
        self.assertEqual(two.answer, two.rating)
        self.assertNotEqual(one.answer, two.answer)

    def test_generated_gradient_boards_match_path_enumeration(self):
        rng = random.Random(1010)
        for _ in range(35):
            width, height = rng.randrange(6, 12), rng.randrange(2, 7)
            rows = tuple(
                "".join(
                    str(min(9, x + y)) if rng.random() > 0.12 else "."
                    for x in range(width)
                )
                for y in range(height)
            )
            final = list(animation.snapshots(rows))[-1]
            self.assertEqual((final.score, final.rating), oracle(rows))

    def test_source_is_linear_in_cells_and_heads_not_paths(self):
        rows = tuple("".join(str(min(9, x + y)) for x in range(10)) for y in range(10))
        source = animation.snapshots(rows)
        count = 0
        for final in source:
            count += 1
        self.assertEqual(count, 103)  # initial + 100 cells + one head + completion
        self.assertEqual(final.rating, 512)
        self.assertEqual(final.score, 10)

    def test_immutable_snapshots_and_pure_clipped_draw(self):
        source = animation.snapshots(animation.parse("0123456789\n1234567899"))
        initial = next(source)
        with self.assertRaises(FrozenInstanceError):
            initial.phase = "changed"
        final = list(source)[-1]
        self.assertEqual(initial.highlighted, frozenset())
        self.assertEqual(initial.processed, 0)
        for state in (initial, final):
            for height, width in ((1, 1), (4, 3), (25, 70)):
                left, right = Buffer(height, width), Buffer(height, width)
                animation.draw(state, left)
                animation.draw(state, right)
                self.assertEqual(
                    [
                        [left.get_char(x, y) for x in range(width)]
                        for y in range(height)
                    ],
                    [
                        [right.get_char(x, y) for x in range(width)]
                        for y in range(height)
                    ],
                )

    def test_playback_pause_step_completion(self):
        player = Playback(
            animation.snapshots(("0123456789",)), animation.draw, steps_per_second=20
        )
        player.start()
        player.update(0)
        initial = player.state
        player.pause()
        player.update(50)
        self.assertIs(player.state, initial)
        player.step()
        player.update(0)
        self.assertIsNot(player.state, initial)
        player.resume()
        for _ in range(30):
            player.update(0.1)
        self.assertTrue(player.finished)
        self.assertEqual(player.state.answer, 1)
        player.close()

    def test_main_anchors_input_and_preserves_runner_controls(self):
        with (
            patch("pathlib.Path.read_text", return_value="0123456789"),
            patch.object(animation, "run_animation", return_value=4) as run,
        ):
            self.assertEqual(
                animation.main(
                    ["--part", "1", "--no-background", "--exit-on-complete"]
                ),
                4,
            )
            self.assertFalse(run.call_args.kwargs["background"])
            self.assertEqual(run.call_args.kwargs["steps_per_second"], 12)
            self.assertEqual(run.call_args.kwargs["on_complete"], "exit")
            self.assertEqual(list(run.call_args.args[0])[-1].answer, 1)
        parser = animation.argument_parser("test", animation.__file__, "data")
        self.assertEqual(
            parser.parse_args([]).input, Path(animation.__file__).with_name("data")
        )


if __name__ == "__main__":
    unittest.main()
