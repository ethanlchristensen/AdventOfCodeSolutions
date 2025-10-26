"""
Advent of Code 2024 - Day 19
"""

import os
import re
import math
import time
from tqdm import tqdm


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name='data'):
        with open(name, 'r') as file:
            lines = [line.strip() for line in file.readlines() if line.strip() != ""]
            rules = lines[0].split(", ")
            towels = lines[1:]
            return rules, towels

    memo = {}

    def part1(self):
        """Code to solve part one"""
        start = time.time()

        rules, towels = self.load_data()

        total = 0

        for towel in towels:
            if self.valid(rules, towel):
                total += 1
        end = time.time()
        return total, end - start


    def part2(self): 
        """Code to solve part two"""
        start = time.time()

        rules, towels = self.load_data()

        total = 0

        for towel in towels:
            if possible_combinations := self.valid(rules, towel):
                total += possible_combinations

        end = time.time()
        return total, end - start


    def valid(self, rules, string: str):
        if string not in memo:
            if len(string) == 0:
                return 1
            else:
                total = 0
                for rule in rules:
                    if string.startswith(rule):
                        total += self.valid(rules, string[len(rule):])
                    memo[string] = total
        return memo[string]


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
