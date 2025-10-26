import os
import re
import math
import time
import itertools


def load_data(name="data"):
    with open(name, "r") as file:
        return [
            [int(v) for v in line.replace(":", "").split(" ")]
            for line in file.readlines()
        ]

def get_all_operations_1(n):
    return list(itertools.product((0, 1), repeat=n))

def get_all_operations_2(n):
    return list(itertools.product((0, 1, 2), repeat=n))

def part_one():
    """Code to solve part one"""
    data = load_data()
    total = 0

    for calibration in data:
        target = calibration[0]
        values = calibration[1:]
        for operation_group in get_all_operations_1(len(values) - 1):
            erm = values[0]
            for idx, operation in enumerate(operation_group):
                if operation == 1:
                    erm += values[idx + 1]
                elif operation == 0:
                    erm *= values[idx + 1]
                if erm > target:
                    break
            if erm == target:
                total += target
                break

    return total

def part_two():
    """Code to solve part two"""
    data = load_data()
    total = 0

    for calibration in data:
        target = calibration[0]
        values = calibration[1:]
        operation_groups = get_all_operations_2(len(values) - 1)
        for operation_group in operation_groups:
            erm = values[0]
            for idx, operation in enumerate(operation_group):
                if operation == 2:
                    erm = int(str(erm) + str(values[idx + 1]))
                elif operation == 1:
                    erm *= values[idx + 1]
                elif operation == 0:
                    erm += values[idx + 1]
                if erm > target:
                    break
            if erm == target:
                total += target
                break
    return total


def solve():
    """Run solutions for part one and two"""
    part_one_answer = part_one()

    if part_one_answer:
        print(f"part one: {part_one_answer}")

    part_two_answer = part_two()

    if part_two_answer:
        print(f"part two: {part_two_answer}")


if __name__ == "__main__":
    solve()
