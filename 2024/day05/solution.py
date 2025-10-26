"""
Advent of Code 2024 - Day 5
"""

import re
import itertools


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name='data'):
        file = open(name, 'r')
        self.data = file.read()
        file.close()
        rules = [[int(v) for v in match.group().split("|")] for match in re.finditer(pattern=r"\d+\|\d+", string=self.data)]
        pages = [[int(v) for v in match.group().split(",")] for match in re.finditer(pattern=r"\d+(,\d+)*,\d+", string=self.data)]
        return rules, pages


    def part1(self):
        """
        code to solve part one
        """
        rules, pages = self.load_data()
        total = 0
        for page in pages:
            # if the page doesn't fail any of the rules, add the middle element to the total
            if not self.failed_rules(page, rules): total += page[len(page) // 2]
        return total


    def part2(self):
        """
        code to solve part two
        """
        rules, pages = self.load_data()
        total = 0
        for page in pages:
            if self.failed_rules(page, rules):
                # keep swapping failures until there are no failures left
                while failures := self.failed_rules(page, rules):
                    for failed_rule in failures:
                        tmp = page[page.index(failed_rule[0])]
                        page[page.index(failed_rule[0])] = page[page.index(failed_rule[1])]
                        page[page.index(failed_rule[1])] = tmp
                total += page[len(page) // 2]
        return total


    def failed_rules(self, page, rules):
        failed_rules = []
        for rule in rules:
            # if both rule values are in the page
            if rule[0] in page and rule[1] in page:
                # does the first value appear before the second?
                if not page.index(rule[0]) < page.index(rule[1]):
                    failed_rules.append(rule)
        return failed_rules


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
