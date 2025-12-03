"""
Advent of Code 2025 - Day 2
"""

from sympy import divisors

class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, 'r') as f:
            return f.read().strip()
            
    def part1(self):
        """Solve part 1 of the puzzle."""
        return sum([0 if (len(str(v))%2!=0 or(str(v)[len(str(v))//2:]!=str(v)[:len(str(v))//2]))else v for l in[list(range(a,b+1))for a,b in[list(map(int, r.split("-")))for r in self.data.split(",")]]for v in l])
    
    def part2(self):
        """Solve part 2 of the puzzle."""
        total = 0

        ids = [list(map(int, r.split("-")))for r in self.data.split(",")]

        for low, high in ids:
            for val in range(low, high + 1):
                cs, csl = str(val), len(str(val))

                if csl == 1: continue
                
                divs = divisors(csl)[1:-1]

                if len(divs) == 0:
                    if cs.count(cs[0]) == csl:
                        total += val
                else:
                    for chunk_size in divs:
                        section = cs[:chunk_size]
                        if all(cs[i:i+chunk_size] == section for i in range(0, csl, chunk_size)):
                            total += val
                            break
        return total
    
    def solve(self):
        """Run both parts and print results."""
        print(f"Day 2 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
