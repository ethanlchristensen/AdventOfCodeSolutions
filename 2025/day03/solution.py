"""
Advent of Code 2025 - Day 3
"""

class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, 'r') as f:
            return f.read().strip()
    
    def find_largest_joltage(self, bank: list[int], size: int = 2) -> int:
        values = []

        search_start = 0

        bank_size = len(bank)

        for position in range(size, 0, -1):
            last_viable_spot = bank_size - position
            largest_digit = max(bank[search_start:last_viable_spot+1])
            largest_digit_index = bank.index(largest_digit, search_start, last_viable_spot+1)
            values.append(str(largest_digit))
            search_start = largest_digit_index + 1
        return int("".join(values))

    def part1(self):
        """Solve part 1 of the puzzle."""
        total = 0
        banks = [[int(c) for c in line] for line in self.data.split("\n")]
        for bank in banks:
            total += self.find_largest_joltage(bank)
        return total
    
    def part2(self):
        """Solve part 2 of the puzzle."""
        total = 0
        banks = [[int(c) for c in line] for line in self.data.split("\n")]
        for bank in banks:
            largest = self.find_largest_joltage(bank, 12)
            total += largest
        return total
    
    def solve(self):
        """Run both parts and print results."""
        print(f"Day 3 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
