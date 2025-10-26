"""
Advent of Code 2024 - Day 4
"""

PRINT_BOARD = False

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
        if PRINT_BOARD:
            print(f"{'=' * 20} PART ONE {'=' * 20}")

        self.data = self.load_data()
    
        directions = [
            [1,0],
            [0,1],
            [-1,0],
            [0,-1],
            [1,1],
            [-1,-1],
            [-1,1],
            [1,-1]
        ]
    
        # to keep track of what we have found so far
        locks = [[" " for _ in range(len(self.data[0]))] for _ in range(len(self.data))]

        # debug_tracker can be any value
        def check_dir(s, x, y, dir, debug_tracker = None):
            # did we find XMAS?
            if s == "XMAS":
                # place into the lock board the characters that made up the word XMAS
                if debug_tracker: print(f"s={s} is goated for being XMAS!")
                lock_x, lock_y = x, y
                locks[y][x] = s[-1]
                for _ in range(2, 5):
                    lock_x += -dir[0]
                    lock_y += -dir[1]
                    locks[lock_y][lock_x] = s[-_]
                return 1
        
            if debug_tracker: print(f"Recieved: ({x}, {y}), {s} --> Checking: ({x + dir[0]}, {y + dir[1]}), {self.data[y+dir[1]][x+dir[0]]}")

            # no point in looking if we are past 4 chars
            if len(s) > 4:
                return 0
        
            # no point in looking if we are going to be out of bounds
            if not 0 <= y + dir[1] < len(self.data) or not 0 <= x + dir[0] < len(self.data[0]):
                if debug_tracker: print("erm, we outta bounds pal.")
                return 0

            # is it possible our string could still be XMAS?
            if s in "XMAS":
                if debug_tracker: print(f"'{s}' is in XMAS, lets look some more!")
                return check_dir(s + self.data[y + dir[1]][x + dir[0]], x + dir[0], y + dir[1], dir, debug_tracker=debug_tracker)
        
            return 0

        total = 0
        debug = False
        debug_target = (3, 9) # was giving me problems
        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                for dir in directions:
                    if x == debug_target[0] and y == debug_target[1] and dir == [-1, -1]:
                        total += check_dir(s=self.data[y][x], x=x, y=y, dir=dir, debug_tracker=1 if debug else None)
                    else:
                        total += check_dir(s=self.data[y][x], x=x, y=y, dir=dir, debug_tracker=None)

        # print out what we found
        if PRINT_BOARD:
            print("\nTHE BOARD:")
            self.print_board(board=locks)

        return total


    def part2(self):
        """
        code to solve part two
        """
        if PRINT_BOARD:
            print(f"{'=' * 20} PART TWO {'=' * 20}")

        self.data = self.load_data()
    
        # only check corners
        d1 = [
            [-1, -1],
            [1, 1]
        ]
        d2 = [
            [-1, 1],
            [1, -1]
        ]
    
        # to keep track of what we have found so far
        locks = [[" " for _ in range(len(self.data[0]))] for _ in range(len(self.data))]

        def star_out(x, y):
            # check d1 - does this first diagonal make 'MAS'?
            if (self.data[y + d1[0][1]][x + d1[0][0]] == "M" and self.data[y + d1[1][1]][x + d1[1][0]] == "S") or (self.data[y + d1[0][1]][x + d1[0][0]] == "S" and self.data[y + d1[1][1]][x + d1[1][0]] == "M"):
                # check d2 - does this second diagonal make 'MAS'?
                if (self.data[y + d2[0][1]][x + d2[0][0]] == "M" and self.data[y + d2[1][1]][x + d2[1][0]] == "S") or (self.data[y + d2[0][1]][x + d2[0][0]] == "S" and self.data[y + d2[1][1]][x + d2[1][0]] == "M"):
                    # add to the locks array for printing out later
                    locks[y][x] = self.data[y][x]
                    locks[y + d1[0][1]][x + d1[0][0]] = self.data[y + d1[0][1]][x + d1[0][0]]
                    locks[y + d1[1][1]][x + d1[1][0]] = self.data[y + d1[1][1]][x + d1[1][0]]
                    locks[y + d2[0][1]][x + d2[0][0]] = self.data[y + d2[0][1]][x + d2[0][0]]
                    locks[y + d2[1][1]][x + d2[1][0]] = self.data[y + d2[1][1]][x + d2[1][0]]
                    return 1
            return 0

        total = 0
        for y in range(1, len(self.data) - 1):
            for x in range(1, len(self.data[0]) - 1):
                # we only need to look at the a values since they are the intersection of two 'MAS'
                if self.data[y][x] == "A":
                    total += star_out(x, y)

        # print out what we found
        if PRINT_BOARD:
            print("\nTHE BOARD:")
            self.print_board(board=locks)

        return total
    

    def print_board(self, board):
        for idx in range(len(board)):
            board[idx] = "| " + " ".join(board[idx]) + " |"
        print("+" + "-"*(len(board[0])-2) + "+")
        for row in board:
            print(row)
        print("+" + "-"*(len(board[0])-2) + "+\n")


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
