import os
import re
import math
import time

directions = [
    (0,1),
    (0,-1),
    (1,0),
    (-1,0),
]

def load_data(name='data', part=1):
    with open(name, 'r') as file:
        lines = file.readlines()
        if part == 2:
            for idx in range(len(lines)-1):
                lines[idx] = lines[idx].replace("#", "##"
                ).replace("O", "[]"
                ).replace(".", ".."
                ).replace("@", "@.")
        data =  [list(line.strip()) for line in lines if line.strip() != ""]
        return data[:-1], data[-1]

def get_direction(char: str):
    if char == "^":
        return (0, -1)
    if char == ">":
        return (1, 0)
    if char == "<":
        return (-1, 0)
    if char == "v":
        return (0, 1)

def get_robot_position(data):
    for y in range(len(data)):
        for x in range(len(data[0])):
            if data[y][x] == "@":
                return (x, y)

def get_gps_coordinates(data):
    total = 0
    for y in range(len(data)):
        for x in range(len(data[0])):
            if data[y][x] in "O[":
                total += (100 * y) + x
    return total

def part_one():
    """Code to solve part one"""
    start = time.time()

    data, moves = load_data()

    for move in moves:
        robot_position = get_robot_position(data)
        can_move = True
        cords_to_move = [robot_position]
        iteration = 0
        dx, dy = get_direction(move)
        while iteration < len(cords_to_move):
            x, y = cords_to_move[iteration]
            nx, ny = x + dx, y + dy
            if data[ny][nx] == "O":
                if (nx, ny) not in cords_to_move:
                    cords_to_move.append((nx, ny))
            elif data[ny][nx] == "#":
                can_move = False
                break
            iteration += 1
        
        if not can_move: continue
        tmp = [[data[y][x] for x in range(len(data[0]))] for y in range(len(data))]
        for x, y in cords_to_move:
            tmp[y][x] = "."
        for x, y in cords_to_move:
            tmp[y+dy][x+dx] = data[y][x]
        data[:] = tmp[:]
    
    total = get_gps_coordinates(data)

    end = time.time()
    return total, end - start

def part_two(): 
    """Code to solve part two"""
    start = time.time()

    total = 0
    
    data, moves = load_data(part=2)

    for move in moves:
        robot_position = get_robot_position(data)
        can_move = True
        cords_to_move = [robot_position]
        iteration = 0
        dx, dy = get_direction(move)
        while iteration < len(cords_to_move):
            x, y = cords_to_move[iteration]
            nx, ny = x + dx, y + dy
            if data[ny][nx] == "O":
                if (nx, ny) not in cords_to_move:
                    cords_to_move.append((nx, ny))
            elif data[ny][nx] in "[]":
                if (nx, ny) not in cords_to_move:
                    cords_to_move.append((nx, ny))
                if data[ny][nx] == "]":
                    addition = (nx - 1, ny)
                    if addition not in cords_to_move:
                        cords_to_move.append(addition)
                elif data[ny][nx] == "[":
                    addition = (nx + 1, ny)
                    if addition not in cords_to_move:
                        cords_to_move.append(addition)
            elif data[ny][nx] == "#":
                can_move = False
                break
            iteration += 1
        
        if not can_move: continue
        tmp = [[data[y][x] for x in range(len(data[0]))] for y in range(len(data))]
        for x, y in cords_to_move:
            tmp[y][x] = "."
        for x, y in cords_to_move:
            tmp[y+dy][x+dx] = data[y][x]
        data[:] = tmp[:]

        # os.system("cls")
        # for row in data:
        #     print(" ".join(row))
        # print()
        # time.sleep(0.2)

    total = get_gps_coordinates(data)

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
