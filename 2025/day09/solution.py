"""
Advent of Code 2025 - Day 9
"""

import math


class Solution:
    def __init__(self, data_file="datasmall"):
        self.data = self.load_data(data_file)

    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, "r") as f:
            return [
                tuple(map(int, row.split(","))) for row in f.read().strip().split("\n")
            ]

    def print_board(self, board):
        for row in board:
            for c in row:
                print(f"{c} ", end="")
            print()
        print()

    def part1(self):
        """Solve part 1 of the puzzle."""
        width = max(x for x, y in self.data)
        height = max(y for x, y in self.data)

        board = [["." for _ in range(width + 1)] for __ in range(height + 1)]

        for x, y in self.data:
            board[y][x] = "#"

        self.print_board(board)

        for x, y in self.data:
            hit = self.find_line_up(x, y, board)

            print(hit)

        return None

    def part2(self):
        """Solve part 2 of the puzzle."""
        # TODO: Implement part 2
        return None

    def solve(self):
        """Run both parts and print results."""
        print(f"Day 9 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
