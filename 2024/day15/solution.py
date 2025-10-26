"""
Advent of Code 2024 - Day 15
"""

import os
import re
import math
import time


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name='data', part=1):
        with open(name, 'r') as file:
            lines = file.readlines()
            if part == 2:
                for idx in range(len(lines)-1):
                    lines[idx] = lines[idx].replace("#", "##"
                    ).replace("O", "[]"
                    ).replace(".", ".."
                    ).replace("@", "@.")
            self.data =  [list(line.strip()) for line in lines if line.strip() != ""]
            return self.data[:-1], self.data[-1]


    def part1(self):
        """Code to solve part one"""
        start = time.time()

        self.data, moves = self.load_data()

        for move in moves:
            robot_position = self.get_robot_position(self.data)
            can_move = True
            cords_to_move = [robot_position]
            iteration = 0
            dx, dy = self.get_direction(move)
            while iteration < len(cords_to_move):
                x, y = cords_to_move[iteration]
                nx, ny = x + dx, y + dy
                if self.data[ny][nx] == "O":
                    if (nx, ny) not in cords_to_move:
                        cords_to_move.append((nx, ny))
                elif self.data[ny][nx] == "#":
                    can_move = False
                    break
                iteration += 1
        
            if not can_move: continue
            tmp = [[self.data[y][x] for x in range(len(self.data[0]))] for y in range(len(self.data))]
            for x, y in cords_to_move:
                tmp[y][x] = "."
            for x, y in cords_to_move:
                tmp[y+dy][x+dx] = self.data[y][x]
            self.data[:] = tmp[:]
    
        total = self.get_gps_coordinates(self.data)

        end = time.time()
        return total, end - start


    def part2(self): 
        """Code to solve part two"""
        start = time.time()

        total = 0
    
        self.data, moves = self.load_data(part=2)

        for move in moves:
            robot_position = self.get_robot_position(self.data)
            can_move = True
            cords_to_move = [robot_position]
            iteration = 0
            dx, dy = self.get_direction(move)
            while iteration < len(cords_to_move):
                x, y = cords_to_move[iteration]
                nx, ny = x + dx, y + dy
                if self.data[ny][nx] == "O":
                    if (nx, ny) not in cords_to_move:
                        cords_to_move.append((nx, ny))
                elif self.data[ny][nx] in "[]":
                    if (nx, ny) not in cords_to_move:
                        cords_to_move.append((nx, ny))
                    if self.data[ny][nx] == "]":
                        addition = (nx - 1, ny)
                        if addition not in cords_to_move:
                            cords_to_move.append(addition)
                    elif self.data[ny][nx] == "[":
                        addition = (nx + 1, ny)
                        if addition not in cords_to_move:
                            cords_to_move.append(addition)
                elif self.data[ny][nx] == "#":
                    can_move = False
                    break
                iteration += 1
        
            if not can_move: continue
            tmp = [[self.data[y][x] for x in range(len(self.data[0]))] for y in range(len(self.data))]
            for x, y in cords_to_move:
                tmp[y][x] = "."
            for x, y in cords_to_move:
                tmp[y+dy][x+dx] = self.data[y][x]
            self.data[:] = tmp[:]

            # os.system("cls")
            # for row in self.data:
            #     print(" ".join(row))
            # print()
            # time.sleep(0.2)

        total = self.get_gps_coordinates(self.data)

        end = time.time()
        return total, end - start


    def get_direction(self, char: str):
        if char == "^":
            return (0, -1)
        if char == ">":
            return (1, 0)
        if char == "<":
            return (-1, 0)
        if char == "v":
            return (0, 1)


    def get_robot_position(self):
        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                if self.data[y][x] == "@":
                    return (x, y)


    def get_gps_coordinates(self):
        total = 0
        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                if self.data[y][x] in "O[":
                    total += (100 * y) + x
        return total


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
