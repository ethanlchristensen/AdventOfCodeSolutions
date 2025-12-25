"""
Advent of Code 2025 - Day 9
"""

import math


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)

    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, "r") as f:
            return [
                tuple(map(int, row.split(","))) for row in f.read().strip().split("\n")
            ]

    def print_board(self, board):
        print(". " * (len(board[0]) + 2))
        for row in board:
            print(". ", end="")
            for c in row:
                print(f"{c} ", end="")
            print(". ", end="")
            print()
        print(". " * (len(board[0]) + 2))
        print()

    def part1(self):
        """Solve part 1 of the puzzle."""
        rectangles = []
        for y1, x1 in self.data:
            for y2, x2 in [p for p in self.data if p != (x1, y1)]:
                area = abs((x2 - x1 + 1) * (y2 - y1 + 1))
                rectangles.append(area)
        return max(rectangles)

    def move_straight(self, dx, dy, x, y, board):
        points = []
        while 0 <= x + dx < len(board[0]) and 0 <= y + dy < len(board):
            x += dx
            y += dy
            if board[y][x] == "#":
                return points
            points.append((x, y))

        return []

    def is_in_bounds(self, point, width):
        if point in self.p2_valid_points:
            return True
        hits = 0
        x, y = point
        cur_x = x
        while cur_x + 1 < width:
            cur_x += 1
            if (cur_x, y) in self.data:
                return False
            if (cur_x, y) in self.p2_valid_points:
                hits += 1

        if hits == 0 or hits % 2 == 0:
            return False
        return True

    def part2(self):
        """Solve part 2 of the puzzle."""
        xs = [x for x, _ in self.data]
        ys = [y for _, y in self.data]

        width = max(xs) + 1
        height = max(ys) + 1

        x_data = {}
        y_data = {}

        for x, y in self.data:
            if x not in x_data:
                x_data[x] = [y]
            else:
                x_data[x].append(y)
            if y not in y_data:
                y_data[y] = [x]
            else:
                y_data[y].append(x)

        valid_points = set()

        for k, v in x_data.items():
            start = min(v)
            end = max(v)
            for y in range(start, end + 1):
                valid_points.add((k, y))

        for k, v in y_data.items():
            start = min(v)
            end = max(v)
            for x in range(start, end + 1):
                valid_points.add((x, k))

        print(f"Shape outline complete")
        self.p2_valid_points = valid_points

        rectangles = []
        for y1, x1 in self.data:
            for y2, x2 in [p for p in self.data if p != (x1, y1)]:
                is_valid = True
                corners = [(x1, y1), (x1, y2), (x2, y1), (x2, y2)]
                for corner in corners:
                    if not self.is_in_bounds(corner, width):
                        is_valid = False
                if is_valid:
                    area = abs((x2 - x1 + 1) * (y2 - y1 + 1))
                    rectangles.append(area)
        return max(rectangles)

    def solve(self):
        """Run both parts and print results."""
        print(f"Day 9 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
