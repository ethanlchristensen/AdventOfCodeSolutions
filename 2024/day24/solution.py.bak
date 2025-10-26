import os
import re
import math
import time


def load_data(name='data'):
    with open(name, 'r') as file:
        a, b = file.read().strip().split("\n\n")
        a = {c.split(": ")[0]:int(c.split(": ")[1]) for c in a.split("\n")}
        b = [[v for idx,v in enumerate(c.split(" ")) if idx != 3] for c in b.split("\n")]
        return a, b


def part_one():
    """Code to solve part one"""
    start = time.time()

    regs, ops = load_data("data")

    try_again = []
    idx = 0
    for r1, op, r2, out in ops:
        if r1 in regs and r2 in regs:
            v1 = regs[r1]
            v2 = regs[r2]
            if op == "AND":
                regs[out] = v1 & v2
            elif op == "OR":
                regs[out] = v1 | v2
            else:
                regs[out] = v1 ^ v2
        else:
            try_again.append(idx)
        idx += 1
    
    try_idx = 0
    while len(try_again) > 0:
        r1, op, r2, out = ops[try_again[try_idx]]
        if r1 in regs and r2 in regs:
            v1 = regs[r1]
            v2 = regs[r2]
            if op == "AND":
                regs[out] = v1 & v2
            elif op == "OR":
                regs[out] = v1 | v2
            else:
                regs[out] = v1 ^ v2
            try_again.remove(try_again[try_idx])
        else:
            try_idx += 1
        
        if try_idx >= len(try_again):
            try_idx = 0

    regs = {k:v for k,v in regs.items() if "z" in k}
    regs = sorted(regs.items(), key=lambda x: int(x[0][1:]), reverse=True)
    result = int(''.join(map(str, list([item[1] for item in regs]))), 2)

    end = time.time()
    return result, end - start

def add_binary_numbers(a: str, b: str) -> str:
    max_len = max(len(a), len(b))
    a = a.zfill(max_len)
    b = b.zfill(max_len)
    a_bits = [int(x) for x in a]
    b_bits = [int(x) for x in b]
    result = []
    carry = 0
    for i in range(max_len - 1, -1, -1):
        bit_a = a_bits[i]
        bit_b = b_bits[i]
        sum_without_carry = bit_a ^ bit_b
        sum_bit = sum_without_carry ^ carry
        carry = (bit_a & bit_b) | (carry & (bit_a ^ bit_b))
        result.insert(0, str(sum_bit))
    if carry:
        result.insert(0, '1')
    return ''.join(result)


def part_two(): 
    """Code to solve part two"""
    start = time.time()

    regs, ops = load_data("datasmall3")

    ops = [(op,x,y) for x, op, y, _ in ops]

    print(ops)

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
