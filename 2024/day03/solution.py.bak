
import re

def load_data(name='data'):
    file = open(name, 'r')
    data = file.read()
    file.close()
    return data
    
    
def part_one():
    """
    code to solve part one
    """
    return sum(int(match[0]) * int(match[1]) for match in re.findall(pattern=r'mul\((\d+),(\d+)\)', string=load_data()))

def part_two():
    """
    code to solve part two
    """
    data=[v.group() for v in list(re.finditer(pattern=r'mul\((\d+),(\d+)\)|do\(\)|don\'t\(\)', string=load_data()))];return sum((int(re.search("mul\((?P<a>\d+),(?P<b>\d+)\)", mul).groups()[0]) * int(re.search("mul\((?P<a>\d+),(?P<b>\d+)\)", mul).groups()[1])) for mul in [item for i, item in enumerate(data) if data[i] != "do()" and data[i] != "don't()" and (i < next((idx for idx, val in enumerate(data) if val == "don't()"), len(data)) or any(j < i < k for j in (idx for idx, val in enumerate(data) if val == "do()") for k in [next((idx for idx, val in enumerate(data[j:], j) if val == "don't()"), len(data))]))])
    
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
