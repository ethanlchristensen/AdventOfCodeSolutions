import os
import re
import math
import time
import numpy as np
from sympy import nsolve
from sympy.abc import A, B
from z3 import Ints, solve as s, And, RealVal


def load_data(name="data", part=1):
    with open(name, "r") as file:
        puzzles = []
        lines = [line.strip() for line in file.readlines()]
        puzzle = []
        for idx, line in enumerate(lines):
            if idx % 2 == 0:
                if match := re.match(r"Button A: X\+(\d+),\sY\+(\d+)", line):
                    puzzle.append([int(v) for v in match.groups()])
                elif match := re.match(r"Prize\:\sX\=(\d+),\sY\=(\d+)", line):
                    if part == 1:
                        puzzle.append([int(v) for v in match.groups()])
                    elif part == 2:
                        puzzle.append([int(v) + 10000000000000 for v in match.groups()])
            else:
                if line != "":
                    if match := re.match(r"Button B: X\+(\d+),\sY\+(\d+)", line):
                        puzzle.append([int(v) for v in match.groups()])
                else:
                    puzzles.append(puzzle)
                    puzzle = []
        puzzles.append(puzzle)
        return puzzles


def part_one():
    """Code to solve part one"""
    start = time.time()
    data = load_data()
    total = 0
    possible_costs = {}
    for idx, puzzle in enumerate(data):
        possible_costs[idx] = []

        for a in range(1, 101):
            for b in range(1, 101):
                s1 = puzzle[0][0] * a + puzzle[1][0] * b
                s2 = puzzle[0][1] * a + puzzle[1][1] * b
                if s1 == puzzle[2][0] and s2 == puzzle[2][1]:
                    possible_costs[idx].append(a * 3 + b)

        if not possible_costs[idx]:
            del possible_costs[idx]

    for idx, costs in possible_costs.items():
        total += min(costs)

    end = time.time()
    return total, end - start


def part_two():
    """Code to solve part two"""
    start = time.time()
    data = load_data(part=2)
    total = 0
    a, b = Ints("a b")
    for idx, puzzle in enumerate(data):
        seen = set()
        while True:
            args = []

            args.append(
                (RealVal(puzzle[0][0]) * a) + (RealVal(puzzle[1][0]) * b)
                == RealVal(puzzle[2][0])
            )
            args.append(
                (RealVal(puzzle[0][1]) * a) + (RealVal(puzzle[1][1]) * b)
                == RealVal(puzzle[2][1])
            )

            for v in seen:
                args.append(b != v[0])
                args.append(a != v[1])

            sol = s(*args)

            sol = str(sol)

            if sol == "None":
                break

            matches = re.search(r"\[b = (\d+), a = (\d+)\]", sol)
            if matches:
                values = tuple([int(v) for v in matches.groups()])
                if values not in seen:
                    total += (values[1] * 3) + values[0]
                    seen.add(values)
                else:
                    break

    end = time.time()
    return total, end - start


def solve():
    """Run solutions for part one and two"""
    part_one_answer, part_one_time_to_complete = part_one()

    if part_one_answer:
        print(
            f"part one: {part_one_answer}\npart one time: {part_one_time_to_complete:.4f}s"
        )

    part_two_answer, part_two_time_to_complete = part_two()

    if part_two_answer:
        print(
            f"part two: {part_two_answer}\npart two time: {part_two_time_to_complete:.4f}s"
        )


if __name__ == "__main__":
    solve()
