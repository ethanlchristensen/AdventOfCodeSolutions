"""
Advent of Code 2024 - Day 11
"""

import os
import re
import math
import time
import tqdm


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name="data"):
        with open(name, 'r') as file:
            return [int(v) for v in file.read().strip().split(" ")]


    def part1(self):
        """Code to solve part one"""
        start = time.time()
        self.data = self.load_data()
        blinks = 25
        total = 0
    
        for number in self.data:
            total += self.predict_growth(number, blinks)

        end = time.time()
        return total, end - start


    def part2(self):
        start = time.time()
        self.data = self.load_data()
        blinks = 75
        total = 0

        for number in self.data:
            total += self.predict_growth(number, blinks)
        
        end = time.time()
        return total, end - start


    def predict_growth(self, number, steps, memo=None):
        if memo is None:
            memo = {}

        key = (number, steps)

        if key in memo:
            return memo[key]

        if steps == 0:
            memo[key] = 1
            return 1
    
        if number == 0:
            sub_total = self.predict_growth(1, steps - 1, memo)
            memo[key] = sub_total
            return sub_total

        nstr = str(number)
        if len(nstr) % 2 == 0:
            left = int(nstr[:len(nstr)//2])
            right = int(nstr[len(nstr)//2:])
            sub_total = self.predict_growth(left, steps - 1, memo) + self.predict_growth(right, steps - 1, memo)
            memo[key] = sub_total
            return sub_total
    
        sub_total = self.predict_growth(number * 2024, steps - 1, memo)
        memo[key] = sub_total
        return sub_total


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
