"""
Advent of Code 2025 - Day 2
"""

from sympy import divisors


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)

    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, "r") as f:
            return f.read().strip()

    def part1(self):
        """Solve part 1 of the puzzle."""
        return sum(
            [
                (
                    0
                    if (
                        len(str(v)) % 2 != 0
                        or (str(v)[len(str(v)) // 2 :] != str(v)[: len(str(v)) // 2])
                    )
                    else v
                )
                for l in [
                    list(range(a, b + 1))
                    for a, b in [
                        list(map(int, r.split("-"))) for r in self.data.split(",")
                    ]
                ]
                for v in l
            ]
        )

    def part2(self):
        """Solve part 2 of the puzzle."""
        return sum(
            [
                (
                    v
                    if (
                        len(str(v)) > 1
                        and (
                            (
                                len(divisors(len(str(v)))[1:-1]) == 0
                                and str(v).count(str(v)[0]) == len(str(v))
                            )
                            or (
                                any(
                                    all(
                                        str(v)[i : i + z] == str(v)[:z]
                                        for i in range(0, len(str(v)), z)
                                    )
                                    for z in divisors(len(str(v)))[1:-1]
                                )
                            )
                        )
                    )
                    else 0
                )
                for l in [
                    list(range(a, b + 1))
                    for a, b in [
                        list(map(int, r.split("-"))) for r in self.data.split(",")
                    ]
                ]
                for v in l
            ]
        )

    def solve(self):
        """Run both parts and print results."""
        print("Day 2 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
