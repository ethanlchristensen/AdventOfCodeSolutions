"""
Advent of Code 2023 - Day 6
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
        """
        code to solve part one
        """

        self.data = self.load_data()
        self.data = [list(map(int, re.sub(r' +', ' ', line.split(': ')[1].strip()).split(' '))) for line in self.data]
    
        result = 1
    
        time_record = zip(self.data[0], self.data[1])
    
        for time, record in time_record:
            ways_to_win_race = 0
            for idx in range(1, time):
                if (idx * (time - idx)) > record:
                    ways_to_win_race += 1
            result *= ways_to_win_race
 
        return result



    def part2(self):
        """
        code to solve part two
        """
    
        self.data = self.load_data()
        self.data = [int(line.strip().split(': ')[1].replace(' ', '')) for line in self.data]
            
        ways_to_win_race = 0
        for idx in range(1, self.data[0]//2):
            if (idx * (self.data[0] - idx)) > self.data[1]:
                ways_to_win_race += 2
             
        return ways_to_win_race + 1



    def solve(self):
        """
        code to run part one and part two
        """
        part_one_answer = self.part1()
        part_two_answer = self.part2()

        if part_one_answer:
            print(f"part one: {part_one_answer}")
        if part_two_answer:
            print(f"part two: {part_two_answer}")




if __name__ == "__main__":
    solution = Solution()
    solution.solve()
