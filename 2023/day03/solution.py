"""
Advent of Code 2023 - Day 3
"""

import re


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name='data'):
        file = open(name, 'r')
        self.data = [line.strip() for line in file.readlines()]
        file.close()
        return self.data



    def part1(self):

        self.data = self.load_data()

        width, height = len(self.data[0]), len(self.data)

        valid_numbers = []

        for idx, line in enumerate(self.data):
            numbers = [number for number in re.finditer("(\d+)", line)]
            for number_map in numbers:
                number_start = number_map.start()
                number_end = number_map.end()

                number_added = False

                # check diagonally to the left
                if number_start > 0:
                    if self.data[idx][number_start-1] != '.':
                        valid_numbers.append(int(number_map.group()))
                        number_added = True
                    if idx < height-1:
                        if self.data[idx + 1][number_start-1] != '.':
                            valid_numbers.append(int(number_map.group()))
                            continue
                        else:
                            for tmp_idx in range(number_start, number_end):
                                if number_added:
                                    break
                                if self.data[idx+1][tmp_idx] != '.':
                                    valid_numbers.append(int(number_map.group()))
                                    number_added = True
                    if idx > 0:
                        if self.data[idx - 1][number_start-1] != '.':
                            valid_numbers.append(int(number_map.group()))
                            number_added = True
                        else:
                            for tmp_idx in range(number_start, number_end):
                                if number_added:
                                    break
                                if self.data[idx - 1][tmp_idx] != '.':
                                    valid_numbers.append(int(number_map.group()))
                                    number_added = True

                # check diagonally to the right
                if number_end < width - 1:
                    if self.data[idx][number_end] != '.':
                        valid_numbers.append(int(number_map.group()))
                        number_added = True
                    if idx < height-1:
                        if self.data[idx + 1][number_end] != '.':
                            valid_numbers.append(int(number_map.group()))
                            number_added = True
                        else:
                            for tmp_idx in range(number_start, number_end):
                                if number_added:
                                    break
                                if self.data[idx+1][tmp_idx] != '.':
                                    valid_numbers.append(int(number_map.group()))
                                    number_added = True
                    if idx > 0:
                        if self.data[idx - 1][number_end] != '.':
                            valid_numbers.append(int(number_map.group()))
                            number_added = True
                        else:
                            for tmp_idx in range(number_start, number_end):
                                if number_added:
                                    break
                                if self.data[idx-1][tmp_idx] != '.':
                                    valid_numbers.append(int(number_map.group()))
                                    number_added = True

        return sum(valid_numbers)



    def part2(self):

        directions = [
            [0, 1],
            [1, 0],
            [0, -1],
            [-1, 0],
            [1, 1],
            [1, -1],
            [-1, 1],
            [-1, -1],
        ]

        self.data = self.load_data()

        sum = 0

        gear_locations = set()
        number_locations = set()

        def get_gear_neighbors_product(gear, neighbors):

            output = []

            # get the set of valid gear coords. this is
            # the 8 cells that surround the gear.
            valid_gear_cords = [
                (gear[0] + direction[0], gear[1] + direction[1]) 
                for direction in directions
            ]

            for neighbor in neighbors:
                # create the range of (x, y) coordinates that make
                # up the number
                valid_neighbor_cords = [
                    (x, neighbor[2])
                    for x in range(neighbor[0], neighbor[1])
                ]
            
                # if a number coordinate is in the valid gear coordniates
                # then the gear is adjacent to this unique number
                for valid_neighbor_cord in valid_neighbor_cords:
                    if valid_neighbor_cord in valid_gear_cords:
                        output.append(int(neighbor[3]))
                        break
                
            # if the gear had only two adjacent numbers
            # return the product, otherwise 0     
            if len(output) == 2:
                return(output[0] * output[1])
            return 0
    
        # loop through input and get the gear and number
        # locations.
        for idx, line in enumerate(self.data):
            for gear in re.finditer("\*", line):
                gear_locations.add((gear.start(), idx))
            for digit in re.finditer("\d+", line):
                number_locations.add(
                    (digit.start(), digit.end(), idx, digit.group(0)))
    
        # for each gear, get the product of it's two 
        # adjacent numbers (or 0 if there aren't two)
        for gear in gear_locations:
            sum += get_gear_neighbors_product(gear, number_locations)

        return sum



    def solve(self):
        part_one_answer = self.part1()
        part_two_answer = self.part2()

        print(f"part one: {part_one_answer}")
        print(f"part two: {part_two_answer}")




if __name__ == "__main__":
    solution = Solution()
    solution.solve()
