"""Exercise generated v1 animations without real inputs, sessions or terminals."""

import contextlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile
import types
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bruhanimate import Player, Screen  # noqa: E402

import animation_support as support  # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


with patch.dict(sys.modules, {"requests": types.ModuleType("requests")}):
    cli = load("scaffolding_test_cli", ROOT / "cli.py")


class ScreenStub:
    width, height = 80, 24

    def __init__(self):
        self.frames = 0
        self.closed = False

    def has_resized(self):
        return False

    def get_event(self):
        return None

    def begin_frame(self):
        self.frames += 1

    def flush_frame(self):
        pass

    def print_at(self, text, x, y, width):
        pass

    def close(self):
        self.closed = True


ORIGINAL_RUN = Player.run


def run_with_clock(player):
    now = [0.0]

    def sleep(dt):
        now[0] += dt

    player.clock, player.sleep = lambda: now[0], sleep
    return ORIGINAL_RUN(player)


class ScaffoldingTests(unittest.TestCase):
    def setUp(self):
        self.original_dir = Path.cwd()
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name).resolve()
        shutil.copyfile(
            ROOT / "animation_support.py", self.root / "animation_support.py"
        )
        os.chdir(self.root)
        self.addCleanup(self.restore)

    def restore(self):
        os.chdir(self.original_dir)
        self.folder.cleanup()
        sys.modules.pop("day09_animate", None)

    def scaffold(self):
        with patch.object(
            cli, "get_session_cookie", side_effect=AssertionError("read session")
        ):
            cli.setup_day(2099, 9, animate=True, verbose=False)
        return self.root / "2099/day09/animate.py"

    def test_generated_import_is_inert_and_states_are_frozen(self):
        filename = self.scaffold()
        with (
            patch.object(
                Path, "read_text", side_effect=AssertionError("import read input")
            ),
            patch.object(Screen, "open", side_effect=AssertionError("opened terminal")),
        ):
            module = load("generated_inert_animation", filename)
        states = module.states(("one", "two"))
        first = next(states)
        with self.assertRaises(FrozenInstanceError):
            first.phase = "changed"
        self.assertEqual([state.index for state in states], [1, 2, 2])
        self.assertEqual(first.index, 0)

    def test_generated_template_runs_to_completion_with_actual_player(self):
        filename = self.scaffold()
        filename.with_name("data").write_text("one\ntwo\n", encoding="utf-8")
        module = load("generated_playable_animation", filename)
        screen = ScreenStub()
        with (
            patch.object(Screen, "open", return_value=screen),
            patch.object(Player, "run", run_with_clock),
        ):
            frames = module.main(["--exit-on-complete", "--frames", "100"])
        self.assertTrue(0 < frames < 100)
        self.assertEqual(screen.frames, frames)
        self.assertTrue(screen.closed)

    def test_cli_setup_creates_v1_files_and_does_not_overwrite_existing_ones(self):
        with (
            patch.object(
                sys,
                "argv",
                ["cli.py", "setup", "--year", "2099", "--day", "9", "--animate"],
            ),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            cli.main()
        filename = self.root / "2099/day09/animate.py"
        generated = filename.read_text(encoding="utf-8")
        self.assertIn("@dataclass(frozen=True)", generated)
        self.assertNotIn("EffectRenderer", generated)
        self.assertNotIn("render_frame", generated)
        filename.write_text("# user animation\n", encoding="utf-8")
        cli.setup_day(2099, 9, animate=True, verbose=False)
        self.assertEqual(filename.read_text(encoding="utf-8"), "# user animation\n")

    def test_cli_forwards_part_and_relative_input_from_invoking_directory(self):
        self.scaffold()
        fixture = self.root / "example input.txt"
        fixture.write_text("synthetic\n", encoding="utf-8")
        for input_args in (
            ["--input", "example input.txt"],
            ["--input=example input.txt"],
        ):
            screen = ScreenStub()
            argv = [
                "cli.py",
                "animate",
                "--year",
                "2099",
                "--day",
                "9",
                "--",
                "--part",
                "2",
                "--frames",
                "100",
                "--exit-on-complete",
                *input_args,
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.object(Screen, "open", return_value=screen),
                patch.object(Player, "run", run_with_clock),
                patch.object(
                    support, "run_animation", wraps=support.run_animation
                ) as run,
            ):
                cli.main()
            self.assertIn("Part 2", run.call_args.kwargs["title"])
            self.assertTrue(0 < screen.frames < 100)
            self.assertTrue(screen.closed)
            self.assertEqual(Path.cwd(), self.root)

    def test_forwarding_does_not_mutate_the_callers_argument_list(self):
        self.scaffold()
        options = ["--input", "example.txt", "--help"]
        original = list(options)
        with (
            contextlib.redirect_stdout(io.StringIO()),
            self.assertRaises(SystemExit) as result,
        ):
            cli.run_animation(2099, 9, options)
        self.assertEqual(result.exception.code, 0)
        self.assertEqual(options, original)
        self.assertEqual(Path.cwd(), self.root)

    def test_help_is_forwarded_and_working_directory_is_restored(self):
        self.scaffold()
        output = io.StringIO()
        with (
            patch.object(
                sys,
                "argv",
                ["cli.py", "animate", "--year", "2099", "--day", "9", "--", "--help"],
            ),
            contextlib.redirect_stdout(output),
            self.assertRaises(SystemExit) as result,
        ):
            cli.main()
        self.assertEqual(result.exception.code, 0)
        self.assertIn("--steps-per-second", output.getvalue())
        self.assertEqual(Path.cwd(), self.root)

    def test_bad_animation_options_restore_directory_before_exiting(self):
        self.scaffold()
        with (
            patch.object(Screen, "open") as opened,
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit) as result,
        ):
            cli.run_animation(2099, 9, ["--fps", "0"])
        self.assertEqual(result.exception.code, 2)
        self.assertEqual(Path.cwd(), self.root)
        opened.assert_not_called()

    def test_missing_animation_sets_cli_failure_exit_code(self):
        with (
            patch.object(
                sys, "argv", ["cli.py", "animate", "--year", "2099", "--day", "9"]
            ),
            contextlib.redirect_stdout(io.StringIO()),
            self.assertRaises(SystemExit) as result,
        ):
            cli.main()
        self.assertEqual(result.exception.code, 1)

    def test_shared_parser_defaults_are_configurable_and_existing_defaults_stay_compatible(
        self,
    ):
        filename = self.root / "2099/day09/animate.py"
        old = support.argument_parser("test", filename).parse_args([])
        self.assertEqual(old.part, 2)
        self.assertFalse(old.no_background)
        new = support.argument_parser(
            "test", filename, part=1, background=False
        ).parse_args([])
        self.assertEqual(new.part, 1)
        self.assertTrue(new.no_background)
        self.assertEqual(new.input, filename.with_name("data"))

    def test_shared_runner_accepts_plain_values_without_phase_or_describe(self):
        screen = ScreenStub()
        seen = []

        def draw(state, buffer):
            seen.append(state)
            buffer.put_at(0, 5, str(state))

        with (
            patch.object(Screen, "open", return_value=screen),
            patch.object(Player, "run", run_with_clock),
        ):
            frames = support.run_animation(
                iter((1, None, 3)),
                draw,
                title="Generic events",
                background=False,
                on_complete="exit",
                frames=100,
            )
        self.assertTrue(frames < 100)
        self.assertIn(None, seen)
        self.assertEqual(seen[-1], 3)
        self.assertTrue(screen.closed)


if __name__ == "__main__":
    unittest.main()
