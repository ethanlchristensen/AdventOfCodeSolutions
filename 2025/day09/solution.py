"""
Advent of Code 2025 - Day 9
"""



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

    def is_in_bounds(self, point):
        if point in self.p2_valid_points:
            return True

        x, y = point
        inside = False

        for i in range(len(self.data)):
            x1, y1 = self.data[i]
            x2, y2 = self.data[(i + 1) % len(self.data)]

            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                inside = not inside

        return inside

    def part2(self):
        """Solve part 2 of the puzzle."""
        # doesnt work
        valid_points = set()

        for i in range(len(self.data)):
            x1, y1 = self.data[i]
            x2, y2 = self.data[(i + 1) % len(self.data)]

            if x1 == x2:
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    valid_points.add((x1, y))
            else:
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    valid_points.add((x, y1))

        self.p2_valid_points = valid_points

        max_area = 0
        for i, (x1, y1) in enumerate(self.data):
            for j, (x2, y2) in enumerate(self.data):
                if i >= j:
                    continue

                corners = [(x1, y2), (x2, y1)]
                if all(
                    self.is_in_bounds(c) for c in corners
                ):  # are the mirrored corners inbounds
                    area = (abs(x2 - x1) + 1) * (abs(y2 - y1) + 1)
                    max_area = max(max_area, area)

        return max_area

    def solve(self):
        """Run both parts and print results."""
        print("Day 9 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
