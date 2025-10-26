"""
Advent of Code 2024 - Day 20
"""

import os
import re
import math
import time
from collections import deque as queue
from bruhcolor import bruhcolored as bc


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name='data'):
        with open(name, 'r') as file:
            return [list(line.strip()) for line in file.readlines()]
    

    def part1(self):
        """Code to solve part one"""
        start = time.time()

        self.data = self.load_data()

        total = 0

        sx, sy = -1, -1
        ex, ey = -1, -1
        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                if self.data[y][x] == "S":
                    sx, sy = x, y
                if self.data[y][x] == "E":
                    ex, ey = x, y
    
        def bfs(board, sx, sy):
            seen = set()
            q = queue()
            q.append((sx, sy, [(sx, sy)]))

            while len(q) > 0:
                x, y, p = q.popleft()
                if x == ex and y == ey:
                    return p
                for dx, dy in [(0,1),(1,0),(-1,0),(0,-1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < len(self.data[0]) and 0 <= ny < len(self.data) and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        if board[ny][nx] in ".EAB":
                            if board[ny][nx] == "B":
                                if board[y][x] != ".":
                                    continue
                            if board[ny][nx] == "B":
                                if board[y][x] != "A":
                                    continue
                            q.append((nx, ny, p + [(nx, ny)]))

        path = bfs(self.data, sx, sy)
        base_picoseconds = len(path)
        saved_picosecond_hits = {}

        for y in range(len(self.data) - 1):
            for x in range(len(self.data[0]) - 1):
                c1 = (x, y)
                c2 = (x, y + 1)
                nb = [[self.data[y][x] for x in range(len(self.data[0]))] for y in range(len(self.data))]
                nb[c1[1]][c1[0]] = "A"
                nb[c2[1]][c2[0]] = "B"
                path = bfs(nb, sx, sy)
                if path and len(path) < base_picoseconds:
                    difference = base_picoseconds - len(path)
                    if difference in saved_picosecond_hits:
                        saved_picosecond_hits[difference] += 1
                    else:
                        saved_picosecond_hits[difference] = 1

        for y in range(len(self.data) - 1):
            for x in range(len(self.data[0]) - 1):
                c1 = (x, y)
                c2 = (x + 1, y)
                nb = [[self.data[y][x] for x in range(len(self.data[0]))] for y in range(len(self.data))]
                nb[c1[1]][c1[0]] = "A"
                nb[c2[1]][c2[0]] = "B"
                path = bfs(nb, sx, sy)
                if path and len(path) < base_picoseconds:
                    difference = base_picoseconds - len(path)
                    if difference in saved_picosecond_hits:
                        saved_picosecond_hits[difference] += 1
                    else:
                        saved_picosecond_hits[difference] = 1   
    
        for k, v in saved_picosecond_hits.items():
            if k > 99:
                total += v

        end = time.time()
        return total, end - start


    def part2(self):
        """Code to solve part two"""
        start = time.time()

        self.data = self.load_data()

        total = 0

        sx, sy = -1, -1
        ex, ey = -1, -1
        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                if self.data[y][x] == "S":
                    sx, sy = x, y
                if self.data[y][x] == "E":
                    ex, ey = x, y
    
        def bfs(board, sx, sy, max_cheat_duration=0):
            seen = set()
            q = queue([(sx, sy, [], max_cheat_duration)])  # (x, y, path, remaining cheat time)
            seen.add((sx, sy, max_cheat_duration))

            while q:
                x, y, path, cheat_time = q.popleft()
                if (x, y) == (ex, ey):
                    return path
            
                for dx, dy in [(0,1),(1,0),(-1,0),(0,-1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < len(self.data[0]) and 0 <= ny < len(self.data) and (nx, ny, cheat_time) not in seen:
                        if board[ny][nx] == "#" and cheat_time > 0:  # Wall, but we can cheat through it
                            q.append((nx, ny, path + [(nx, ny)], cheat_time - 1))
                            seen.add((nx, ny, cheat_time - 1))
                        elif board[ny][nx] != "#":  # Valid track, no need to cheat
                            q.append((nx, ny, path + [(nx, ny)], cheat_time))
                            seen.add((nx, ny, cheat_time))
            return None

        base_picoseconds = len(bfs(self.data, sx, sy))

        saved_picosecond_hits = {}

        # Try all possible cheating durations from 1 to 20
        for cheat_time in range(1, 21):
            for y in range(len(self.data) - 1):
                for x in range(len(self.data[0]) - 1):
                    c1 = (x, y)
                    c2 = (x, y + 1)
                    nb = [list(row) for row in self.data]
                    nb[c1[1]][c1[0]] = "A"
                    nb[c2[1]][c2[0]] = "B"
                    path = bfs(nb, sx, sy, max_cheat_duration=cheat_time)
                    if path and len(path) < base_picoseconds:
                        difference = base_picoseconds - len(path)
                        if difference in saved_picosecond_hits:
                            saved_picosecond_hits[difference] += 1
                        else:
                            saved_picosecond_hits[difference] = 1

        for k, v in saved_picosecond_hits.items():
            if k > 99:
                total += v

        end = time.time()
        return total, end - start


    def print_path(self, s, e, path):
        sx, sy = s
        ex, ey = e
        self.data[sy][sx] = bc("  ", 255, 72).colored
        self.data[ey][ex] = bc("  ", 255, 196).colored
        for row in self.data:
            print("".join(row).replace(".", "  ").replace("#", bc("  ", None, 255).colored).replace("A", bc("  ", None, 208).colored).replace("B", bc("  ", None, 125).colored))

        for idx, (x, y) in enumerate(path):
            self.data[y][x] = bc("  ", None, 27).colored
            # os.system("cls")
            # for row in self.data:
            #     print("".join(row).replace(".", "  ").replace("#", bc("  ", None, 255).colored).replace("A", bc("  ", None, 208).colored).replace("B", bc("  ", None, 125).colored))
            # print()
            # time.sleep(0.02)
        os.system("cls")
        for row in self.data:
            print("".join(row).replace(".", "  ").replace("#", bc("  ", None, 255).colored).replace("A", bc("  ", None, 208).colored).replace("B", bc("  ", None, 125).colored))
        print()


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
