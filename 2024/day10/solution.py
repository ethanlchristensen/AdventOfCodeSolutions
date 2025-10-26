"""
Advent of Code 2024 - Day 10
"""

import os
import re
import math
import time
import uuid


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name="data"):
        with open(name, "r") as file:
            return [list(line.strip()) for line in file.readlines()]


    def part1(self):
        """Code to solve part one"""
        start = time.time()
        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        self.data = self.load_data()
        tiles_traversed = {}
        def check_dir(value, x, y, dir, trail_head_id):
            dx, dy = x + dir[0], y + dir[1]
            if 0 <= dy < len(self.data) and 0 <= dx < len(self.data[0]):
                if self.data[dy][dx] != ".":
                    if int(self.data[dy][dx]) == int(value) + 1:
                        if (dx, dy) not in tiles_traversed[trail_head_id]["seen_xy"]:
                            tiles_traversed[trail_head_id]["seen_xy"].append((dx, dy))
                            if self.data[dy][dx] == "9":
                                tiles_traversed[trail_head_id]["times_hit_9"] += 1
                                return
                            # we found a valid next tile, so now we need to search in all directions
                            new_value = self.data[dy][dx]
                            for direction in directions:
                                check_dir(new_value, dx, dy, direction, trail_head_id)

        trail_heads = self.find_all_trail_heads(self.data=self.data)
        for trail_head in trail_heads:
            trail_head_id = str(uuid.uuid4())
            tiles_traversed[trail_head_id] = {"times_hit_9": 0, "seen_xy": []}
            for direction in directions:
                check_dir("0", trail_head[0], trail_head[1], direction, trail_head_id)
        total = sum(v["times_hit_9"] for v in tiles_traversed.values())
        end = time.time()
        return total, end - start



    def part2(self):
        """Code to solve part two"""
        start = time.time()
        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        self.data = self.load_data()
        tiles_traversed = {}
        def check_dir(value, x, y, dir, trail_head_id):
            dx, dy = x + dir[0], y + dir[1]
            if 0 <= dy < len(self.data) and 0 <= dx < len(self.data[0]):
                if self.data[dy][dx] != ".":
                    if int(self.data[dy][dx]) == int(value) + 1:
                    # if (dx, dy) not in tiles_traversed[trail_head_id]["seen_xy"]: # just need to comment out this line for part 2!
                        tiles_traversed[trail_head_id]["seen_xy"].append((dx, dy))
                        if self.data[dy][dx] == "9":
                            tiles_traversed[trail_head_id]["times_hit_9"] += 1
                            return
                        new_value = self.data[dy][dx]
                        for direction in directions:
                            check_dir(new_value, dx, dy, direction, trail_head_id)

        trail_heads = self.find_all_trail_heads(self.data=self.data)

        for trail_head in trail_heads:
            trail_head_id = str(uuid.uuid4())
            tiles_traversed[trail_head_id] = {"times_hit_9": 0, "seen_xy": []}
            for direction in directions:
                check_dir("0", trail_head[0], trail_head[1], direction, trail_head_id)

        total = sum(v["times_hit_9"] for v in tiles_traversed.values())

        end = time.time()
    
        return total, end - start



    def find_all_trail_heads(self):
        trail_heads = []
        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                if self.data[y][x] == "0":
                    trail_heads.append((x, y))
        return trail_heads


    def solve(self):
        """Run solutions for part one and two"""
        part_one_answer, part_one_time_to_complete = self.part1()

        if part_one_answer:
            print(
                f"part one: {part_one_answer}\npart one time: {part_one_time_to_complete:.4f}s"
            )

        part_two_answer, part_two_time_to_complete = self.part2()

        if part_two_answer:
            print(
                f"part two: {part_two_answer}\npart two time: {part_two_time_to_complete:.4f}s"
            )




if __name__ == "__main__":
    solution = Solution()
    solution.solve()
