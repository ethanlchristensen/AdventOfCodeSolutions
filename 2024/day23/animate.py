"""Inspect qualifying triangles or grow the largest fully connected LAN."""

from __future__ import annotations

import math
import re
import string
import sys
from dataclasses import dataclass
from pathlib import Path

from bruhanimate import Buffer, DrawLinesEffect, DrawLinesSettings

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from animation_support import (  # noqa: E402
    argument_parser,
    ink,
    label,
    load_input,
    positive_integer,
    run_animation,
    run_options,
)


@dataclass(frozen=True)
class Network:
    """Sorted names and symmetric immutable adjacency, with duplicate edges removed."""

    names: tuple[str, ...]
    neighbors: tuple[frozenset[int], ...]


def parse_input(text):
    edges = set()
    names = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        values = line.strip().split("-")
        if len(values) != 2 or not all(
            re.fullmatch(r"[A-Za-z0-9_]+", value) for value in values
        ):
            raise ValueError(
                f"Line {number}: expected two computer names separated by '-' "
            )
        left, right = values
        if left == right:
            raise ValueError(f"Line {number}: self connections are not allowed")
        edges.add(tuple(sorted((left, right))))
        names.update(values)
    names = tuple(sorted(names))
    indices = {name: index for index, name in enumerate(names)}
    neighbors = [set() for _ in names]
    for left, right in edges:
        a, b = indices[left], indices[right]
        neighbors[a].add(b)
        neighbors[b].add(a)
    return Network(names, tuple(frozenset(values) for values in neighbors))


@dataclass(frozen=True)
class Snapshot:
    """Only the current search branch and best answer are retained, never a trace."""

    network: Network
    part: int
    phase: str
    current: tuple[int, ...] = ()
    best: tuple[int, ...] = ()
    checked: int = 0
    triangles: int = 0
    qualifying: int = 0
    accepted: bool = False
    candidates: tuple[int, ...] = ()
    pruned: bool = False
    seen: frozenset[int] = frozenset()


def snapshots(network, *, part=2, batch=32):
    """Yield exact results with bounded search expansions between snapshots.

    Part 1 intersects neighbor sets to visit each triangle once. Part 2 uses
    iterative include/exclude branch and bound, with at most one pending
    exclude branch per depth. It never materializes all cliques and does not
    require networkx. Maximum clique remains exponential in the worst case;
    --search-batch bounds expansions per yield, not the total work.
    """
    if part not in (1, 2) or batch < 1:
        raise ValueError("part must be 1 or 2 and search batch must be positive")
    yield Snapshot(
        network,
        part,
        "ready",
        candidates=tuple(range(len(network.names))) if part == 2 else (),
    )
    checked = triangles = qualifying = 0
    if part == 1:
        example, last_triangle = (), ()
        seen = frozenset()
        for a, neighbors in enumerate(network.neighbors):
            for b in sorted(node for node in neighbors if node > a):
                checked += 1
                if checked % batch == 0:
                    yield Snapshot(
                        network,
                        part,
                        "search",
                        example,
                        checked=checked,
                        triangles=triangles,
                        qualifying=qualifying,
                        accepted=bool(example),
                        seen=seen,
                    )
                for c in sorted(
                    node for node in neighbors & network.neighbors[b] if node > b
                ):
                    triangles += 1
                    clique = (a, b, c)
                    accepted = any(
                        network.names[node].startswith("t") for node in clique
                    )
                    qualifying += accepted
                    last_triangle = clique
                    if accepted:
                        example = clique
                        yield Snapshot(
                            network,
                            part,
                            "triangle",
                            clique,
                            checked=checked,
                            triangles=triangles,
                            qualifying=qualifying,
                            accepted=True,
                            seen=seen,
                        )
                        seen = seen | frozenset(clique)
                    elif triangles % batch == 0:
                        yield Snapshot(
                            network,
                            part,
                            "search",
                            example,
                            checked=checked,
                            triangles=triangles,
                            qualifying=qualifying,
                            accepted=bool(example),
                            seen=seen,
                        )
        yield Snapshot(
            network,
            part,
            "complete",
            current=example or last_triangle,
            checked=checked,
            triangles=triangles,
            qualifying=qualifying,
            accepted=bool(example),
            seen=seen,
        )
        return
    candidates = tuple(
        sorted(range(len(network.names)), key=lambda n: (-len(network.neighbors[n]), n))
    )
    stack = [((), candidates)]
    best = ()
    current = ()
    while stack:
        current, candidates = stack.pop()
        checked += 1
        ordered = tuple(sorted(current))
        improved = len(ordered) > len(best) or (
            len(ordered) == len(best) and ordered < best
        )
        if improved:
            best = ordered
        pruned = len(current) + len(candidates) < len(best)
        if not pruned and candidates:
            node, rest = candidates[0], candidates[1:]
            stack.append((current, rest))
            stack.append(
                (
                    (*current, node),
                    tuple(n for n in rest if n in network.neighbors[node]),
                )
            )
        if improved or checked % batch == 0:
            yield Snapshot(
                network,
                part,
                "best" if improved else "search",
                current,
                best,
                checked,
                candidates=candidates,
                pruned=pruned,
            )
    yield Snapshot(network, part, "complete", best, best, checked)


def action(state):
    """Explain the current solver event in puzzle terms rather than graph jargon."""
    if not state.network.names:
        return "No computers in the input."
    if state.part == 1:
        if state.phase == "complete":
            return f"COMPLETE: {state.qualifying} triangles contain a name starting with t."
        if state.phase == "triangle":
            return (
                "COUNT THIS TRIANGLE: contains a t-name."
                if state.accepted
                else "SKIP THIS TRIANGLE: no name starts with t."
            )
        return "Checking a cable for a third computer linked to both ends."
    if state.phase == "complete":
        return f"COMPLETE: largest group has {len(state.best)} computers."
    if state.phase == "ready":
        return "Start empty; add only computers linked to EVERY current member."
    if state.phase == "best":
        return f"NEW BEST: {len(state.best)} computers, all connected to one another."
    if state.pruned:
        return f"SKIP BRANCH: at most {len(state.current) + len(state.candidates)} computers; best has {len(state.best)}."
    if state.candidates:
        return f"GROW GROUP: {len(state.candidates)} remaining computers can join this branch."
    return "Backtracking to try a different group."


def password_lines(names, width):
    """Wrap an exact password at commas, preserving every name."""
    lines, line = [], ""
    for index, name in enumerate(names):
        token = name + ("," if index < len(names) - 1 else "")
        if line and len(line) + len(token) > width:
            lines.append(line)
            line = ""
        while len(token) > width:
            lines.append(token[:width])
            token = token[width:]
        line += token
    if line:
        lines.append(line)
    return lines


def coordinates(network):
    """Restore the original first-letter X / second-letter Y mapping.

    Non-two-letter names use a stable row-major layout instead of colliding or
    inventing letter coordinates. Both layouts stay fixed throughout playback.
    """
    alphabetic = all(re.fullmatch(r"[a-z]{2}", name) for name in network.names)
    if alphabetic:
        return (
            {
                node: (ord(name[0]) - 97, ord(name[1]) - 97)
                for node, name in enumerate(network.names)
            },
            26,
            26,
            True,
        )
    columns = max(1, math.ceil(math.sqrt(len(network.names))))
    rows = max(1, math.ceil(len(network.names) / columns))
    return (
        {node: (node % columns, node // columns) for node in range(len(network.names))},
        columns,
        rows,
        False,
    )


def triangle_preview(state):
    """Part 1 shows a qualifying triple; part 2 draws at most three edges."""
    if state.part == 1:
        return state.current if state.accepted and state.phase != "complete" else ()
    group = tuple(sorted(state.current if len(state.current) >= 3 else state.best))
    if len(group) <= 3:
        return group
    offset = state.checked % len(group)
    return tuple(group[(offset + index) % len(group)] for index in range(3))


def draw_line(buffer, start, end):
    """Use the original sub-cell character renderer rather than approximating it."""
    raster = Buffer(buffer.height(), buffer.width())
    effect = DrawLinesEffect(raster, " ", settings=DrawLinesSettings(thin=False))
    try:
        effect.start()
        effect.add_line(start, end)
        effect.update(0)
        for y, row in enumerate(raster.buffer):
            for x, char in enumerate(row):
                if char != " ":
                    buffer.put_char(x, y, ink(char, 76))
    finally:
        effect.close()


def draw(state, buffer):
    """Render the original fixed coordinate board and one green triangle.

    Previously displayed triangle members stay gray, active vertices are green,
    and only three connecting edges are shown. Short terminals compress the
    full board explicitly; they do not move nodes to a changing circle.
    """
    width, height = buffer.width(), buffer.height()
    if width < 1 or height < 7:
        return
    preview = triangle_preview(state)
    names = tuple(state.network.names[node] for node in preview)
    label(
        buffer,
        0,
        2,
        "A-Z grid: first letter across, second letter down"
        if all(re.fullmatch(r"[a-z]{2}", n) for n in state.network.names)
        else "Stable name grid: sorted names, left to right / top to bottom",
        245,
    )
    headline = (
        f"Triangle {state.qualifying}: {', '.join(names)}"
        if state.part == 1 and preview
        else "All qualifying triangles shown."
        if state.part == 1 and state.phase == "complete"
        else "Searching for the next triangle with a t-name..."
        if state.part == 1
        else f"Triangle preview: {', '.join(names) or '-'} | best group: {len(state.best)}"
    )
    label(buffer, 0, 3, headline, 76)
    if height < 14 or width < 16:
        label(buffer, 0, height - 2, action(state), 51)
        return
    points, columns, rows, alphabetic = coordinates(state.network)
    span_x, span_y = min((columns - 1) * 2, width - 8), min(rows - 1, height - 11)
    x0 = (width - span_x - 1) // 2
    y0 = 6 + max(0, (height - 11 - span_y) // 2)

    def screen(point):
        x, y = point
        return (
            x0 + x * span_x // max(1, columns - 1),
            y0 + y * span_y // max(1, rows - 1),
        )

    compressed = span_x < columns - 1 or span_y < rows - 1
    if state.part == 2:
        message = f"Only {len(preview)} nodes / {len(preview) * (len(preview) - 1) // 2} edges shown; the complete group is still solved."
    else:
        message = "Gray @: earlier triangles | Green @ and lines: current triangle"
    label(buffer, 0, 4, message, 245)
    for y in range(rows):
        for x in range(columns):
            sx, sy = screen((x, y))
            buffer.put_char(sx, sy, ink(".", 234))
    x_step = max(1, math.ceil((columns - 1) / max(1, span_x)))
    y_step = max(1, math.ceil((rows - 1) / max(1, span_y)))
    for x in sorted(set(range(0, columns, x_step)) | {columns - 1}):
        sx, _ = screen((x, 0))
        label(
            buffer,
            sx,
            y0 - 1,
            string.ascii_uppercase[x] if alphabetic else str(x % 10),
            245,
        )
    for y in sorted(set(range(0, rows, y_step)) | {rows - 1}):
        _, sy = screen((0, y))
        label(
            buffer,
            x0 - 2,
            sy,
            string.ascii_uppercase[y] if alphabetic else str(y % 10),
            245,
        )
    for node in state.seen:
        buffer.put_char(*screen(points[node]), ink("@", 240))
    if state.part == 2:
        for node in state.best:
            buffer.put_char(*screen(points[node]), ink("@", 51))
    for index, node in enumerate(preview):
        for other in preview[index + 1 :]:
            if other in state.network.neighbors[node]:
                draw_line(buffer, screen(points[node]), screen(points[other]))
    # Vertices paint after edges, preserving the original green @ markers.
    for node in preview:
        buffer.put_char(*screen(points[node]), ink("@", 76))
    if state.part == 1:
        links = (
            " | ".join(f"{names[i]} <-> {names[(i + 1) % 3]}" for i in range(3))
            if len(names) == 3
            else "No active triangle"
        )
        label(buffer, 0, height - 4, links, 76)
        label(
            buffer,
            0,
            height - 3,
            "Compact grid: coordinates may share cells; enlarge terminal for full A-Z spacing."
            if compressed
            else "Each @ sits at its two-letter coordinate; only the current triangle has lines.",
            245,
        )
        label(
            buffer,
            0,
            height - 2,
            f"Qualifying triangles: {state.qualifying} | All triangles examined: {state.triangles}",
            51,
        )
    else:
        label(buffer, 0, height - 4, action(state), 51)
        result = tuple(state.network.names[n] for n in sorted(state.best))
        lines = password_lines(result, max(1, width - 10)) or ["(empty)"]
        for index, text in enumerate(lines[:2]):
            label(
                buffer,
                0,
                height - 3 + index,
                ("Password: " if index == 0 else "          ") + text,
                51,
            )
        if len(lines) > 2:
            label(
                buffer,
                0,
                height - 2,
                "... enlarge terminal for the complete password",
                226,
            )


def describe(state):
    if state.part == 1:
        return f"Triangles with t*: {state.qualifying} | all triangles: {state.triangles} | edges checked: {state.checked}"
    return f"Computers: {len(state.network.names)} | Current group: {len(state.current)} | Largest found: {len(state.best)} | Branches checked: {state.checked}"


def main(argv=None):
    parser = argument_parser(__doc__, __file__, "data", rate=10)
    parser.set_defaults(part=1, no_background=True)
    parser.add_argument(
        "--background",
        dest="no_background",
        action="store_false",
        help="Enable the decorative background (off by default)",
    )
    parser.add_argument(
        "--search-batch",
        type=positive_integer,
        default=32,
        help="part 2: maximum branch expansions between visual updates",
    )
    args = parser.parse_args(argv)
    network = load_input(parser, args, parse_input)
    return run_animation(
        snapshots(network, part=args.part, batch=args.search_batch),
        draw,
        title=f"2024 Day 23 / part {args.part}",
        describe=describe,
        **run_options(args),
    )


if __name__ == "__main__":
    main()
