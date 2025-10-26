"""
Advent of Code 2024 - Day 6
"""

import os
import re
import time


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name='data'):
        file = open(name, 'r')
        self.data = [[c for c in line.strip()] for line in file.readlines()]
        file.close()
        return self.data


    def part1(self):
        """
        code to solve part one
        """
        self.data = self.load_data()
        guard_position = self.get_starting_guard_position()
    
        while True:
            new_position, new_data = self.get_next_position(position=guard_position, )
            if new_position == None:
                self.data = new_data
                break
            guard_position, self.data = new_position, new_data
    
        total = 0
        for row in self.data:
            for char in row:
                if char == "X":
                    total += 1
        return total


    def part2(self):
        """
        code to solve part two
        """
        start = time.time()

        self.data = self.load_data()
        guard_position = self.get_starting_guard_position()
    
        total_chars = len(self.data[0]) * len(self.data)
    
        loops = 0

        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                if self.placement_sees_other_blockers(x, y, ):
                    if x == guard_position[0] and y == guard_position[1]:
                        continue
                    if self.data[y][x] == "#":
                        continue

                    new_data = [[self.data[j][i] for i in range(len(self.data[0]))] for j in range(len(self.data))]
                    new_data[y][x] = "#"

                    if self.is_loop(guard_position=guard_position, total_chars=total_chars): loops += 1

        return loops, time.time() - start


    def get_direction(self, char: str):
        if char == "^":
            return [0, -1]
        if char == ">":
            return [1, 0]
        if char == "<":
            return [-1, 0]
        if char == "v":
            return [0, 1]


    def get_next_guard(self, current_guard):
        if current_guard == "^":
            return ">"
        if current_guard == ">":
            return "v"
        if current_guard == "v":
            return "<"
        if current_guard == "<":
            return "^"


    def get_next_position(self, position):
        current_guard = self.data[position[1]][position[0]]
        direction = self.get_direction(self.data[position[1]][position[0]])
        new_position = (position[0] + direction[0], position[1] + direction[1])
        if not 0 <= new_position[0] < len(self.data[0]) or not 0 <= new_position[1] < len(self.data):
                self.data[position[1]][position[0]] = "X"
                return None, self.data
        if self.data[new_position[1]][new_position[0]] == "#":
            next_guard = self.get_next_guard(current_guard)
            self.data[position[1]][position[0]] = next_guard
            return position, self.data
        else:
            self.data[position[1]][position[0]] = "X"
            self.data[new_position[1]][new_position[0]] = current_guard
            return new_position, self.data


    def get_starting_guard_position(self):
        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                if self.data[y][x] == "^":
                    return (x, y)


    def is_loop(self, guard_position, total_chars, debug = False):
        moves = 0
        starting_position = guard_position
        while True:
            new_position, new_data = self.get_next_position(position=guard_position, )
            if new_position == None:
                self.data = new_data
                break
            guard_position, self.data = new_position, new_data
            moves += 1
            if moves > total_chars:
                break
            if guard_position == starting_position and self.data[new_position[1]][new_position[0]] == "^":
                return True
        return moves > total_chars


    def placement_sees_other_blockers(self, placement_x, placement_y):
        for y in range(len(self.data)):
            if self.data[y][placement_x] == "#":
                return True
        for x in range(len(self.data[0])):
            if self.data[placement_y][x] == "#":
                return True
        return False


    def solve(self):
        """
        code to run part one and part two
        """
        part_one_answer = self.part1()
        part_two_answer, part_two_time = self.part2()
    
        if part_one_answer:
            print(f"part one: {part_one_answer}")
        if part_two_answer:
            print(f"part two: Time to complete: {part_two_time}")
            print(f"part two: {part_two_answer}")
    


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
