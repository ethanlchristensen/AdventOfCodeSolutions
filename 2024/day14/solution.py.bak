import os
import re
import math
import time
import pandas as pd
import matplotlib.pyplot as plt
from bruhcolor import bruhcolored as bc

def load_data(name='data'):
    with open(name, 'r') as file:
        data = []
        for line in file.readlines():
            match = re.search(r"p=(.*)\sv=(.*)", line)
            position = [int(v) for v in match.groups()[0].split(",")]
            velocity = [int(v) for v in match.groups()[1].split(",")]
            data.append((tuple(position), tuple(velocity)))
        return data

class Robot:
    def __init__(self, position, velocity, bounds):
        self.previous_position = None
        self.position = position
        self.velocity = velocity
        self.bounds = bounds
    
    def move(self):
        self.previous_position = (self.position[0], self.position[1])
        dx, dy = self.position[0] + self.velocity[0], self.position[1] +  self.velocity[1]
        if not -self.bounds[0] < dx < self.bounds[0]:
            if dx < 0: dx += self.bounds[0]
            else: dx -= self.bounds[0]
        if not -self.bounds[1] < dy < self.bounds[1]:
            if dy < 0: dy += self.bounds[1]
            else: dy -= self.bounds[1]
        self.position = (dx, dy)

    def __str__(self):
        return f"Robot(position={self.position}, velocity={self.velocity})"
    def __repr__(self):
        return f"Robot(position={self.position}, velocity={self.velocity})"

def print_board(board, sleep=0.25):
    os.system("cls")
    for row in board:
        print("".join([bc(text=" ", on_color=255).colored if v != 0 else " " for v in row]))
    print()
    time.sleep(sleep)

def get_quadrant_ranges(width, height):
    mid_width, mid_height = width // 2, height // 2
    return [
        ((0, mid_width), (0, mid_height)),
        ((mid_width + 1, width), (0, mid_height)),
        ((0, mid_width), (mid_height + 1, height)),
        ((mid_width + 1, width), (mid_height + 1, height)),
    ]

def get_quadrant_count(ranges, board):
    total = 0
    for y in range(ranges[1][0], ranges[1][1]):
        total += sum(board[y][ranges[0][0]:ranges[0][1]])
    return total

def part_one():
    """Code to solve part one"""
    start = time.time()

    total = 1
    data = load_data()
    width, height = 101, 103
    quadrants = get_quadrant_ranges(width, height)
    robots = [Robot(position, velocity, (width, height)) for position, velocity in data]
    tile_board = [[0 for _ in range(width)] for _ in range(height)]

    for robot in robots:
        x, y = robot.position
        tile_board[y][x] += 1
    
    # print_board(tile_board)
    for _ in range(1, 101):
        for robot in robots:
            robot.move()
            x, y = robot.position
            px, py = robot.previous_position
            tile_board[y][x] += 1
            tile_board[py][px] -= 1
        # print_board(tile_board)

    for quadrant in quadrants:
        total *= get_quadrant_count(quadrant, tile_board)

    end = time.time()
    return total, end - start

def part_two(): 
    """Code to solve part two"""
    start = time.time()

    total = 1
    data = load_data()
    width, height = 101, 103
    mid_width, mid_height = width // 2, height // 2
    quadrants = get_quadrant_ranges(width, height)
    robots = [Robot(position, velocity, (width, height)) for position, velocity in data]
    tile_board = [[0 for _ in range(width)] for _ in range(height)]

    for robot in robots:
        x, y = robot.position
        tile_board[y][x] += 1

    quadrant_averages = {
        idx: {
            "count": 0,
            "average": 0
        }
        for idx in range(len(quadrants))
    }
    
    df = pd.DataFrame()
    df["second"] = []
    for idx in range(len(quadrants)):
        df[idx] = []
    
    data_frame_data = []

    # print_board(tile_board)
    for _ in range(1, 100000):
        for robot in robots:
            robot.move()
            x, y = robot.position
            px, py = robot.previous_position
            tile_board[y][x] += 1
            tile_board[py][px] -= 1
        if _ > 6750:
            print_board(tile_board)
        if _ == 6771: break
    #     quadrant_values = [get_quadrant_count(q, tile_board) for q in quadrants]
    #     data_frame_data.append([_] + quadrant_values)
    # for quadrant in quadrants:
    #     total *= get_quadrant_count(quadrant, tile_board)
    # df = pd.DataFrame(data=data_frame_data, columns=["second", 0, 1, 2, 3])
    # df.plot(kind="line", x="second", y=[0, 1, 2, 3])
    # plt.show()

    end = time.time()
    return total, end - start

def solve():
    """Run solutions for part one and two"""
    part_one_answer, part_one_time_to_complete = part_one()

    if part_one_answer:
        print(f"part one: {part_one_answer}\npart one time: {part_one_time_to_complete:.4f}s")

    part_two_answer, part_two_time_to_complete = part_two()
    
    if part_two_answer:
        print(f"part two: {part_two_answer}\npart two time: {part_two_time_to_complete:.4f}s")

if __name__ == '__main__':
    solve()
