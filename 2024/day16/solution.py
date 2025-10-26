"""
Advent of Code 2024 - Day 16
"""

import os
import re
import math
import time
from heapq import heappush, heappop
from collections import defaultdict


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name="data"):
        with open(name, "r") as file:
            return [list(line.strip()) for line in file.readlines()]


    def part1(self):
        """Code to solve part one"""
        start = time.time()
    
        def solve_maze(self.data, start_point, end_point):
            directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            queue = [(0, start_point[0], start_point[1], 0)]  
            visited = set()
        
            while queue:
                queue.sort(key=lambda x: x[0])
                score, x, y, direction = queue.pop(0)
            
                if (x, y) == end_point:
                    return score
                
                state = (x, y, direction)
                if state in visited:
                    continue
                
                visited.add(state)
            
                dx, dy = directions[direction]
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(self.data[0]) and 0 <= ny < len(self.data) and self.data[ny][nx] != '#':
                    queue.append((score + 1, nx, ny, direction))
            
                new_direction = (direction - 1) % 4
                queue.append((score + 1000, x, y, new_direction))
            
                new_direction = (direction + 1) % 4
                queue.append((score + 1000, x, y, new_direction))
            
            return None

        self.data = self.load_data()
        start_point, end_point = self.find_start_end(self.data)
        total = solve_maze(self.data, start_point, end_point)

        end = time.time()
        return total, end - start


    def part2(self):
        """Code to solve part two"""
        start = time.time()
    
        def solve_maze(self.data, start_point, end_point):
            directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        
            queue = []
            # switch to heapq was expontentially faster than queue.append() and queue.pop(0)
            heappush(queue, (0, start_point[0], start_point[1], 0, [(start_point[0], start_point[1], 0)]))
            visited = set()
            best_score = float("inf")
            best_scores = {}
            best_paths = []
        
            while queue:
                score, x, y, direction, path = heappop(queue)

                if score > 90460: continue

                state = (x, y, direction)

                if state in best_scores and score > best_scores[state]:
                    continue

                best_scores[state] = score
            
                if (x, y) == end_point:
                    if score < best_score:
                        best_score = score
                        best_paths = [path]
                    elif score == best_score:
                        best_paths.append(path)
                    continue

                visited.add(state)
            
                dx, dy = directions[direction]
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(self.data[0]) and 0 <= ny < len(self.data) and self.data[ny][nx] != '#':
                    heappush(queue, (score + 1, nx, ny, direction, path + [(nx, ny, direction)]))
            
                new_direction = (direction - 1) % 4
                heappush(queue, (score + 1000, x, y, new_direction, path + [(x, y, new_direction)]))
            
                new_direction = (direction + 1) % 4
                heappush(queue, (score + 1000, x, y, new_direction, path + [(x, y, new_direction)]))
            
            return best_score, best_paths

        self.data = self.load_data()
        start_point, end_point = self.find_start_end(self.data)
        best_score, best_paths = solve_maze(self.data, start_point, end_point)
        seen_spots = set()

        for path in best_paths:
            # self.data = self.print_path(self.data, path)
            for x, y, _ in path:
                seen_spots.add((x, y))
    
        total = len(seen_spots)

        end = time.time()
        return total, end - start


    def find_start_end(self):
        start = None
        end = None
        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                if self.data[y][x] == "S":
                    start = (x, y)
                if self.data[y][x] == "E":
                    end = (x, y)
                if start is not None and end is not None:
                    return start, end


    def print_path(self, path):
        maze_copy = [row[:] for row in self.data]
        dir_markers = {
            0: '>',
            1: 'v',
            2: '<',
            3: '^'
        }
        for x, y, direction in path:
            if maze_copy[y][x] not in ['S', 'E']:
                maze_copy[y][x] = dir_markers[direction]
        for row in maze_copy:
            print(' '.join(row))
        print()
        return maze_copy


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
