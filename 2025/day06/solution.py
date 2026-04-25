"""
Advent of Code 2025 - Day 6
"""

import re


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)

    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, "r") as f:
            return f.read().split("\n")

    def run_operation(self, operation: str, numbers: list[int]) -> int:
        total = 0 if operation == "+" else 1
        for number in numbers:
            if operation == "+":
                total += number
            elif operation == "*":
                total *= number
        return total

    def seeker(self):
        main_rows = self.data[:-1]
        width = len(main_rows[0])
        seeker_position = 0

        current_column = 0
        current_column_width = 0
        column_widths = []

        while seeker_position < width:
            if all(
                main_rows[idx][seeker_position] == " " for idx in range(len(main_rows))
            ):
                column_widths.append(current_column_width)
                current_column += 1
                current_column_width = 0
            else:
                current_column_width += 1
            seeker_position += 1

        column_widths.append(current_column_width)

        return column_widths

    def part1(self):
        """Solve part 1 of the puzzle."""
        total = 0
        problem_numbers = {}
        for row in self.data[:-1]:
            row = re.sub(r"\s+", " ", row).split()
            for idx, number in enumerate(row):
                if idx in problem_numbers:
                    problem_numbers[idx].append(int(number))
                else:
                    problem_numbers[idx] = [int(number)]

        operations = re.sub(r"\s+", " ", self.data[-1]).split(" ")
        for idx in range(len(problem_numbers)):
            numbers = problem_numbers[idx]
            total += self.run_operation(operations[idx], numbers)

        return total

    def part2(self):
        """Solve part 2 of the puzzle."""
        total = 0
        column_widths = self.seeker()
        main_rows = self.data[:-1]
        operations = re.sub(r"\s+", " ", self.data[-1]).split(" ")
        seeker_position = 0

        for wdx, width in enumerate(column_widths):
            numbers = []
            operation = operations[wdx]
            for jdx in range(seeker_position + width - 1, seeker_position - 1, -1):
                erm = "".join([main_rows[idx][jdx] for idx in range(len(main_rows))])
                numbers.append(int(erm))
            total += self.run_operation(operation, numbers)
            seeker_position += width + 1
        return total

    def solve(self):
        """Run both parts and print results."""
        print("Day 6 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
