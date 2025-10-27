"""
Advent of Code 2023 - Day 1
"""


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, 'r') as f:
            return f.read().strip()
    
    def part1(self):
        """
        code to solve part one
        """
        import re;return sum(int(_[0]+_[-1])for l in open('self.data','r')if (_:=re.sub('\D','',l)))


    def part2(self):
        """
        code to solve part two
        """
        import re;return sum(list(map(lambda x:[(vals:=sorted([j for sub in[[(str(val),match.start())for match in re.finditer(key,x)]for key,val in {'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9'}.items()if key in x]for j in sub],key=lambda item:item[1])),int(vals[0][0]+vals[-1][0])][1],open('self.data','r').readlines())))
    

    def solve(self):
        """
        code to run part one and part two
        """
        part_one_answer = self.part1()
        part_two_answer = self.part2()
    
        print(f"part one: {part_one_answer}")
        print(f"part two: {part_two_answer}")
    


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
