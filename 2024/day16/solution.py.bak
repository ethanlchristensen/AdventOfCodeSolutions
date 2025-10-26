import os
import re
import math
import time
from heapq import heappush, heappop
from collections import defaultdict


def load_data(name="data"):
    with open(name, "r") as file:
        return [list(line.strip()) for line in file.readlines()]

def find_start_end(data):
    start = None
    end = None
    for y in range(len(data)):
        for x in range(len(data[0])):
            if data[y][x] == "S":
                start = (x, y)
            if data[y][x] == "E":
                end = (x, y)
            if start is not None and end is not None:
                return start, end

def part_one():
    """Code to solve part one"""
    start = time.time()
    
    def solve_maze(data, start_point, end_point):
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
            if 0 <= nx < len(data[0]) and 0 <= ny < len(data) and data[ny][nx] != '#':
                queue.append((score + 1, nx, ny, direction))
            
            new_direction = (direction - 1) % 4
            queue.append((score + 1000, x, y, new_direction))
            
            new_direction = (direction + 1) % 4
            queue.append((score + 1000, x, y, new_direction))
            
        return None

    data = load_data()
    start_point, end_point = find_start_end(data)
    total = solve_maze(data, start_point, end_point)

    end = time.time()
    return total, end - start

def print_path(data, path):
    maze_copy = [row[:] for row in data]
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

def part_two():
    """Code to solve part two"""
    start = time.time()
    
    def solve_maze(data, start_point, end_point):
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
            if 0 <= nx < len(data[0]) and 0 <= ny < len(data) and data[ny][nx] != '#':
                heappush(queue, (score + 1, nx, ny, direction, path + [(nx, ny, direction)]))
            
            new_direction = (direction - 1) % 4
            heappush(queue, (score + 1000, x, y, new_direction, path + [(x, y, new_direction)]))
            
            new_direction = (direction + 1) % 4
            heappush(queue, (score + 1000, x, y, new_direction, path + [(x, y, new_direction)]))
            
        return best_score, best_paths

    data = load_data()
    start_point, end_point = find_start_end(data)
    best_score, best_paths = solve_maze(data, start_point, end_point)
    seen_spots = set()

    for path in best_paths:
        # data = print_path(data, path)
        for x, y, _ in path:
            seen_spots.add((x, y))
    
    total = len(seen_spots)

    end = time.time()
    return total, end - start

def solve():
    """Run solutions for part one and two"""
    part_one_answer, part_one_time_to_complete = part_one()

    if part_one_answer:
        print(
            f"part one: {part_one_answer}\npart one time: {part_one_time_to_complete:.4f}s"
        )

    part_two_answer, part_two_time_to_complete = part_two()

    if part_two_answer:
        print(
            f"part two: {part_two_answer}\npart two time: {part_two_time_to_complete:.4f}s"
        )

if __name__ == "__main__":
    solve()
