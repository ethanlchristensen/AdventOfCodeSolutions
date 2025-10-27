"""
Advent of Code 2023 - Day 4
"""

import time


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
    
        day_4_sum = 0
    
        for card in self.data:
            card_data = card.split(': ')[1].split(' | ')
            winning_numbers = [num for num in card_data[0].split(' ') if num != '']
            card_numbers = [num for num in card_data[1].split(' ') if num != '']
        
            card_score = 0
        
            for card_number in card_numbers:            
                if card_number in winning_numbers:
                    if card_score > 0:
                        card_score *= 2
                    else:
                        card_score += 1

            day_4_sum += card_score

        return day_4_sum



    def part2(self):
    
        self.data = self.load_data()
    
        start = time.time_ns()
    
        mapping = [1 for _ in range(len(self.data))]
    
        for idx, card in enumerate(self.data):
            matching_numbers = ((x:=card.split(': ')[1].split(' | ')), len(set(x[0].split()).intersection(set(x[1].split()))))[1]
            for _ in range(idx + 1, idx + matching_numbers + 1):
                mapping[_] = mapping[_] + mapping[idx]
    
        total = sum(mapping)
    
        total_time = time.time_ns() - start
    
        return total, total_time
        


    def solve(self):
        part_one_answer = self.part1()
        part_two_answer, time_to_run = self.part2()
    
        print(f'part one: {part_one_answer}')
        print(f'part two: {part_two_answer}')




if __name__ == "__main__":
    solution = Solution()
    solution.solve()
