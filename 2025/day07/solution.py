"""
Advent of Code 2025 - Day 7
"""

from collections import deque

from functools import lru_cache


class Solution:
    def __init__(self, data_file="datasmall"):
        self.data = self.load_data(data_file)
        self.width = len(self.data[0])
        self.height = len(self.data)
        self.start_position = self.find_start()
        self.splitters = set()

    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, "r") as f:
            return [[c for c in line] for line in f.read().strip().split("\n")]

    def find_start(self):
        return (self.data[0].index("S"), 0)

    def print_board(self):
        for row in self.data:
            print("".join(row))
        print()

    def part1(self):
        """Solve part 1 of the puzzle."""
        moves = deque()

        sx, sy = self.start_position

        moves.append((sx, sy))

        while moves:
            x, y = moves.popleft()
            dy = y + 1
            dx = x

            if dy >= self.height:
                continue
            if dx < 0 or dx > self.width:
                continue

            value = self.data[dy][dx]

            if value == "." or value == "|":
                moves.append((dx, dy))
                self.data[y][x] = "|"
            elif value == "^":
                self.splitters.add((dx, dy))
                moves.append((dx - 1, dy))
                moves.append((dx + 1, dy))

        return len(self.splitters)

    def part2(self):
        """Solve part 2 of the puzzle."""
        sx, sy = self.start_position

        moves = deque()

        moves.append((sx, sy, (sx, sy)))

        completed = set()

        while moves:
            x, y, path = moves.popleft()

            dy = y + 1
            dx = x

            if dy >= self.height:
                completed.add(path)
                continue

            if dx < 0 or dx >= self.width:
                continue

            cell = self.data[dy][dx]

            if cell in ".|":
                moves.append((dx, dy, path + (dx, dy)))
            elif cell == "^":
                moves.append((dx - 1, dy, path + (dx - 1, dy)))
                moves.append((dx + 1, dy, path + (dx + 1, dy)))

        return len(completed)

    def solve(self):
        """Run both parts and print results."""
        print(f"Day 7 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
