"""
Advent of Code 2025 - Day 1
"""


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)

    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, "r") as f:
            return f.read().strip()

    def rotate(self, direction, clicks, position):
        old_position = position

        passed_through = False

        if direction == "L":
            position += -clicks
        else:
            position += clicks

        if position < 0:
            position = 100 + position
            if position != 0 and old_position != 0:
                passed_through = True
        elif position > 99:
            position = position - 100
            if position != 0 and old_position != 0:
                passed_through = True

        return position, passed_through

    def part1(self):
        """Solve part 1 of the puzzle."""
        data = self.data.split("\n")

        count = 0

        position = 50

        for rotation in data:
            direction, clicks = rotation[0], int(rotation[1:]) % 100
            position, _ = self.rotate(direction, clicks, position)
            if position == 0:
                count += 1

        return count

    def part2(self):
        """Solve part 2 of the puzzle."""
        data = self.data.split("\n")

        count = 0

        position = 50

        for rotation in data:
            direction, clicks, pass_throughs = (
                rotation[0],
                int(rotation[1:]) % 100,
                int(rotation[1:]) // 100,
            )
            position, pass_through = self.rotate(direction, clicks, position)
            if position == 0:
                count += 1
            if pass_through:
                count += 1
            count += pass_throughs

        return count

    def solve(self):
        """Run both parts and print results."""
        print(f"Day 1 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
