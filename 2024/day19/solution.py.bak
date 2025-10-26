import os
import re
import math
import time
from tqdm import tqdm

def load_data(name='data'):
    with open(name, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip() != ""]
        rules = lines[0].split(", ")
        towels = lines[1:]
        return rules, towels

memo = {}
def valid(rules, string: str):
    if string not in memo:
        if len(string) == 0:
            return 1
        else:
            total = 0
            for rule in rules:
                if string.startswith(rule):
                    total += valid(rules, string[len(rule):])
                memo[string] = total
    return memo[string]

def part_one():
    """Code to solve part one"""
    start = time.time()

    rules, towels = load_data()

    total = 0

    for towel in towels:
        if valid(rules, towel):
            total += 1
    end = time.time()
    return total, end - start

def part_two(): 
    """Code to solve part two"""
    start = time.time()

    rules, towels = load_data()

    total = 0

    for towel in towels:
        if possible_combinations := valid(rules, towel):
            total += possible_combinations

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
