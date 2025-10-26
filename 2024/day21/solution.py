"""
Advent of Code 2024 - Day 21
"""

import os
import re
import math
import time


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name='data'):
        with open(name, 'r') as file:
            return [line.strip() for line in file.readlines()]


    def part1(self):
        """Code to solve part one"""
        start = time.time()

        end = time.time()
        return None, end - start


    def part2(self): 
        """Code to solve part two"""
        start = time.time()

        end = time.time()
        return None, end - start


    def solve(self):
        """Run solutions for part one and two"""
        part_one_answer, part_one_time_to_complete = self.part1()

        if part_one_answer:
            print(f"part one: {part_one_answer}\npart one time: {part_one_time_to_complete:.4f}s")

        part_two_answer, part_two_time_to_complete = self.part2()
    
        if part_two_answer:
            print(f"part two: {part_two_answer}\npart two time: {part_two_time_to_complete:.4f}s")



if __name__ == "__main__":
    solution = Solution()
    solution.solve()
