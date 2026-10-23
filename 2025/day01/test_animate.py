"""Synthetic Day 1 checks; no puzzle inputs, credentials, or real terminals."""

import contextlib
import importlib.util
import io
import os
import random
import sys
import types
import unittest
from dataclasses import FrozenInstanceError
from itertools import islice
from pathlib import Path
from unittest.mock import patch

import animate

from bruhanimate import Buffer, Playback, Player, Screen


class HeadlessScreen:
    width, height = 80, 30

    def __init__(self):
        self.draws = 0
        self.closed = False

    def has_resized(self):
        return False

    def get_event(self):
        return None

    def begin_frame(self):
        self.draws += 1

    def flush_frame(self):
        pass

    def print_at(self, text, x, y, width):
        pass

    def close(self):
        self.closed = True


class DialTests(unittest.TestCase):
    def test_existing_aoc_cli_runs_once_and_restores_terminal_and_directory(self):
        root = Path(animate.__file__).resolve().parents[2]
        spec = importlib.util.spec_from_file_location("day1_test_cli", root / "cli.py")
        cli = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"requests": types.ModuleType("requests")}):
            spec.loader.exec_module(cli)
        screen = HeadlessScreen()
        original_run = Player.run
        original_dir = Path.cwd()
        now = [0.0]

        def sleep(dt):
            now[0] += dt

        def run(player):
            player.frames = 90
            player.clock, player.sleep = lambda: now[0], sleep
            return original_run(player)

        def synthetic_input(path, *args, **kwargs):
            self.assertEqual(path, root / "2025/day01/data1")
            return "R0"

        try:
            os.chdir(root)
            with (
                patch.object(Path, "read_text", synthetic_input),
                patch.object(Screen, "open", return_value=screen) as opened,
                patch.object(Player, "run", run),
            ):
                self.assertTrue(cli.run_animation(2025, 1))
            self.assertEqual(opened.call_count, 1)
            self.assertEqual(screen.draws, 90)
            self.assertTrue(screen.closed)
            self.assertEqual(Path.cwd(), root)
        finally:
            os.chdir(original_dir)
            sys.modules.pop("day01_animate", None)

    def test_import_under_cli_name_has_no_input_or_terminal_side_effects(self):
        filename = Path(animate.__file__)
        source = filename.read_text(encoding="utf-8")
        module = types.ModuleType("day01_animate")
        module.__file__ = str(filename)
        with (
            patch.dict(sys.modules, {module.__name__: module}),
            patch.object(Path, "read_text", side_effect=AssertionError("read input")),
            patch.object(Screen, "open", side_effect=AssertionError("opened screen")),
        ):
            exec(compile(source, str(filename), "exec"), module.__dict__)
        self.assertTrue(callable(module.main))

    def test_parser_validates_each_line(self):
        self.assertEqual(
            animate.parse_rotations(" L0\nR150 \n"),
            (animate.Rotation("L", 0), animate.Rotation("R", 150)),
        )
        for text in ("", "R", "X1", "L-2", "R1.5", "L+1", "R１２", "L1\n\nR2"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                animate.parse_rotations(text)

    def test_analytical_totals_match_independent_click_oracle(self):
        rng = random.Random(1)
        for _ in range(100):
            rotations = tuple(
                animate.Rotation(rng.choice("LR"), rng.randrange(401))
                for _ in range(10)
            )
            position, stops, crossings = 50, 0, 0
            for rotation in rotations:
                for _ in range(rotation.clicks):
                    position = (
                        position + (1 if rotation.direction == "R" else -1)
                    ) % 100
                    crossings += position == 0
                stops += position == 0
            self.assertEqual(animate.solve(rotations), (stops, crossings, position))

    def test_full_turns_zero_clicks_and_starting_at_zero(self):
        rotations = animate.parse_rotations("L50\nR100\nL100\nR0\nL1")
        self.assertEqual(animate.solve(rotations), (4, 3, 99))
        # Huge turns must be counted analytically, not by iterating over clicks.
        self.assertEqual(
            animate.solve(animate.parse_rotations(f"R{10**30}")), (0, 10**28, 50)
        )

    def test_lazy_trace_matches_both_answers(self):
        rotations = animate.parse_rotations("L50\nR100\nL100\nR0\nL1")
        for part in (1, 2):
            state = None
            for state in animate.dial_states(rotations, part):
                pass
            self.assertEqual(
                (state.stops, state.crossings, state.position), animate.solve(rotations)
            )
            self.assertEqual((state.phase, state.exit_progress), ("complete", 1))

    def test_count_changes_at_arrival_and_part_one_only_at_instruction_end(self):
        states = animate.dial_states(animate.parse_rotations("L51"))
        previous = next(states)
        for state in states:
            if state.crossings != previous.crossings:
                self.assertEqual(
                    (state.position, state.motion, state.remaining), (0, 0, 1)
                )
                self.assertEqual(previous.position, 1)
                self.assertEqual(state.stops, 0)
                break
            previous = state
        else:
            self.fail("No zero arrival was yielded")

    def test_left_wrap_and_interpolation(self):
        states = animate.dial_states(animate.parse_rotations("L51"))
        saw_motion = False
        for state in states:
            if state.motion:
                saw_motion = True
                self.assertTrue(-1 < state.motion < 0)
        self.assertTrue(saw_motion)
        self.assertEqual(state.position, 99)

    def test_huge_trace_is_lazy_and_snapshots_are_immutable(self):
        states = animate.dial_states(animate.parse_rotations(f"R{10**30}"))
        first = next(states)
        self.assertEqual(len(list(islice(states, 20))), 20)
        self.assertEqual(first.position, 50)
        with self.assertRaises(FrozenInstanceError):
            first.position = 0
        states.close()

    def test_draw_is_repeatable_and_clips_small_and_large_screens(self):
        state = animate.Snapshot(position=0, crossings=3, tick=10, flash_at=5)
        for height, width in ((1, 1), (10, 30), (20, 45), (30, 100)):
            for lines in (False, True):
                with self.subTest(height=height, width=width, lines=lines):
                    first, second = Buffer(height, width), Buffer(height, width)
                    animate.draw_dial(state, first, show_lines=lines)
                    animate.draw_dial(state, second, show_lines=lines)
                    self.assertEqual(first.buffer, second.buffer)
        self.assertEqual(
            state, animate.Snapshot(position=0, crossings=3, tick=10, flash_at=5)
        )

    def test_art_cache_is_bounded_and_returns_immutable_rows(self):
        self.assertIsInstance(animate.art("50"), tuple)
        self.assertEqual(animate.art.cache_info().maxsize, 128)

    def test_playback_pause_step_and_quit_work_without_consuming_in_draw(self):
        playback = Playback(
            animate.dial_states(animate.parse_rotations("R2")),
            animate.draw_dial,
            steps_per_second=60,
        )
        playback.start()
        playback.update(0)
        playback.handle_event(ord(" "))
        state = playback.state
        playback.update(1)
        playback.draw(Buffer(20, 60))
        self.assertIs(playback.state, state)
        playback.handle_event(ord("n"))
        playback.update(0)
        self.assertIsNot(playback.state, state)
        self.assertTrue(playback.handle_event(ord("q")))
        playback.close()

    def test_scene_completes_with_or_without_infinite_backgrounds(self):
        for background in (False, True):
            screen = HeadlessScreen()
            now = [0.0]

            def sleep(dt):
                now[0] += dt

            def headless_play(**kwargs):
                return Player(screen, clock=lambda: now[0], sleep=sleep, **kwargs).run()

            with patch.object(animate, "play", side_effect=headless_play):
                frames = animate.run(
                    animate.parse_rotations("R0"),
                    background=background,
                    on_complete="exit",
                    frames=150,
                )
            self.assertTrue(70 < frames < 150)
            self.assertEqual(screen.draws, frames)
            self.assertFalse(screen.closed)

    def test_presentation_fps_does_not_change_completion_time(self):
        durations = []
        for fps in (30, 120):
            now = [0.0]
            screen = HeadlessScreen()

            def sleep(dt):
                now[0] += dt

            def headless_play(**kwargs):
                return Player(screen, clock=lambda: now[0], sleep=sleep, **kwargs).run()

            with patch.object(animate, "play", side_effect=headless_play):
                animate.run(
                    animate.parse_rotations("L2"),
                    background=False,
                    fps=fps,
                    on_complete="exit",
                    frames=1000,
                )
            durations.append(now[0])
        self.assertAlmostEqual(*durations, delta=1 / 30)

    def test_cli_default_input_is_anchored_and_options_are_forwarded(self):
        with (
            patch.object(Path, "read_text", autospec=True, return_value="R0") as read,
            patch.object(animate, "run", return_value=42) as run,
        ):
            result = animate.main(
                [
                    "--part",
                    "1",
                    "--speed",
                    "2",
                    "--no-background",
                    "--show-lines",
                    "--exit-on-complete",
                    "--frames",
                    "10",
                ]
            )
        self.assertEqual(result, 42)
        self.assertEqual(
            read.call_args.args[0], Path(animate.__file__).resolve().with_name("data1")
        )
        self.assertEqual(run.call_args.kwargs["part"], 1)
        self.assertEqual(run.call_args.kwargs["speed"], 2)
        self.assertFalse(run.call_args.kwargs["background"])
        self.assertEqual(run.call_args.kwargs["on_complete"], "exit")

    def test_cli_rejects_invalid_options_and_missing_or_malformed_input(self):
        for args in (
            ["--speed", "0"],
            ["--fps", "nan"],
            ["--part", "3"],
            ["--frames", "-1"],
        ):
            with (
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                animate.main(args)
        for outcome in (FileNotFoundError("missing input"), "R-2"):
            kwargs = (
                {"side_effect": outcome}
                if isinstance(outcome, Exception)
                else {"return_value": outcome}
            )
            with (
                patch.object(Path, "read_text", **kwargs),
                patch.object(animate, "run") as run,
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                animate.main([])
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
