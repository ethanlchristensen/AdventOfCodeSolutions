import os
import re
import math
import time
import tqdm

def load_data(name='data'):
    with open(name, 'r') as file:
        return file.read().strip()

def get_layout(disk_map):
    layout = []
    current_id = 0
    for idx, char in enumerate(disk_map):
        if idx % 2 == 0:
            for _ in range(int(char)):
                layout.append(str(current_id))
            current_id += 1
        else:
            for _ in range(int(char)):
                layout.append(".")
    return layout

def get_open_blocks(disk_layout):
    blocks = []
    current_block = {"start": -1, "end": -1, "length": 0}
    for idx, char in enumerate(disk_layout):
        if char == ".":
            if current_block["start"] == -1:
                current_block["start"] = idx
        else:
            if current_block["start"] != -1 and current_block["end"] == -1:
                current_block["end"] = idx - 1
                current_block["length"] = current_block["end"] - current_block["start"] + 1
                blocks.append(current_block)
                current_block = {"start": -1, "end": -1, "length": 0}
    return blocks

def get_right_most_block(disk_layout, seen_block_values, highest):
    block = {"start": -1, "end": -1, "length": 0, "value": -1}
    for idx in range(len(disk_layout) - 1, -1, -1):
        if  block["end"] == -1 and disk_layout[idx] != "." and ((not seen_block_values and disk_layout[idx] == str(highest)) or disk_layout[idx] == str(int(seen_block_values[-1]) - 1)):
            block["end"] = idx
            block["value"] = disk_layout[idx]
        if block["end"] != -1 and (disk_layout[idx] == "." or disk_layout[idx] != block["value"]):
            block["start"] = idx + 1
            block["length"] = block["end"] - block["start"] + 1
            return block

def part_one():
    """Code to solve part one"""
    start = time.time()
    data = load_data()
    disk_layout = get_layout(data)
    disk_length = len(disk_layout)
    total_periods = disk_layout.count(".")
    current_idx = len(disk_layout) - 1
    while True:
        if disk_length - current_idx == total_periods:
            break
        if disk_layout[current_idx] != ".":
            tmp = disk_layout[current_idx]
            disk_layout[disk_layout.index(".")] = tmp
            disk_layout[current_idx] = "."
        current_idx -= 1
    disk_layout = [char for char in disk_layout if char != "."]
    total = sum([int(char) * idx for idx, char in enumerate(disk_layout) if char != "."])
    end = time.time()
    return total, end - start

def part_two(): 
    """Code to solve part two"""
    start = time.time()
    data = load_data()
    seen_values = []
    disk_layout = get_layout(data)
    lowest_id, highest_id = min([v for v in disk_layout if v != "."]), max([v for v in disk_layout if v != "."])
    while True:
        open_blocks = get_open_blocks(disk_layout=disk_layout)
        next_block = get_right_most_block(disk_layout=disk_layout, seen_block_values=seen_values, highest=highest_id)
                
        if next_block is None:
            break
        
        if next_block["start"] < open_blocks[0]["start"]:
            break

        seen_values.append(next_block["value"])
        for block in open_blocks:
            if block["length"] >= next_block["length"] and block["start"] < next_block["start"]:
                for idx in range(next_block["length"]):
                    tmp = disk_layout[block["start"] + idx]
                    disk_layout[block["start"] + idx] = next_block["value"]
                    disk_layout[next_block["start"] + idx] = tmp
                break
    total = sum([int(char) * idx for idx, char in enumerate(disk_layout) if char != "."])
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
