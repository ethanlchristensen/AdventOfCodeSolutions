"""Synthetic checks for the Day 3-6 v1 migrations; no private input is read."""

import contextlib
import importlib.util
import io
import math
import os
import random
import re
import sys
import types
import unittest
from dataclasses import FrozenInstanceError
from itertools import combinations, islice
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import animation_support as support  # noqa: E402

from bruhanimate import Buffer, Playback, Player, Screen  # noqa: E402


def load_day(day):
    spec = importlib.util.spec_from_file_location(
        f"day{day:02d}_migration", ROOT / f"2025/day{day:02d}/animate.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


D3, D4, D5, D6 = (load_day(day) for day in range(3, 7))
WORKSHEET = "12  34\n56  78\n+   * \n"
INVENTORY = "1-3\n3-5\n8-8\n6-7\n\n0\n1\n5\n8\n9\n"
FIXTURES = {
    3: "1234567890123\n5555555555555",
    4: "@@@\n@@@\n@@@",
    5: INVENTORY,
    6: WORKSHEET,
}
DEFAULT_INPUTS = {3: "data", 4: "datasmall", 5: "data", 6: "dataanimate"}


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


def fake_run(original, *, limit=None):
    """Inject a deterministic clock without replacing the actual player loop."""

    def run(player):
        now = [0.0]

        def sleep(dt):
            now[0] += dt

        player.clock, player.sleep = lambda: now[0], sleep
        if limit is not None:
            player.frames = limit
        return original(player)

    return run


class BatteryTests(unittest.TestCase):
    def test_selection_matches_brute_force_subsequences(self):
        rng = random.Random(3)
        for _ in range(100):
            bank = "".join(str(rng.randrange(10)) for _ in range(7))
            count = rng.randrange(1, 5)
            expected = max(
                "".join(bank[i] for i in indices)
                for indices in combinations(range(len(bank)), count)
            )
            actual = D3.choose(bank, count)
            self.assertEqual("".join(bank[i] for i in actual), expected)
            final = list(D3.bank_states((bank,), count))[-1]
            self.assertEqual(final.selected, actual)
            self.assertEqual(final.total, int(expected))

    def test_equal_digits_choose_earliest_and_count_all_banks(self):
        self.assertEqual(D3.choose("9999", 2), (0, 1))
        final = list(D3.bank_states(("12",) * 30, 2))[-1]
        self.assertEqual(final.total, 30 * 12)
        self.assertEqual(final.bank, 29)
        self.assertEqual(len(final.recent), 5)

    def test_invalid_banks_and_selection_sizes(self):
        for text in ("", "12\n\n34", "12x", "１２"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                D3.parse_banks(text)
        for count in (0, 4):
            with self.assertRaises(ValueError):
                D3.choose("123", count)
            with self.assertRaises(ValueError):
                next(D3.bank_states(("123",), count))

    def test_selection_window_reserves_enough_digits(self):
        bank = "191919"
        for state in D3.bank_states((bank,), 4):
            if state.phase == "searching":
                self.assertTrue(state.start <= state.candidate < state.end)
                self.assertEqual(state.end, len(bank) - (4 - len(state.selected)) + 1)

    def test_total_commits_once_after_gathering(self):
        states = list(D3.bank_states(("1234", "5678"), 2))
        self.assertEqual(states[-1].total, 34 + 78)
        previous = 0
        for state in states:
            if state.total != previous:
                self.assertEqual(state.phase, "bank complete")
                previous = state.total


class RollTests(unittest.TestCase):
    def test_three_by_three_requires_synchronous_waves(self):
        board = D4.parse_board(FIXTURES[4])
        states = list(D4.roll_states(board))
        removals = [
            state
            for state in states
            if state.phase == "removing" and state.progress == 1
        ]
        self.assertEqual([state.total for state in removals], [4, 8, 9])
        self.assertEqual([state.wave for state in removals], [1, 2, 3])
        self.assertFalse(states[-1].rolls)
        first = list(D4.roll_states(board, part=1))[-1]
        self.assertEqual(first.total, 4)
        self.assertEqual(first.rolls, board.rolls)

    def test_matches_independent_grid_oracle(self):
        rng = random.Random(4)
        for _ in range(30):
            rows = [
                ["@" if rng.random() < 0.7 else "." for _ in range(6)] for _ in range(5)
            ]
            board = D4.parse_board("\n".join("".join(row) for row in rows))
            total = 0
            while True:
                removable = []
                for y in range(5):
                    for x in range(6):
                        neighbors = sum(
                            rows[ny][nx] == "@"
                            for ny in range(max(0, y - 1), min(5, y + 2))
                            for nx in range(max(0, x - 1), min(6, x + 2))
                            if (nx, ny) != (x, y)
                        )
                        if rows[y][x] == "@" and neighbors < 4:
                            removable.append((x, y))
                if not removable:
                    break
                total += len(removable)
                for x, y in removable:
                    rows[y][x] = "."
            final = list(D4.roll_states(board))[-1]
            self.assertEqual(final.total, total)
            self.assertEqual(
                final.rolls,
                frozenset(
                    (x, y) for y in range(5) for x in range(6) if rows[y][x] == "@"
                ),
            )

    def test_detailed_and_wave_modes_agree(self):
        board = D4.parse_board(FIXTURES[4])
        for part in (1, 2):
            detailed = list(D4.roll_states(board, part, detail=True))[-1]
            quick = list(D4.roll_states(board, part))[-1]
            self.assertEqual(
                (detailed.total, detailed.rolls), (quick.total, quick.rolls)
            )

    def test_full_board_is_not_cropped_and_removal_batches_are_bounded(self):
        board = D4.parse_board("@." * 50)
        self.assertEqual(board.width, 100)
        states = list(D4.roll_states(board))
        self.assertEqual(states[-1].total, 50)
        self.assertLessEqual(max(len(state.removed) for state in states), 32)
        self.assertTrue(all(state.total + len(state.rolls) == 50 for state in states))

    def test_empty_rolls_and_invalid_boards(self):
        self.assertEqual(list(D4.roll_states(D4.parse_board("...")))[-1].total, 0)
        for text in ("", "@@\n@", "@x"):
            with self.assertRaises(ValueError):
                D4.parse_board(text)


class InventoryTests(unittest.TestCase):
    def test_overlap_adjacency_endpoints_and_parts(self):
        inventory = D5.parse_inventory(INVENTORY)
        self.assertEqual(D5.merge_ranges(inventory.ranges), ((1, 8),))
        self.assertEqual(list(D5.inventory_states(inventory, 1))[-1].count, 3)
        self.assertEqual(list(D5.inventory_states(inventory, 2))[-1].coverage, 8)

    def test_ranges_match_expanded_set_oracle(self):
        rng = random.Random(5)
        for _ in range(60):
            ranges = tuple(
                tuple(sorted((rng.randrange(30), rng.randrange(30)))) for _ in range(8)
            )
            inventory = D5.Inventory(ranges, tuple(range(35)))
            expected = set().union(*(set(range(a, b + 1)) for a, b in ranges))
            state = list(D5.inventory_states(inventory, 1))[-1]
            self.assertEqual(state.coverage, len(expected))
            self.assertEqual(state.count, len(expected))
            self.assertEqual(state.merged, D5.merge_ranges(ranges))

    def test_huge_ranges_are_not_expanded(self):
        limit = 10**100
        inventory = D5.Inventory(
            ((0, limit), (limit, limit * 2)), (0, limit * 2, limit * 2 + 1)
        )
        states = list(D5.inventory_states(inventory, 1))
        self.assertEqual(states[-1].coverage, limit * 2 + 1)
        self.assertEqual(states[-1].count, 2)
        self.assertLess(len(states), 10)
        D5.draw_inventory(inventory, states[-1], Buffer(20, 60))

    def test_duplicate_ids_are_checked_individually_and_empty_id_list_is_allowed(self):
        inventory = D5.parse_inventory("2-2\n\n2\n2\n1\n")
        self.assertEqual(list(D5.inventory_states(inventory, 1))[-1].count, 2)
        self.assertEqual(D5.parse_inventory("2-2\n\n").ingredients, ())

    def test_invalid_inventory_is_rejected(self):
        for text in ("", "1-2", "\n1-2\n\n1", "3-1\n\n2", "-1-3\n\n1", "1-3\n\nx"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                D5.parse_inventory(text)


class WorksheetTests(unittest.TestCase):
    def test_generated_worksheets_match_independent_row_and_column_oracles(self):
        rng = random.Random(6)
        for _ in range(40):
            operands = [[rng.randrange(1000) for _ in range(3)] for _ in range(4)]
            operations = [rng.choice(("+", "*")) for _ in range(4)]
            rows = [
                "  ".join(f"{block[row]:3d}" for block in operands) for row in range(3)
            ]
            text = "\n".join((*rows, "  ".join(op.ljust(3) for op in operations)))
            worksheet = D6.parse_worksheet(text)
            horizontal_total, vertical_total = 0, 0
            for block, operation in zip(operands, operations):
                aggregate = sum if operation == "+" else math.prod
                horizontal_total += aggregate(block)
                columns = []
                printed = [f"{value:3d}" for value in block]
                for column in range(2, -1, -1):
                    digits = "".join(row[column] for row in printed).replace(" ", "")
                    if digits:
                        columns.append(int(digits))
                vertical_total += aggregate(columns)
            self.assertEqual(
                list(D6.worksheet_states(worksheet, 1))[-1].total, horizontal_total
            )
            self.assertEqual(
                list(D6.worksheet_states(worksheet, 2))[-1].total, vertical_total
            )

    def test_both_reading_directions_and_exact_results(self):
        worksheet = D6.parse_worksheet(WORKSHEET)
        self.assertEqual(worksheet.problems[0].horizontal, (12, 56))
        self.assertEqual(worksheet.problems[0].vertical, (26, 15))
        self.assertEqual(worksheet.problems[1].vertical, (48, 37))
        self.assertEqual(list(D6.worksheet_states(worksheet, 1))[-1].total, 2720)
        self.assertEqual(list(D6.worksheet_states(worksheet, 2))[-1].total, 1817)
        self.assertEqual(next(D6.worksheet_states(worksheet, 2)).problem, 1)

    def test_repeated_operands_are_not_deduplicated(self):
        worksheet = D6.parse_worksheet("11\n11\n* ")
        for part in (1, 2):
            state = list(D6.worksheet_states(worksheet, part))[-1]
            self.assertEqual(state.numbers, (11, 11))
            self.assertEqual(state.total, 121)

    def test_zero_result_is_completed_and_added(self):
        worksheet = D6.parse_worksheet("0\n0\n*\n")
        for part in (1, 2):
            state = list(D6.worksheet_states(worksheet, part))[-1]
            self.assertEqual(state.total, 0)
            self.assertEqual(state.completed, frozenset({0}))

    def test_trailing_newlines_ragged_edges_and_multiple_separator_columns(self):
        worksheet = D6.parse_worksheet("1   2\n3   40\n+   *\n\n")
        self.assertEqual(len(set(map(len, (*worksheet.rows, worksheet.operations)))), 1)
        self.assertEqual(list(D6.worksheet_states(worksheet, 1))[-1].total, 84)
        self.assertEqual(worksheet.problems[1].vertical, (0, 24))

    def test_invalid_blocks_fail_before_playback(self):
        for text in ("", "1", "x\n+", "1\n-", "1\n+*", "1  2\n3   \n+  *", " \n+"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                D6.parse_worksheet(text)

    def test_equation_totals_commit_only_once_per_problem(self):
        states = list(D6.worksheet_states(D6.parse_worksheet(WORKSHEET)))
        last_total, seen = 0, set()
        for state in states:
            if state.total != last_total:
                self.assertEqual(state.phase, "added")
                self.assertNotIn(state.problem, seen)
                seen.add(state.problem)
                last_total = state.total
        self.assertEqual(len(seen), 2)


def cases():
    banks = D3.parse_banks(FIXTURES[3])
    board = D4.parse_board(FIXTURES[4])
    inventory = D5.parse_inventory(FIXTURES[5])
    worksheet = D6.parse_worksheet(FIXTURES[6])
    return (
        (
            D3,
            banks,
            D3.bank_states(banks, 12),
            lambda state, buffer: D3.draw_bank(banks, state, buffer),
        ),
        (
            D4,
            board,
            D4.roll_states(board),
            lambda state, buffer: D4.draw_board(board, state, buffer),
        ),
        (
            D5,
            inventory,
            D5.inventory_states(inventory, 1),
            lambda state, buffer: D5.draw_inventory(inventory, state, buffer),
        ),
        (
            D6,
            worksheet,
            D6.worksheet_states(worksheet),
            lambda state, buffer: D6.draw_worksheet(worksheet, state, buffer),
        ),
    )


class IntegrationTests(unittest.TestCase):
    def test_following_cameras_keep_distant_active_cells_visible(self):
        bank = "5" * 120
        buffer = Buffer(24, 60)
        state = D3.Snapshot(candidate=100, start=90, end=110, phase="searching")
        D3.draw_bank((bank,), state, buffer)
        self.assertIn(support.ink("5", 226), buffer.buffer[12])

        board = D4.Board(120, 60, frozenset({(100, 45), (101, 45)}))
        buffer = Buffer(24, 60)
        D4.draw_board(board, D4.Snapshot(board.rolls, focus=(100, 45)), buffer)
        self.assertTrue(
            any(support.ink("@", 226) in row for row in buffer.buffer[3:17])
        )

        worksheet = D6.parse_worksheet(
            "\n".join(("12  " * 40, "34  " * 40, "+   " * 40))
        )
        state = next(D6.worksheet_states(worksheet, 2))
        buffer = Buffer(24, 60)
        D6.draw_worksheet(worksheet, state, buffer)
        self.assertEqual(state.problem, 39)
        self.assertTrue(
            any(support.ink("2", 226) in row for row in buffer.buffer[3:12])
        )

    def test_simulation_progress_is_independent_of_presentation_rate(self):
        original = Player.run
        for module, puzzle, _, _ in cases():
            durations = []
            for fps in (30, 120):
                with (
                    patch.object(Screen, "open", return_value=HeadlessScreen()),
                    patch.object(Player, "run", fake_run(original)),
                ):
                    frames = module.run(
                        puzzle,
                        fps=fps,
                        background=False,
                        on_complete="exit",
                        frames=2000,
                    )
                self.assertLess(frames, 2000)
                durations.append((frames - 1) / fps)
            self.assertAlmostEqual(*durations, delta=1 / 30, msg=module.__name__)

    def test_imports_under_actual_cli_names_are_inert(self):
        for day in range(3, 7):
            filename = ROOT / f"2025/day{day:02d}/animate.py"
            source = filename.read_text(encoding="utf-8")
            module = types.ModuleType(f"day{day:02d}_animate")
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

    def test_draws_are_pure_clipped_and_ansi_cells_remain_intact(self):
        ansi = re.compile(r"\x1b\[[0-9;]*m")
        for module, _, states, draw in cases():
            snapshots = list(states)
            for state in snapshots:
                for height, width in ((1, 1), (8, 15), (10, 12), (24, 80)):
                    with self.subTest(
                        module=module.__name__, phase=state.phase, size=(height, width)
                    ):
                        first, second = Buffer(height, width), Buffer(height, width)
                        draw(state, first)
                        draw(state, second)
                        self.assertEqual(first.buffer, second.buffer)
                        self.assertEqual(len(first.buffer), height)
                        for row in first.buffer:
                            self.assertEqual(len(row), width)
                            for cell in row:
                                self.assertEqual(len(ansi.sub("", cell)), 1)
                                self.assertNotIn("\x1b", ansi.sub("", cell))
            with self.assertRaises(FrozenInstanceError):
                snapshots[0].phase = "mutated"

    def test_sources_are_lazy_and_stable_when_partially_consumed(self):
        for module, _, states, _ in cases():
            first = next(states)
            original = repr(first)
            list(islice(states, 4))
            self.assertEqual(repr(first), original, module.__name__)
            states.close()

    def test_controls_and_repeated_drawing_never_consume_source(self):
        playback = Playback(
            iter((1, 2, 3)), lambda state, buffer: buffer.put_at(0, 0, str(state))
        )
        playback.start()
        playback.update(0)
        playback.handle_event(ord(" "))
        playback.update(100)
        playback.draw(Buffer(1, 1))
        playback.draw(Buffer(1, 1))
        self.assertEqual(playback.state, 1)
        playback.handle_event(ord("n"))
        playback.update(0)
        self.assertEqual(playback.state, 2)
        playback.handle_event(ord("+"))
        self.assertEqual(playback.steps_per_second, 20)
        self.assertTrue(playback.handle_event(ord("q")))
        playback.close()

    def test_every_scene_completes_and_restores_terminal_with_endless_background(self):
        original = Player.run
        for module, puzzle, _, _ in cases():
            for background in (False, True):
                screen = HeadlessScreen()
                with (
                    patch.object(Screen, "open", return_value=screen),
                    patch.object(Player, "run", fake_run(original)),
                ):
                    frames = module.run(
                        puzzle, frames=2000, on_complete="exit", background=background
                    )
                self.assertTrue(0 < frames < 2000, module.__name__)
                self.assertEqual(screen.draws, frames)
                self.assertTrue(screen.closed)

    def test_actual_cli_entrypoints_run_once_and_restore_directory(self):
        spec = importlib.util.spec_from_file_location(
            "migration_test_cli", ROOT / "cli.py"
        )
        cli = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"requests": types.ModuleType("requests")}):
            spec.loader.exec_module(cli)
        original_dir = Path.cwd()
        original_run = Player.run
        try:
            os.chdir(ROOT)
            for day in range(3, 7):
                screen = HeadlessScreen()

                def synthetic_input(path, *args, **kwargs):
                    self.assertEqual(
                        path, ROOT / f"2025/day{day:02d}" / DEFAULT_INPUTS[day]
                    )
                    return FIXTURES[day]

                with (
                    patch.object(Path, "read_text", synthetic_input),
                    patch.object(Screen, "open", return_value=screen) as opened,
                    patch.object(Player, "run", fake_run(original_run, limit=8)),
                ):
                    self.assertTrue(cli.run_animation(2025, day))
                self.assertEqual(opened.call_count, 1)
                self.assertEqual(screen.draws, 8)
                self.assertTrue(screen.closed)
                self.assertEqual(Path.cwd(), ROOT)
        finally:
            os.chdir(original_dir)
            for day in range(3, 7):
                sys.modules.pop(f"day{day:02d}_animate", None)

    def test_defaults_and_common_options(self):
        for day, module in zip(range(3, 7), (D3, D4, D5, D6)):
            with (
                patch.object(
                    Path, "read_text", autospec=True, return_value=FIXTURES[day]
                ) as read,
                patch.object(module, "run", return_value=42) as run,
            ):
                self.assertEqual(
                    module.main(
                        [
                            "--part",
                            "1",
                            "--steps-per-second",
                            "12",
                            "--fps",
                            "30",
                            "--frames",
                            "10",
                            "--no-background",
                            "--exit-on-complete",
                        ]
                    ),
                    42,
                )
            self.assertEqual(
                read.call_args.args[0],
                ROOT / f"2025/day{day:02d}" / DEFAULT_INPUTS[day],
            )
            self.assertEqual(run.call_args.kwargs["on_complete"], "exit")
            self.assertEqual(run.call_args.kwargs["fps"], 30)
            self.assertFalse(run.call_args.kwargs["background"])
            if day == 3:
                self.assertEqual(run.call_args.kwargs["count"], 2)
            else:
                self.assertEqual(run.call_args.kwargs["part"], 1)

    def test_bad_input_and_options_fail_before_terminal_start(self):
        for module in (D3, D4, D5, D6):
            for args in (
                ["--frames", "-1"],
                ["--fps", "nan"],
                ["--steps-per-second", "0"],
                ["--part", "3"],
            ):
                with (
                    patch.object(Screen, "open") as opened,
                    contextlib.redirect_stderr(io.StringIO()),
                    self.assertRaises(SystemExit),
                ):
                    module.main(args)
                opened.assert_not_called()
            for outcome in (FileNotFoundError("missing"), "invalid input"):
                kwargs = (
                    dict(side_effect=outcome)
                    if isinstance(outcome, Exception)
                    else dict(return_value=outcome)
                )
                with (
                    patch.object(Path, "read_text", **kwargs),
                    patch.object(Screen, "open") as opened,
                    contextlib.redirect_stderr(io.StringIO()),
                    self.assertRaises(SystemExit),
                ):
                    module.main([])
                opened.assert_not_called()

    def test_colored_labels_clip_without_splitting_escape_sequences(self):
        buffer = Buffer(2, 2)
        support.label(buffer, -1, 0, "abc", 51)
        self.assertIn("b", buffer.buffer[0][0])
        self.assertIn("c", buffer.buffer[0][1])
        support.label(buffer, 0, -1, "abc", 51)
        with self.assertRaises(ValueError):
            support.ink("multiple", 51)


if __name__ == "__main__":
    unittest.main()
