"""
Advent of Code 2025 - Day 5
"""


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)

    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, "r") as f:
            lines = f.read().strip().split("\n")
            split_idx = 0
            for idx, line in enumerate(lines):
                if line == "":
                    split_idx = idx
            ranges = [tuple(map(int, val.split("-"))) for val in lines[:split_idx]]
            values = [int(val) for val in lines[split_idx + 1 :]]
            return (ranges, values)

    def is_fresh(self, val, ranges):
        for a, b in ranges:
            if a <= val <= b:
                return True
        return False

    def merge_ranges(self, ranges):
        seen_ranges = []
        for start, end in sorted(ranges):
            if seen_ranges and start <= seen_ranges[-1][1]:
                seen_ranges[-1] = (seen_ranges[-1][0], max(seen_ranges[-1][1], end))
            else:
                seen_ranges.append((start, end))
        return seen_ranges

    def part1(self):
        """Solve part 1 of the puzzle."""
        total = 0

        ranges, values = self.data

        for val in values:
            if self.is_fresh(val, ranges):
                total += 1

        return total

    def part2(self):
        """Solve part 2 of the puzzle."""
        total = 0

        ranges, _ = self.data

        merged_ranges = self.merge_ranges(ranges)

        for start, end in merged_ranges:
            total += end - start + 1

        return total

    def solve(self):
        """Run both parts and print results."""
        print("Day 5 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
