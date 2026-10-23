"""Day 7 migration checks using synthetic boards and a headless Screen."""

import contextlib
import importlib.util
import io
import os
import sys
import tempfile
import types
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import patch

import animate
from bruhanimate import Buffer, Playback, Player, Screen

BOARD = animate.parse_board("..S..\n.....\n..^..\n.^.^.\n.....")


class HeadlessScreen:
    width, height = 60, 20

    def __init__(self):
        self.closed = False
        self.draws = 0

    def close(self):
        self.closed = True

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


class BeamTests(unittest.TestCase):
    def test_import_under_the_cli_name_does_not_read_input_or_open_a_terminal(self):
        filename = Path(animate.__file__)
        source = filename.read_text(encoding="utf-8")
        module = types.ModuleType("day07_animate")
        module.__file__ = str(filename)
        with (
            patch.dict(sys.modules, {module.__name__: module}),
            patch.object(
                Path, "read_text", side_effect=AssertionError("import read input")
            ),
            patch.object(
                Screen, "open", side_effect=AssertionError("import opened terminal")
            ),
        ):
            exec(compile(source, str(filename), "exec"), module.__dict__)
        self.assertTrue(callable(module.main))

    def test_invalid_boards_are_rejected(self):
        for text in ("", "S..\n..", "...\n...", "...\n.S.", "SS", "S?"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                animate.parse_board(text)

    def test_counts_include_reconverging_timelines_once_per_route(self):
        self.assertEqual(animate.count_timelines(BOARD), animate.Totals(3, 4))
        paths = list(animate.iter_branches(BOARD))
        self.assertEqual(len(paths), 4)
        self.assertEqual(sum(path[-1][0] == 2 for path in paths), 2)

    def test_boundary_splitter_and_single_row(self):
        edge = animate.parse_board("S..\n^..\n...")
        self.assertEqual(animate.count_timelines(edge), animate.Totals(1, 1))
        self.assertEqual(len(list(animate.iter_branches(edge))), 1)
        self.assertEqual(animate.count_timelines(("S",)), animate.Totals(0, 1))
        self.assertEqual(animate.count_timelines(("S", "^")), animate.Totals(1, 0))

    def test_dynamic_count_does_not_enumerate_exponential_routes(self):
        board = ("..S..",) + ("..^..", ".^.^.") * 40 + (".....",)
        with patch.object(
            animate, "iter_branches", side_effect=AssertionError("eager")
        ):
            self.assertGreater(animate.count_timelines(board).timelines, 10**10)

    def test_branch_source_is_lazy_and_respects_its_limit(self):
        requested = []

        def paths():
            requested.append(1)
            yield ((2, 0), (2, 1))
            raise AssertionError("Read beyond the branch limit")

        with patch.object(animate, "iter_branches", return_value=paths()):
            states = animate.branch_states(BOARD, max_branches=1)
            self.assertEqual(requested, [])
            first = next(states)
            self.assertEqual(requested, [1])
            remaining = list(states)
        self.assertEqual(first.completed, frozenset())
        with self.assertRaises(FrozenInstanceError):
            first.tick = 99
        self.assertEqual(remaining[-1].phase, "complete")
        self.assertEqual(remaining[-1].branch, 1)
        self.assertEqual(remaining[-1].completed, frozenset({((2, 0), (2, 1))}))
        self.assertEqual(first.completed, frozenset())

    def test_row_mode_draws_the_same_complete_graph_as_all_branches(self):
        rows = list(animate.row_states(BOARD))
        branches = list(animate.branch_states(BOARD))
        self.assertEqual(rows[-1].completed, branches[-1].completed)
        self.assertEqual(rows[-1].phase, "complete")

    def test_drawing_is_repeatable_and_does_not_consume_source(self):
        source = animate.branch_states(BOARD)
        playback = Playback(
            source, lambda state, target: animate.draw_snapshot(BOARD, state, target)
        )
        playback.start()
        try:
            for _ in range(7):
                playback.update(0.1)
            snapshot, steps = playback.state, playback.steps
            first, second = Buffer(20, 60), Buffer(20, 60)
            playback.draw(first)
            playback.draw(second)
            self.assertEqual(first.buffer, second.buffer)
            self.assertIs(playback.state, snapshot)
            self.assertEqual(playback.steps, steps)
        finally:
            playback.close()

    def test_clipped_and_scrolled_drawing_handles_tiny_buffers(self):
        state = list(animate.branch_states(BOARD, max_branches=1))[-1]
        for height, width in ((1, 1), (2, 3), (5, 4), (20, 60)):
            with self.subTest(size=(height, width)):
                buffer = Buffer(height, width)
                animate.draw_snapshot(BOARD, state, buffer)
                self.assertEqual(len(buffer.buffer), height)
                self.assertTrue(all(len(row) == width for row in buffer.buffer))

    def test_player_completes_with_endless_backgrounds_and_restores_screen(self):
        original_run = Player.run

        def run(player):
            now = 0.0

            def sleep(seconds):
                nonlocal now
                now += seconds

            player.clock, player.sleep = lambda: now, sleep
            return original_run(player)

        for mode in ("branches", "rows"):
            with self.subTest(mode=mode):
                screen = HeadlessScreen()
                with (
                    patch.object(Screen, "open", return_value=screen),
                    patch.object(Player, "run", run),
                ):
                    frames = animate.run(
                        ("S", ".", "."),
                        mode=mode,
                        frames=120,
                        background=True,
                        on_complete="exit",
                    )
                self.assertLess(frames, 120)
                self.assertGreater(screen.draws, 0)
                self.assertTrue(screen.closed)

    def test_main_reads_only_the_explicit_input_and_forwards_options(self):
        with tempfile.TemporaryDirectory() as folder:
            filename = Path(folder) / "fixture.txt"
            filename.write_text("S..\n...\n", encoding="utf-8")
            with patch.object(animate, "run", return_value=42) as run:
                result = animate.main(
                    [
                        "--input",
                        str(filename),
                        "--mode",
                        "rows",
                        "--no-background",
                        "--exit-on-complete",
                    ]
                )
            self.assertEqual(result, 42)
            self.assertEqual(run.call_args.args[0], ("S..", "..."))
            self.assertFalse(run.call_args.kwargs["background"])
            self.assertEqual(run.call_args.kwargs["on_complete"], "exit")

    def test_missing_input_and_invalid_rates_fail_before_terminal_start(self):
        with tempfile.TemporaryDirectory() as folder:
            missing = str(Path(folder) / "missing")
            for args in (
                ["--input", missing],
                ["--fps", "0"],
                ["--steps-per-second", "nan"],
                ["--max-branches", "0"],
                ["--frames", "-1"],
            ):
                with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                    with (
                        patch.object(animate, "run") as run,
                        self.assertRaises(SystemExit),
                    ):
                        animate.main(args)
                    run.assert_not_called()

    def test_cli_explicit_entrypoint_runs_once_and_restores_working_directory(self):
        cli_file = Path(__file__).resolve().parents[2] / "cli.py"
        spec = importlib.util.spec_from_file_location("day7_test_cli", cli_file)
        cli = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"requests": types.ModuleType("requests")}):
            spec.loader.exec_module(cli)
        original = Path.cwd()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            day = root / "2025/day07"
            day.mkdir(parents=True)
            (day / "animate.py").write_text(
                "from pathlib import Path\n"
                "def main(argv=None):\n"
                "    assert argv == []\n"
                '    Path("called").write_text("once")\n',
                encoding="utf-8",
            )
            try:
                os.chdir(root)
                self.assertTrue(cli.run_animation(2025, 7))
                self.assertEqual(Path.cwd(), root)
                self.assertEqual((day / "called").read_text(), "once")
            finally:
                os.chdir(original)
                sys.modules.pop("day07_animate", None)


if __name__ == "__main__":
    unittest.main()
