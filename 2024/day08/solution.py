"""
Advent of Code 2024 - Day 8
"""

import os
import re
import math


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name='data'):
        with open(name, 'r') as file:
            return [list(line.strip()) for line in file.readlines()]


    def part1(self):
        """Code to solve part one"""
        self.data = self.load_data()
        total = 0
        atenna_locations = self.get_atenna_type_locations(self.data=self.data)
        for atenna, locations in atenna_locations.items():
            for i in range(len(locations)-1):
                for j in range(1+i, len(locations)):
                    p1, p2 = locations[i], locations[j]
                    rise, run = self.rise_and_run(p1, p2)
                    self.data, candidates = self.place_points_in_line(p1, p2, rise, run, self.data)
                    for candidate in candidates:
                        distance_one = self.distance(p1, candidate)
                        distance_two = self.distance(p2, candidate)
                        if distance_one > distance_two:
                            if distance_two * 2 == distance_one:
                                if self.data[candidate[1]][candidate[0]] in [".", "#"]:
                                    total += 1
                        else:
                            if distance_one * 2 == distance_two:
                                if self.data[candidate[1]][candidate[0]] in [".", "#"]:
                                    total += 1

        return total


    def part2(self): 
        """Code to solve part two"""
        self.data = self.load_data()
        total = 0
        antenna_locations = self.get_atenna_type_locations(self.data=self.data)
        for antenna, locations in antenna_locations.items():
            for i in range(len(locations)-1):
                for j in range(1+i, len(locations)):
                    p1, p2 = locations[i], locations[j]
                    rise, run = self.rise_and_run(p1, p2)
                    self.data, candidates = self.place_points_in_line(p1, p2, rise, run, self.data)
                    for candidate in candidates:
                        if self.data[candidate[1]][candidate[0]] == ".":
                            # doesn't work with out this line . . .
                            self.data[candidate[1]][candidate[0]] = "#"
                            total += 1
            total += len(locations)
        for r in self.data:
            print(" ".join(r))
        return total


    def distance(self, p1, p2):
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


    def rise_and_run(self, p1, p2):
        rise = p2[1] - p1[1]
        run = p2[0] - p1[0]
        return rise, run


    def place_points_in_line(self, p1, p2, rise, run):
        height = len(self.data)
        width = len(self.data[0])
        new_p = p1
        locations_placed = []
        while True:
            new_p = (new_p[0] + run, new_p[1] + rise)
            if 0 <= new_p[0] < width and 0 <= new_p[1] < height:
                locations_placed.append(new_p)
            else:
                break
        new_p = p1
        while True:
            new_p = (new_p[0] - run, new_p[1] - rise)
            if 0 <= new_p[0] < width and 0 <= new_p[1] < height:
                locations_placed.append(new_p)
            else:
                break
        locations_placed = [p for p in locations_placed if p not in [p1, p2]]
        return self.data, locations_placed


    def get_atenna_type_locations(self):
        atenna_types = set("".join(["".join(r) for r in self.data]).replace(".", ""))
        atenna_locations = {atenna_type:[] for atenna_type in atenna_types}
        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                if self.data[y][x] != ".":
                    atenna_locations[self.data[y][x]].append((x, y))
        return atenna_locations


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
