"""
Advent of Code 2024 - Day 18
"""

import os
import re
import math
import time
from collections import deque
from bruhanimate import Screen, Buffer


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name="data"):
        with open(name, "r") as file:
            return [
                (int(line.split(",")[0]), int(line.split(",")[1]))
                for line in file.readlines()
            ]



    def part1(self):
        """Code to solve part one"""
        start = time.time()
        self.data = self.load_data()
        n = 71
        memory = [["." for _ in range(n)] for _ in range(n)]
        def bfs(memory, seen, row, col):
            q = deque()
            q.append((row, col, []))
            while len(q) > 0:
                x, y, p = q.popleft()
                if x == n - 1 and y == n - 1:
                    return len(p)
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < n and 0 <= ny < n and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        if memory[nx][ny] == ".":
                            q.append((nx, ny, p + [(nx, ny)]))
                            memory[nx][ny] = "0"
                        pass
        for cx, cy in self.data[:1024]:
            memory[cx][cy] = "#"
        total = bfs(memory, set(), 0, 0)
        end = time.time()
        return total, end - start



    def part2(self):
        """Code to solve part two"""
        start = time.time()
        self.data = self.load_data()
        n = 71

        def bfs(memory, seen, row, col):
            q = deque()
            q.append((row, col, []))
            while len(q) > 0:
                x, y, p = q.popleft()
                if x == n - 1 and y == n - 1:
                    return len(p)
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < n and 0 <= ny < n and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        if memory[nx][ny] == ".":
                            q.append((nx, ny, p + [(nx, ny)]))
                            memory[nx][ny] = "0"
                        pass
        erm  = [["." for _ in range(n)] for _ in range(n)]
        for d in self.data:
            xx, yy = d
            erm[xx][yy] = "#"
            total = bfs([[erm[x][y] for x in range(n)] for y in range(n)], set(), 0, 0)
            if total is None:
                total = (xx, yy)
                break
        end = time.time()
        return total, end - start



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
