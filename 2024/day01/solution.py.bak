
import re
import numpy as np

def load_data(name='data'):
    file = open(name, 'r')
    data = [line.strip() for line in file.readlines()]
    file.close()
    l1 = []
    l2 = []
    for line in data:
        vals = line.split("   ")
        l1.append(int(vals[0]))
        l2.append(int(vals[1]))
    return l1, l2
     
def part_one():
    """
    code to solve part one
    """
    return sum([abs(a - b) for a, b in zip(*load_data())])

def part_two():
    """
    code to solve part two
    """
    return sum([num * load_data()[1].count(num) for num in load_data()[0]])
    
def solve():
    """
    code to run part one and part two
    """
    part_one_answer = part_one()
    part_two_answer = part_two()
    
    if part_one_answer:
        print(f"part one: {part_one_answer}")
    if part_two_answer:
        print(f"part two: {part_two_answer}")
    
if __name__ == '__main__':
    """
    code to run solve
    """
    solve()
