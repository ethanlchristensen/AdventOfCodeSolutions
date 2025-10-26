import re
import itertools

def load_data(name='data'):
    file = open(name, 'r')
    data = file.read()
    file.close()
    rules = [[int(v) for v in match.group().split("|")] for match in re.finditer(pattern=r"\d+\|\d+", string=data)]
    pages = [[int(v) for v in match.group().split(",")] for match in re.finditer(pattern=r"\d+(,\d+)*,\d+", string=data)]
    return rules, pages

def failed_rules(page, rules):
    failed_rules = []
    for rule in rules:
        # if both rule values are in the page
        if rule[0] in page and rule[1] in page:
            # does the first value appear before the second?
            if not page.index(rule[0]) < page.index(rule[1]):
                failed_rules.append(rule)
    return failed_rules

def part_one():
    """
    code to solve part one
    """
    rules, pages = load_data()
    total = 0
    for page in pages:
        # if the page doesn't fail any of the rules, add the middle element to the total
        if not failed_rules(page, rules): total += page[len(page) // 2]
    return total

def part_two():
    """
    code to solve part two
    """
    rules, pages = load_data()
    total = 0
    for page in pages:
        if failed_rules(page, rules):
            # keep swapping failures until there are no failures left
            while failures := failed_rules(page, rules):
                for failed_rule in failures:
                    tmp = page[page.index(failed_rule[0])]
                    page[page.index(failed_rule[0])] = page[page.index(failed_rule[1])]
                    page[page.index(failed_rule[1])] = tmp
            total += page[len(page) // 2]
    return total

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
