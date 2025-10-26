"""
Advent of Code 2024 - Day 3
"""

import re


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name='data'):
        file = open(name, 'r')
        self.data = file.read()
        file.close()
        return self.data
    
    

    def part1(self):
        """
        code to solve part one
        """
        return sum(int(match[0]) * int(match[1]) for match in re.findall(pattern=r'mul\((\d+),(\d+)\)', string=self.load_data()))


    def part2(self):
        """
        code to solve part two
        """
        self.data=[v.group() for v in list(re.finditer(pattern=r'mul\((\d+),(\d+)\)|do\(\)|don\'t\(\)', string=self.load_data()))];return sum((int(re.search("mul\((?P<a>\d+),(?P<b>\d+)\)", mul).groups()[0]) * int(re.search("mul\((?P<a>\d+),(?P<b>\d+)\)", mul).groups()[1])) for mul in [item for i, item in enumerate(self.data) if self.data[i] != "do()" and self.data[i] != "don't()" and (i < next((idx for idx, val in enumerate(self.data) if val == "don't()"), len(self.data)) or any(j < i < k for j in (idx for idx, val in enumerate(self.data) if val == "do()") for k in [next((idx for idx, val in enumerate(self.data[j:], j) if val == "don't()"), len(self.data))]))])
    

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
