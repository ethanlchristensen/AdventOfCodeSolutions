"""
Advent of Code 2024 - Day 1
"""

import re
import numpy as np


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name='data'):
        file = open(name, 'r')
        self.data = [line.strip() for line in file.readlines()]
        file.close()
        l1 = []
        l2 = []
        for line in self.data:
            vals = line.split("   ")
            l1.append(int(vals[0]))
            l2.append(int(vals[1]))
        return l1, l2
     

    def part1(self):
        """
        code to solve part one
        """
        return sum([abs(a - b) for a, b in zip(*self.load_data())])


    def part2(self):
        """
        code to solve part two
        """
        return sum([num * self.load_data()[1].count(num) for num in self.load_data()[0]])
    

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
