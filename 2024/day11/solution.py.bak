import os
import re
import math
import time
import tqdm

total = 0
erm = {}
mock_total = 0

def load_data(name="data"):
    with open(name, 'r') as file:
        return [int(v) for v in file.read().strip().split(" ")]

def predict_growth(number, steps, memo=None):
    if memo is None:
        memo = {}

    key = (number, steps)

    if key in memo:
        return memo[key]

    if steps == 0:
        memo[key] = 1
        return 1
    
    if number == 0:
        sub_total = predict_growth(1, steps - 1, memo)
        memo[key] = sub_total
        return sub_total

    nstr = str(number)
    if len(nstr) % 2 == 0:
        left = int(nstr[:len(nstr)//2])
        right = int(nstr[len(nstr)//2:])
        sub_total = predict_growth(left, steps - 1, memo) + predict_growth(right, steps - 1, memo)
        memo[key] = sub_total
        return sub_total
    
    sub_total = predict_growth(number * 2024, steps - 1, memo)
    memo[key] = sub_total
    return sub_total

def part_one():
    """Code to solve part one"""
    start = time.time()
    data = load_data()
    blinks = 25
    total = 0
    
    for number in data:
        total += predict_growth(number, blinks)

    end = time.time()
    return total, end - start

def part_two():
    start = time.time()
    data = load_data()
    blinks = 75
    total = 0

    for number in data:
        total += predict_growth(number, blinks)
        
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
