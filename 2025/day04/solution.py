"""
Advent of Code 2025 - Day 4
"""


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
        self.previous_state = None
        self.directions = [
            [1, 0],
            [1, 1],
            [0, 1],
            [-1, 1],
            [-1, 0],
            [-1, -1],
            [0, -1],
            [1, -1],
        ]

    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, "r") as f:
            grid = [[c for c in line] for line in f.read().strip().split("\n")]
            self.height = len(grid)
            self.width = len(grid[0])
            return grid

    def neighbor_count(self, x: int, y: int) -> int:
        count = 0
        for dx, dy in self.directions:
            if 0 <= dx + x < self.width and 0 <= dy + y < self.height:
                if self.data[dy + y][dx + x] == "@":
                    count += 1
        return count

    def part1(self):
        """Solve part 1 of the puzzle."""
        total = 0

        for y in range(self.height):
            for x in range(self.width):
                if self.data[y][x] == "@":
                    if self.neighbor_count(x, y) < 4:
                        total += 1

        return total

    def part2(self):
        """Solve part 2 of the puzzle."""
        total = 0

        while self.data != self.previous_state:
            to_remove = []
            self.previous_state = [[c for c in line] for line in self.data]
            for y in range(self.height):
                for x in range(self.width):
                    if self.data[y][x] == "@":
                        if self.neighbor_count(x, y) < 4:
                            to_remove.append((x, y))
            for x, y in to_remove:
                self.data[y][x] = "."
                total += 1

        return total

    def solve(self):
        """Run both parts and print results."""
        print("Day 4 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
