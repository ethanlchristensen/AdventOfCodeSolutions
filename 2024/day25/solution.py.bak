import os
import re
import math
import time

def load_data(name='data'):
    with open(name, 'r') as file:
        data = file.read().strip().split("\n\n")
        keys, locks = [], []

        for item in data:
            grid = [list(r) for r in item.split("\n")]
            top_row = [grid[0][x] for x in range(len(grid[0]))]            

            if set(top_row) == {"#"}:
                locks.append(grid)
            else:
                keys.append(grid)
        
        return keys, locks

def part_one():
    """Code to solve part one"""
    start = time.time()

    keys, locks = load_data("data")

    key_schemantics = []
    lock_schemantics = []

    for key in keys:
        key_schmemantic = []
        for x in range(len(key[0])):
            for y in range(len(key)-1,-1,-1):
                if key[y][x] != "#":
                    key_schmemantic.append(len(key) - y - 1)
                    break
        key_schemantics.append(key_schmemantic)
    for lock in locks:
        lock_schemantic = []
        for x in range(len(lock[0])):
            for y in range(len(lock)):
                if lock[y][x] != "#":
                    lock_schemantic.append(y)
                    break
        lock_schemantics.append(lock_schemantic)
    

    def test_key_lock(key, lock, lock_height):
        for kh, lh in zip(key, lock):
            if kh + lh > lock_height:
                return False
        return True
    
    total = 0
    for idx in range(len(key_schemantics)):
        for jdx in range(len(lock_schemantics)):
            if test_key_lock(key_schemantics[idx], lock_schemantics[jdx], len(locks[jdx])):
                total += 1

    end = time.time()
    return total, end - start

def part_two(): 
    """Code to solve part two"""
    start = time.time()

    end = time.time()
    return None, end - start

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
