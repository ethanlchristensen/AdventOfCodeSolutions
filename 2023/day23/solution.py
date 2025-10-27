"""
Advent of Code 2023 - Day 23
"""

import re


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name='data'):
        file = open(name, 'r')
        self.data = [line.strip() for line in file.readlines()]
        file.close()
        return self.data
    
    

    def part1(self):
        """
        code to solve part one
        """
        return None


    def part2(self):
        """
        code to solve part two
        """
        return None
    

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
