"""
Advent of Code 2024 - Day 2
"""


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name='data'):
        file = open(name, 'r')
        self.data = [line.strip() for line in file.readlines()]
        file.close()
        for idx in range(len(self.data)):
            self.data[idx] = [int(v) for v in self.data[idx].split(" ")]
        return self.data


    def part1(self):
        """
        code to solve part one
        """
        return sum([1 if (False if not any([report == sorted(report), report == sorted(report)[::-1]]) else all([(abs(report[idx] - report[idx + 1]) >= 1 and abs(report[idx] - report[idx + 1]) <= 3) for idx in range(len(report) - 1)])) else 0 for report in self.load_data()])


    def part2(self):
        """
        code to solve part two
        """
        return sum([1 if ((False if not any([report == sorted(report), report == sorted(report)[::-1]]) else all([(abs(report[idx] - report[idx + 1]) >= 1 and abs(report[idx] - report[idx + 1]) <= 3) for idx in range(len(report) - 1)])) or any([(False if not any([[v for i, v in enumerate(report) if i != idx] == sorted([v for i, v in enumerate(report) if i != idx]), [v for i, v in enumerate(report) if i != idx] == sorted([v for i, v in enumerate(report) if i != idx])[::-1]]) else all([(abs([v for i, v in enumerate(report) if i != idx][j] - [v for i, v in enumerate(report) if i != idx][j + 1]) >= 1 and abs([v for i, v in enumerate(report) if i != idx][j] - [v for i, v in enumerate(report) if i != idx][j + 1]) <= 3) for j in range(len([v for i, v in enumerate(report) if i != idx]) - 1)])) for idx in range(len(report))])) else 0 for report in self.load_data()])    


    def solve(self):
        """
        code to run part one and part two
        """
        part_one_answer = self.part1()
        part_two_answer = self.part2()
    
        if part_one_answer:
            print(f"part one: {part_one_answer}")
        if part_two_answer:
            print(f"part two: {part_two_answer}")
    


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
