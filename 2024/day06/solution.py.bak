import os
import re
import time


def load_data(name='data'):
    file = open(name, 'r')
    data = [[c for c in line.strip()] for line in file.readlines()]
    file.close()
    return data

def get_direction(char: str):
    if char == "^":
        return [0, -1]
    if char == ">":
        return [1, 0]
    if char == "<":
        return [-1, 0]
    if char == "v":
        return [0, 1]

def get_next_guard(current_guard):
    if current_guard == "^":
        return ">"
    if current_guard == ">":
        return "v"
    if current_guard == "v":
        return "<"
    if current_guard == "<":
        return "^"

def get_next_position(position, data):
    current_guard = data[position[1]][position[0]]
    direction = get_direction(data[position[1]][position[0]])
    new_position = (position[0] + direction[0], position[1] + direction[1])
    if not 0 <= new_position[0] < len(data[0]) or not 0 <= new_position[1] < len(data):
            data[position[1]][position[0]] = "X"
            return None, data
    if data[new_position[1]][new_position[0]] == "#":
        next_guard = get_next_guard(current_guard)
        data[position[1]][position[0]] = next_guard
        return position, data
    else:
        data[position[1]][position[0]] = "X"
        data[new_position[1]][new_position[0]] = current_guard
        return new_position, data

def get_starting_guard_position(data):
    for y in range(len(data)):
        for x in range(len(data[0])):
            if data[y][x] == "^":
                return (x, y)

def is_loop(data, guard_position, total_chars, debug = False):
    moves = 0
    starting_position = guard_position
    while True:
        new_position, new_data = get_next_position(position=guard_position, data=data)
        if new_position == None:
            data = new_data
            break
        guard_position, data = new_position, new_data
        moves += 1
        if moves > total_chars:
            break
        if guard_position == starting_position and data[new_position[1]][new_position[0]] == "^":
            return True
    return moves > total_chars

def placement_sees_other_blockers(placement_x, placement_y, data):
    for y in range(len(data)):
        if data[y][placement_x] == "#":
            return True
    for x in range(len(data[0])):
        if data[placement_y][x] == "#":
            return True
    return False

def part_one():
    """
    code to solve part one
    """
    data = load_data()
    guard_position = get_starting_guard_position(data=data)
    
    while True:
        new_position, new_data = get_next_position(position=guard_position, data=data)
        if new_position == None:
            data = new_data
            break
        guard_position, data = new_position, new_data
    
    total = 0
    for row in data:
        for char in row:
            if char == "X":
                total += 1
    return total

def part_two():
    """
    code to solve part two
    """
    start = time.time()

    data = load_data()
    guard_position = get_starting_guard_position(data=data)
    
    total_chars = len(data[0]) * len(data)
    
    loops = 0

    for y in range(len(data)):
        for x in range(len(data[0])):
            if placement_sees_other_blockers(x, y, data=data):
                if x == guard_position[0] and y == guard_position[1]:
                    continue
                if data[y][x] == "#":
                    continue

                new_data = [[data[j][i] for i in range(len(data[0]))] for j in range(len(data))]
                new_data[y][x] = "#"

                if is_loop(data=new_data, guard_position=guard_position, total_chars=total_chars): loops += 1

    return loops, time.time() - start

def solve():
    """
    code to run part one and part two
    """
    part_one_answer = part_one()
    part_two_answer, part_two_time = part_two()
    
    if part_one_answer:
        print(f"part one: {part_one_answer}")
    if part_two_answer:
        print(f"part two: Time to complete: {part_two_time}")
        print(f"part two: {part_two_answer}")
    
if __name__ == '__main__':
    """
    code to run solve
    """
    solve()
