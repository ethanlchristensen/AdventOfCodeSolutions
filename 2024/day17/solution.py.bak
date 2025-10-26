import os
import re
import math
import time
import multiprocessing

def load_data(name='data'):
    with open(name, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip() != ""]
        program = [int(v) for v in lines[-1].split(": ")[1].split(",")]
        registers = [re.search(r"Register (.)\: (\d+)", line).groups() for line in lines[:-1]]
        registers = {val[0]:int(val[1]) for val in registers}
        return registers, program

def get_ranges(n, nb):
    step = n / nb
    return [(round(step*i), round(step*(i+1))) for i in range(nb)]

def part_one():
    """Code to solve part one"""
    start = time.time()

    registers, program = load_data("data")

    seen = set()
    
    def get_combo_operand(operand):
        if operand in [0,1,2,3]: return operand
        if operand == 4:
            return registers["A"]
        if operand == 5:
            return registers["B"]
        if operand == 6:
            return registers["C"]
        if operand == 7:
            return None

    pointer = 0
    output_values = []
    while True:
        skip_add = False
        opcode = program[pointer]
        operand = program[pointer + 1]
        if opcode == 0:
            numerator = registers["A"]
            combo_operand = get_combo_operand(operand)
            if operand is None: break
            demoninator = 2 ** combo_operand
            registers["A"] = math.trunc(numerator / demoninator)
        elif opcode == 1:
            registers["B"] = registers["B"] ^ operand
        elif opcode == 2:
            combo_operand = get_combo_operand(operand)
            if operand is None: break
            registers["B"] = combo_operand % 8
        elif opcode == 3:
            if registers["A"] != 0:
                pointer = operand
                skip_add = True
        elif opcode == 4:
            registers["B"] = registers["B"] ^ registers["C"]
        elif opcode == 5:
            combo_operand = get_combo_operand(operand)
            if operand is None: break
            value = combo_operand % 8
            output_values.append(value)
        elif opcode == 6:
            numerator = registers["A"]
            combo_operand = get_combo_operand(operand)
            if operand is None: break
            demoninator = 2 ** combo_operand
            registers["B"] = int(numerator / demoninator)
        elif opcode == 7:
            numerator = registers["A"]
            combo_operand = get_combo_operand(operand)
            if operand is None: break
            demoninator = 2 ** combo_operand
            registers["C"] = int(numerator / demoninator)

        if not skip_add:
            pointer += 2
        
        if pointer >= len(program): break

        state = f"{pointer}-{registers['A']}-{registers['B']}-{registers['C']}"
        if state in seen: break
        seen.add(state)

    end = time.time()
    return ",".join([str(v) for v in output_values]), end - start

def run_program(n, program):
    output = []
    while n != 0:
        n = n >> 3
        output.append(n % 8)
        # if output != program[:len(output)]: return None
    return output

def correct_digits(result, program):
    c = 0
    for idx in range(len(program)-1,-1,-1):
        if result[idx] != program[idx]:
            break
        c += 1
    return c

def part_two():
    """Code to solve part 2"""
    start_time = time.time()
    registers, program = load_data("data")
    number_of_digits = len(program)
    start = 8**(number_of_digits - 1)
    end = 8**number_of_digits - 1

    value = start + int((end - start) / 2.5867039189)
    value += (8**8) * 5 - (8**7) * 4 - (8**6 ) * 2 + (8**5) * 4 - (8**4) * 4 - (8**3) * 2 + (8**2) - 8
    
    while run_program(value, program) == program:
        value -= 1
    
    print(value + 1)

    res = run_program(value + 1, program)
    print(program)
    print(res)
    
    end_time = time.time()
    return program, end_time - start_time
    


def solve():
    """Run solutions for part one and two"""
    part_one_answer, part_one_time_to_complete = part_one()

    if part_one_answer:
        print(f"part one: {part_one_answer}\npart one time: {part_one_time_to_complete:.4f}s")

    part_two_answer, part_two_time_to_complete = part_two()
    
    if part_two_answer:
        print(f"part two: {part_two_answer}\npart two time: {part_two_time_to_complete:.4f}s")

if __name__ == '__main__':
    part_two()

