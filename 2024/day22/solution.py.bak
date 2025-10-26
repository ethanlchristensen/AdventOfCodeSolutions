import os
import re
import math
import time
import json
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

def load_data(name='data'):
    with open(name, 'r') as file:
        return [int(line.strip()) for line in file.readlines() if line.strip() != ""]

def prune(value):
    return value % 16777216

def mix(value, secret):
    value = value ^ secret
    return value

def get_secrets(starting_secret, steps=2000):
    secrets = [starting_secret]
    for _ in range(steps):
        starting_secret = (starting_secret ^ (starting_secret * 64)) % 16777216
        starting_secret = (starting_secret ^ (starting_secret // 32)) % 16777216
        starting_secret = (starting_secret ^ (starting_secret * 2048)) % 16777216
        secrets.append(starting_secret)
    return secrets

def get_prices(secrets):
    return [secret % 10 for secret in secrets]

def get_price_changes(prices):
    return [prices[idx + 1] - prices[idx] for idx in range(len(prices) - 1)]

def find_pattern(values, pattern):
    if len(values) < len(pattern):
        return -1, -1
        
    for i in range(len(values) - len(pattern) + 1):
        if values[i:i+len(pattern)] == pattern:
            return i, (i + len(pattern))
    
    return -1, -1

def part_one():
    """Code to solve part one"""
    start = time.time()

    data = load_data()

    total = 0

    for secret in data:
        total += get_secrets(secret)[-1]

    end = time.time()
    return total, end - start

def part_two(): 
    """Code to solve part two"""
    start = time.time()

    data = load_data()

    best_total = float("-inf")
    best_sequence = []

    buyer_secrets = [get_secrets(secret) for secret in data]
    buyer_prices = [get_prices(price) for price in buyer_secrets]
    buyer_price_changes = [get_price_changes(prices) for prices in buyer_prices]
    buyer_price_change_sequences = {idx:{} for idx in range(len(buyer_price_changes))}
    for idx, buyer_price_change in enumerate(buyer_price_changes):
        for jdx in range(len(buyer_price_change) - 3):
            sequence = tuple(buyer_price_change[jdx:jdx+4])
            if sequence not in buyer_price_change_sequences[idx]:
                buyer_price_change_sequences[idx][sequence] = buyer_prices[idx][jdx+4]

    
    unique_sequences = set()
    for k, v in buyer_price_change_sequences.items():
        for kk, vv in v.items():
            unique_sequences.add(kk)
    unique_sequences = list(unique_sequences)
    df = pd.DataFrame()
    df["A"] = [v[0] for v in unique_sequences]
    df["B"] = [v[1] for v in unique_sequences]
    df["C"] = [v[2] for v in unique_sequences]
    df["D"] = [v[3] for v in unique_sequences]
    for buyer in range(len(data)):
        df[f"buyer_{buyer}"] = [buyer_price_change_sequences[buyer].get(unique_sequences[idx], 0) for idx in range(len(unique_sequences))]
    df["totals"] = df.loc[:, 'buyer_0':'buyer_2390'].sum(axis=1)
    best_total = df["totals"].max()

    # total = 19 * 19 * 19 * 19
    # it = 0
    # for a in range(-9, 10):
    #     for b in range(-9, 10):
    #         for c in range(-9, 10):
    #             for d in range(-9, 10):
    #                 it += 1
    #                 sequence = (a, b, c, d)
    #                 sequence_total = 0
    #                 for idx in range(len(data)):
    #                     sequence_total += buyer_price_change_sequences[idx].get(sequence, 0)
    #                 if sequence_total > best_total:
    #                     best_total = sequence_total
    #                     best_sequence = sequence
    # print(f"Best sequence was {best_sequence} which yielded {best_total} bananas")

    end = time.time()
    return best_total, end - start

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
