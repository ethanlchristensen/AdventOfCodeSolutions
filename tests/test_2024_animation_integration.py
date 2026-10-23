"""Cross-day CLI/lifecycle checks with synthetic input and a recording Screen."""

import ast
import contextlib
import importlib.util
import io
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bruhanimate import Player, Screen  # noqa: E402

DAYS = (6, 10, 15, 18, 23)
FIXTURES = {
    6: "....#..\n.......\n..#....\n...^...\n.......\n.#.....\n.......\n",
    10: "0123456789\n1234567899\n",
    15: "#####\n#@O.#\n#...#\n#####\n\n>v<^\n",
    18: "1,0\n1,1\n1,2\n",
    23: "ta-aa\naa-bb\nbb-ta\naa-cc\nbb-cc\nta-cc\n",
}
DEFAULT_INPUTS = {6: "datasmall", 10: "data", 15: "datasmall4", 18: "data", 23: "data"}


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class HeadlessScreen:
    width, height = 80, 24

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


def fake_run(original, limit=12):
    def run(player):
        now = [0.0]

        def sleep(seconds):
            now[0] += seconds

        player.clock = lambda: now[0]
        player.sleep = sleep
        if limit is not None:
            player.frames = limit
        return original(player)

    return run


class AnimationIntegrationTests(unittest.TestCase):
    def test_every_part_completes_and_restores_screen_with_live_background(self):
        original_run = Player.run
        for day in DAYS:
            module = load_module(
                f"completion_2024_day{day}", ROOT / f"2024/day{day:02d}/animate.py"
            )
            for part in (1, 2):
                screen = HeadlessScreen()
                args = [
                    "--part",
                    str(part),
                    "--steps-per-second",
                    "100",
                    "--frames",
                    "1000",
                    "--exit-on-complete",
                ]
                if day == 18:
                    args.extend(("--size", "3", "--prefix", "1"))
                if day == 23:
                    args.append("--background")
                with (
                    patch.object(Path, "read_text", return_value=FIXTURES[day]),
                    patch.object(Screen, "open", return_value=screen),
                    patch.object(Player, "run", fake_run(original_run, limit=None)),
                ):
                    frames = module.main(args)
                self.assertTrue(0 < frames < 1000, (day, part))
                self.assertEqual(screen.draws, frames)
                self.assertTrue(screen.closed)

    def test_imports_under_cli_names_never_read_input_or_open_terminal(self):
        for day in DAYS:
            filename = ROOT / f"2024/day{day:02d}/animate.py"
            source = filename.read_text(encoding="utf-8")
            name = f"day{day:02d}_animate"
            module = types.ModuleType(name)
            module.__file__ = str(filename)
            with (
                patch.dict(sys.modules, {name: module}),
                patch.object(
                    Path, "read_text", side_effect=AssertionError("import read input")
                ),
                patch.object(
                    Screen, "open", side_effect=AssertionError("import opened terminal")
                ),
            ):
                exec(compile(source, str(filename), "exec"), module.__dict__)
            self.assertTrue(callable(module.main))

    def test_migrated_entrypoints_do_not_import_removed_renderers(self):
        for day in DAYS:
            filename = ROOT / f"2024/day{day:02d}/animate.py"
            tree = ast.parse(filename.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
                    "bruhanimate"
                ):
                    names = {item.name for item in node.names}
                    self.assertFalse(
                        names
                        & {
                            "EffectRenderer",
                            "BaseRenderer",
                            "CenterRenderer",
                            "PanRenderer",
                        }
                    )

    def test_actual_cli_runs_every_animation_once_and_restores_directory(self):
        with patch.dict(sys.modules, {"requests": types.ModuleType("requests")}):
            cli = load_module("aoc_2024_integration_cli", ROOT / "cli.py")
        original_dir = Path.cwd()
        original_run = Player.run
        try:
            os.chdir(ROOT)
            for day in DAYS:
                screen = HeadlessScreen()

                def synthetic_input(path, *args, **kwargs):
                    self.assertEqual(
                        path, ROOT / f"2024/day{day:02d}" / DEFAULT_INPUTS[day]
                    )
                    return FIXTURES[day]

                with (
                    patch.object(Path, "read_text", synthetic_input),
                    patch.object(Screen, "open", return_value=screen) as opened,
                    patch.object(Player, "run", fake_run(original_run)),
                ):
                    self.assertTrue(cli.run_animation(2024, day))
                self.assertEqual(opened.call_count, 1)
                self.assertEqual(screen.draws, 12)
                self.assertTrue(screen.closed)
                self.assertEqual(Path.cwd(), ROOT)
        finally:
            os.chdir(original_dir)
            for day in DAYS:
                sys.modules.pop(f"day{day:02d}_animate", None)

    def test_both_parts_run_directly_with_shared_options(self):
        original_run = Player.run
        for day in DAYS:
            module = load_module(
                f"integration_2024_day{day}", ROOT / f"2024/day{day:02d}/animate.py"
            )
            for part in (1, 2):
                screen = HeadlessScreen()
                args = [
                    "--part",
                    str(part),
                    "--no-background",
                    "--fps",
                    "30",
                    "--frames",
                    "12",
                ]
                if day == 18:
                    args.extend(("--size", "3", "--prefix", "1"))
                with (
                    patch.object(Path, "read_text", return_value=FIXTURES[day]),
                    patch.object(Screen, "open", return_value=screen) as opened,
                    patch.object(Player, "run", fake_run(original_run)),
                ):
                    module.main(args)
                self.assertEqual(opened.call_count, 1)
                self.assertEqual(screen.draws, 12)
                self.assertTrue(screen.closed)

    def test_all_2024_animations_are_listed_including_day_six(self):
        with patch.dict(sys.modules, {"requests": types.ModuleType("requests")}):
            cli = load_module("aoc_2024_list_cli", ROOT / "cli.py")
        output, original_dir = io.StringIO(), Path.cwd()
        try:
            os.chdir(ROOT)
            with contextlib.redirect_stdout(output):
                cli.list_animations(2024)
        finally:
            os.chdir(original_dir)
        for day in DAYS:
            self.assertIn(
                f"Day {day:02d}: 2024/day{day:02d}/animate.py", output.getvalue()
            )


if __name__ == "__main__":
    unittest.main()
