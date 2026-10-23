"""Synthetic-only correctness, lazy state, and terminal-free drawing checks."""

import importlib.util
import random
import sys
import unittest
from collections import deque
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import patch

from bruhanimate import Buffer

SPEC = importlib.util.spec_from_file_location(
    "day18_v1_test_subject", Path(__file__).with_name("animate.py")
)
animation = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = animation
SPEC.loader.exec_module(animation)


def oracle(size, blocked):
    if (0, 0) in blocked or (size - 1, size - 1) in blocked:
        return None
    queue = deque([((0, 0), 0)])
    seen = {(0, 0)}
    while queue:
        (x, y), distance = queue.popleft()
        if (x, y) == (size - 1, size - 1):
            return distance
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if all(0 <= c < size for c in p) and p not in seen and p not in blocked:
                seen.add(p)
                queue.append((p, distance + 1))
    return None


class MemoryTests(unittest.TestCase):
    def test_parse_preserves_order_and_duplicates(self):
        self.assertEqual(animation.parse_input("1,0\n\n1,0\n", 3), ((1, 0), (1, 0)))

    def test_parse_rejects_bad_coordinates(self):
        for text in ("x,2", "1,2,3", "-1,0", "3,0"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                animation.parse_input(text, 3)

    def test_part_one_prefix_and_edge_distance(self):
        points = ((1, 0), (1, 1), (1, 2))
        final = list(animation.snapshots(points, part=1, size=3, prefix=2))[-1]
        self.assertEqual(final.distance, 4)
        self.assertEqual(final.count, 2)
        self.assertEqual(len(final.path), 5)
        self.assertEqual(
            list(animation.snapshots((), part=1, size=1, prefix=0))[-1].distance, 0
        )

    def test_first_blocker_even_before_prefix(self):
        points = ((1, 0), (1, 1), (1, 2), (0, 0))
        final = list(animation.snapshots(points, size=3, prefix=99))[-1]
        self.assertEqual((final.blocker, final.count), ((1, 2), 3))

    def test_endpoints_duplicates_and_no_blocker(self):
        for endpoint in ((0, 0), (2, 2)):
            final = list(animation.snapshots((endpoint,), size=3))[-1]
            self.assertEqual(final.blocker, endpoint)
        final = list(animation.snapshots(((1, 1), (1, 1)), size=3))[-1]
        self.assertIsNone(final.blocker)
        self.assertEqual(final.distance, 4)

    def test_random_sequences_match_independent_search(self):
        rng = random.Random(1800)
        for _ in range(24):
            points = [(x, y) for x in range(4) for y in range(4)]
            rng.shuffle(points)
            blocked = set()
            expected = None
            for count, point in enumerate(points, 1):
                blocked.add(point)
                if oracle(4, blocked) is None:
                    expected = (point, count)
                    break
            final = list(animation.snapshots(tuple(points), size=4, batch=2))[-1]
            self.assertEqual((final.blocker, final.count), expected)
            for prefix in (0, 3, 8, 16):
                final = list(
                    animation.snapshots(tuple(points), part=1, size=4, prefix=prefix)
                )[-1]
                self.assertEqual(final.distance, oracle(4, set(points[:prefix])))

    def test_lazy_frozen_snapshots_and_bounded_bfs(self):
        source = animation.snapshots(((2, 2),), size=10, batch=1)
        initial = next(source)
        self.assertEqual(initial.phase, "ready")
        searching = next(source)
        self.assertEqual(len(searching.visited), 1)
        with self.assertRaises(FrozenInstanceError):
            initial.count = 4
        next(source)
        self.assertEqual(initial.blocked, frozenset())
        source.close()

    def test_invalid_options(self):
        for kwargs in ({"part": 3}, {"size": 0}, {"prefix": -1}, {"batch": 0}):
            with self.assertRaises(ValueError):
                next(animation.snapshots((), **kwargs))
        with self.assertRaises(ValueError):
            list(animation.snapshots((), part=1, prefix=1))

    def test_draw_is_pure_clipped_and_deterministic(self):
        state = list(animation.snapshots(((1, 1),), size=4))[-1]
        before = repr(state)
        for height, width in ((1, 1), (6, 5), (20, 50)):
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

    def test_import_does_not_read_input_or_start_terminal(self):
        spec = importlib.util.spec_from_file_location(
            "day18_animate", Path(animation.__file__)
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
