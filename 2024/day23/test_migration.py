"""Synthetic graph oracles and immutable, terminal-free playback tests."""

import importlib.util
import itertools
import random
import re
import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import patch

from bruhanimate import Buffer

SPEC = importlib.util.spec_from_file_location(
    "day23_v1_test_subject", Path(__file__).with_name("animate.py")
)
animation = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = animation
SPEC.loader.exec_module(animation)


def oracle(network):
    cliques = []
    triangles = []
    for size in range(1, len(network.names) + 1):
        for candidate in itertools.combinations(range(len(network.names)), size):
            if all(
                b in network.neighbors[a]
                for a, b in itertools.combinations(candidate, 2)
            ):
                cliques.append(candidate)
                if size == 3 and any(
                    network.names[node].startswith("t") for node in candidate
                ):
                    triangles.append(candidate)
    best = (
        min(
            (clique for clique in cliques if len(clique) == max(map(len, cliques))),
            default=(),
        )
        if cliques
        else ()
    )
    return len(triangles), best


class NetworkTests(unittest.TestCase):
    def test_large_winning_group_still_draws_only_one_triangle(self):
        names = tuple(f"a{chr(97 + index)}" for index in range(13))
        others = tuple(f"z{index:03d}" for index in range(507))
        group = tuple(range(13))
        neighbors = (
            tuple(frozenset(set(group) - {node}) for node in group)
            + (frozenset(),) * 507
        )
        network = animation.Network((*names, *others), neighbors)
        state = animation.Snapshot(network, 2, "complete", group, group)
        buffer = Buffer(24, 80)
        buffer.clear_buffer(val=".")
        buffer.put_at(0, 0, "HEADER")
        buffer.put_at(0, 1, "STATUS")
        buffer.put_at(0, 23, "FOOTER")
        animation.draw(state, buffer)

        def plain(row):
            return re.sub(r"\x1b\[[0-9;]*m", "", "".join(row))

        body = "\n".join(plain(row) for row in buffer.buffer[2:23])
        self.assertIn("largest group has 13 computers", body)
        self.assertIn("Only 3 nodes / 3 edges shown", body)
        self.assertIn("Password:", body)
        self.assertNotIn("Matrix:", body)
        self.assertNotIn("z000", body)
        with patch.object(animation, "draw_line", wraps=animation.draw_line) as edges:
            animation.draw(state, Buffer(24, 80))
        self.assertEqual(edges.call_count, 3)
        self.assertEqual(len(set(animation.triangle_preview(state))), 3)
        self.assertEqual(plain(buffer.buffer[0])[:6], "HEADER")
        self.assertEqual(plain(buffer.buffer[1])[:6], "STATUS")
        self.assertEqual(plain(buffer.buffer[23])[:6], "FOOTER")

    def test_password_wrap_preserves_every_name_and_comma(self):
        names = tuple(f"computer{index:02d}" for index in range(13))
        for width in (5, 12, 30, 50):
            lines = animation.password_lines(names, width)
            self.assertEqual("".join(lines), ",".join(names))
            self.assertTrue(all(len(line) <= width for line in lines))
        short = animation.password_lines(("aa", "bb", "cc", "dd"), 8)
        self.assertEqual(short, ["aa,bb,", "cc,dd"])

    def test_source_exposes_compatible_candidates_and_explains_pruning(self):
        network = animation.parse_input("a-b\na-c\nb-c\na-d\nd-e\n")
        for state in animation.snapshots(network, batch=1):
            self.assertTrue(
                all(
                    node not in state.current
                    and all(
                        node in network.neighbors[member] for member in state.current
                    )
                    for node in state.candidates
                )
            )
            if state.pruned:
                self.assertLess(
                    len(state.current) + len(state.candidates), len(state.best)
                )
                self.assertIn("SKIP BRANCH", animation.action(state))

    def test_part_one_completion_leaves_gray_history_without_active_edges(self):
        for text, accepted in (("a-b\nb-ta\nta-a", True), ("a-b\nb-c\nc-a", False)):
            network = animation.parse_input(text)
            state = list(animation.snapshots(network, part=1))[-1]
            self.assertEqual(len(state.current), 3)
            self.assertEqual(state.accepted, accepted)
            buffer = Buffer(24, 80)
            animation.draw(state, buffer)
            body = re.sub(
                r"\x1b\[[0-9;]*m", "", "\n".join("".join(row) for row in buffer.buffer)
            )
            self.assertIn("All qualifying triangles shown.", body)
            self.assertEqual(animation.triangle_preview(state), ())
            self.assertEqual(len(state.seen), 3 if accepted else 0)

    def test_main_uses_slower_quiet_defaults_and_background_is_opt_in(self):
        for args, background in (([], False), (["--background"], True)):
            with (
                patch.object(Path, "read_text", return_value="a-b\nb-ta\nta-a"),
                patch.object(animation, "run_animation", return_value=42) as run,
            ):
                self.assertEqual(animation.main(args), 42)
            self.assertEqual(run.call_args.kwargs["background"], background)
            self.assertEqual(run.call_args.kwargs["steps_per_second"], 10)
            self.assertEqual(next(run.call_args.args[0]).part, 1)

    def test_original_alphabet_coordinates_and_triangle_edges_are_restored(self):
        network = animation.parse_input("ab-cd\ncd-ta\nta-ab\nzz-ab")
        coordinates, columns, rows, alphabetic = animation.coordinates(network)
        indices = {name: index for index, name in enumerate(network.names)}
        self.assertTrue(alphabetic)
        self.assertEqual((columns, rows), (26, 26))
        self.assertEqual(coordinates[indices["ab"]], (0, 1))
        self.assertEqual(coordinates[indices["ta"]], (19, 0))
        triangle = tuple(indices[name] for name in ("ab", "cd", "ta"))
        state = animation.Snapshot(
            network,
            1,
            "triangle",
            triangle,
            accepted=True,
            seen=frozenset({indices["zz"]}),
        )
        buffer = Buffer(40, 80)
        with patch.object(animation, "draw_line", wraps=animation.draw_line) as edges:
            animation.draw(state, buffer)
        self.assertEqual(edges.call_count, 3)
        self.assertEqual(
            sum(
                cell == animation.ink("@", 76) for row in buffer.buffer for cell in row
            ),
            3,
        )
        self.assertEqual(
            sum(
                cell == animation.ink("@", 240) for row in buffer.buffer for cell in row
            ),
            1,
        )

    def test_triangle_history_is_bounded_by_nodes_and_only_qualifying_triples_animate(
        self,
    ):
        network = animation.parse_input("ab-cd\ncd-ta\nta-ab\nab-zz\ncd-zz\nta-zz")
        states = list(animation.snapshots(network, part=1))
        triangles = [state for state in states if state.phase == "triangle"]
        self.assertEqual(len(triangles), oracle(network)[0])
        self.assertEqual(
            [state.qualifying for state in triangles],
            list(range(1, len(triangles) + 1)),
        )
        for state in triangles:
            self.assertTrue(state.accepted)
            self.assertEqual(len(state.current), 3)
            self.assertLessEqual(len(state.seen), len(network.names))
        self.assertEqual(
            states[-1].seen,
            frozenset(node for state in triangles for node in state.current),
        )

    def test_arbitrary_names_use_stable_noncolliding_fallback_coordinates(self):
        network = animation.parse_input("host-router\nrouter-ta\nta-host")
        points, _, _, alphabetic = animation.coordinates(network)
        self.assertFalse(alphabetic)
        self.assertEqual(len(set(points.values())), 3)
        self.assertEqual(points, animation.coordinates(network)[0])

    def test_parse_duplicate_edges_and_symmetric_neighbors(self):
        network = animation.parse_input("ta-a\na-ta\nta-a\n")
        self.assertEqual(network.names, ("a", "ta"))
        self.assertEqual(network.neighbors, (frozenset({1}), frozenset({0})))

    def test_parse_rejects_invalid_connections(self):
        for text in ("a-a", "a-b-c", "a-", "bad name-b", "x-\x1b"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                animation.parse_input(text)

    def test_triangle_prefix_and_largest_clique_are_distinct(self):
        network = animation.parse_input("ta-a\na-b\nb-ta\na-c\nb-c\na-d\nb-d\nc-d\n")
        first = list(animation.snapshots(network, part=1))[-1]
        second = list(animation.snapshots(network, part=2))[-1]
        self.assertEqual(first.qualifying, 1)
        self.assertEqual(
            tuple(network.names[i] for i in second.best), ("a", "b", "c", "d")
        )

    def test_empty_and_no_qualifying_triangle_terminate(self):
        for text in ("", "a-b", "a-b\nb-c\na-c"):
            network = animation.parse_input(text)
            self.assertEqual(
                list(animation.snapshots(network, part=1))[-1].qualifying, 0
            )
            self.assertEqual(list(animation.snapshots(network))[-1].phase, "complete")

    def test_random_graphs_match_exhaustive_oracle(self):
        rng = random.Random(2300)
        names = ("a", "b", "c", "d", "ta", "tb", "tc")
        for _ in range(70):
            edges = [
                f"{a}-{b}"
                for a, b in itertools.combinations(names, 2)
                if rng.random() < 0.5
            ]
            network = animation.parse_input("\n".join(edges))
            expected_triangles, expected_best = oracle(network)
            self.assertEqual(
                list(animation.snapshots(network, part=1))[-1].qualifying,
                expected_triangles,
            )
            self.assertEqual(
                list(animation.snapshots(network, batch=3))[-1].best, expected_best
            )

    def test_snapshot_source_is_lazy_frozen_and_bounded(self):
        network = animation.parse_input(
            "\n".join(f"n{a}-n{b}" for a, b in itertools.combinations(range(14), 2))
        )
        source = animation.snapshots(network, batch=2)
        first = next(source)
        self.assertEqual(first.checked, 0)
        with self.assertRaises(FrozenInstanceError):
            first.checked = 99
        previous = 0
        for _ in range(12):
            state = next(source)
            self.assertLessEqual(state.checked - previous, 2)
            previous = state.checked
        self.assertEqual(first.current, ())
        source.close()

    def test_invalid_part_and_batch(self):
        network = animation.parse_input("a-b")
        for kwargs in ({"part": 0}, {"batch": 0}):
            with self.assertRaises(ValueError):
                next(animation.snapshots(network, **kwargs))

    def test_draw_is_pure_clipped_and_deterministic(self):
        state = list(animation.snapshots(animation.parse_input("ta-a\na-b\nb-ta")))[-1]
        before = repr(state)
        for height, width in ((1, 1), (7, 4), (25, 80)):
            buffers = [Buffer(height, width), Buffer(height, width)]
            for buffer in buffers:
                animation.draw(state, buffer)

            def rows(buffer):
                return tuple(
                    tuple(buffer.get_char(x, y) for x in range(width))
                    for y in range(height)
                )

            self.assertEqual(rows(buffers[0]), rows(buffers[1]))
        self.assertEqual(repr(state), before)

    def test_import_is_inert_even_under_legacy_cli_module_name(self):
        spec = importlib.util.spec_from_file_location(
            "day23_animate", Path(animation.__file__)
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        with (
            patch("pathlib.Path.read_text", side_effect=AssertionError("input read")),
            patch(
                "animation_support.run_animation",
                side_effect=AssertionError("terminal opened"),
            ),
        ):
            spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))


if __name__ == "__main__":
    unittest.main()
