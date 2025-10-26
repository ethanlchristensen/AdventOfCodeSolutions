"""
Advent of Code 2024 - Day 7
"""

import os
import re
import math
import time
import itertools


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name="data"):
        with open(name, "r") as file:
            return [
                [int(v) for v in line.replace(":", "").split(" ")]
                for line in file.readlines()
            ]


    def part1(self):
        """Code to solve part one"""
        self.data = self.load_data()
        total = 0

        for calibration in self.data:
            target = calibration[0]
            values = calibration[1:]
            for operation_group in self.get_all_operations_1(len(values) - 1):
                erm = values[0]
                for idx, operation in enumerate(operation_group):
                    if operation == 1:
                        erm += values[idx + 1]
                    elif operation == 0:
                        erm *= values[idx + 1]
                    if erm > target:
                        break
                if erm == target:
                    total += target
                    break

        return total


    def part2(self):
        """Code to solve part two"""
        self.data = self.load_data()
        total = 0

        for calibration in self.data:
            target = calibration[0]
            values = calibration[1:]
            operation_groups = self.get_all_operations_2(len(values) - 1)
            for operation_group in operation_groups:
                erm = values[0]
                for idx, operation in enumerate(operation_group):
                    if operation == 2:
                        erm = int(str(erm) + str(values[idx + 1]))
                    elif operation == 1:
                        erm *= values[idx + 1]
                    elif operation == 0:
                        erm += values[idx + 1]
                    if erm > target:
                        break
                if erm == target:
                    total += target
                    break
        return total



    def get_all_operations_1(self, n):
        return list(itertools.product((0, 1), repeat=n))


    def get_all_operations_2(self, n):
        return list(itertools.product((0, 1, 2), repeat=n))


    def solve(self):
        """Run solutions for part one and two"""
        part_one_answer = self.part1()

        if part_one_answer:
            print(f"part one: {part_one_answer}")

        part_two_answer = self.part2()

        if part_two_answer:
            print(f"part two: {part_two_answer}")




if __name__ == "__main__":
    solution = Solution()
    solution.solve()
