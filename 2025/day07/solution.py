"""
Advent of Code 2025 - Day 7
"""

from collections import deque

from functools import lru_cache

from bruhcolor import bruhcolored as bc


class Solution:
    def __init__(self, data_file="data"):
        self.data_file = data_file
        self.data = self.load_data(data_file)
        self.width = len(self.data[0])
        self.height = len(self.data)
        self.start_position = self.find_start()
        self.splitters = set()
        print(f"Height: {self.height}, Width: {self.width}")

    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, "r") as f:
            return [[c for c in line] for line in f.read().strip().split("\n")]

    def find_start(self):
        return (self.data[0].index("S"), 0)

    def print_board(self, board):
        for row in board:
            for val in row:
                if val == 0:
                    print(f"{bc(str(val), 235):^4}", end="")
                elif val == -1:
                    print(f"{bc(str(val), 196):^4}", end="")
                else:
                    print(f"{bc(str(val), val):^4}", end="")
            print()
        print()

    def part1(self):
        """Solve part 1 of the puzzle."""
        board = [[c for c in r] for r in self.data]
        splitters = 0
        for y in range(self.height):
            for x in range(self.width):
                if y + 1 < self.height:
                    cell_below = board[y + 1][x]
                    if cell_below == "." and board[y][x] in "|S":
                        board[y + 1][x] = "|"
                        continue
                    elif cell_below == "^" and board[y][x] == "|":
                        splitters += 1
                        board[y + 1][x] = "#"
                        board[y + 1][x - 1] = "|"
                        board[y + 1][x + 1] = "|"
        # self.print_board(board=board)
        return splitters

    def part2(self):
        """Solve part 2 of the puzzle."""
        # board = [[0 if c == "." else -1 if c == "^" else c for c in r] for r in self.data]

        # moves = deque()

        # sx, sy = self.start_position

        # moves.append((sx, sy))

        # board[sy][sx] = 1

        # while moves:
        #     x, y = moves.popleft()

        #     dx, dy = x, y + 1

        #     if dy >= self.height: continue
        #     if dx < 0 or dx >= self.width: continue

        #     cell = board[dy][dx]

        #     if cell >= 0:
        #         board[dy][dx] = cell + 1
        #         moves.append((dx, dy))
        #     elif cell <= -1:
        #         moves.append((dx - 1, y))
        #         moves.append((dx + 1, y))

        # self.print_board(board)

        # return sum(board[-1])
        paths = [[0] * self.width for _ in range(self.height)]

        sx, sy = self.start_position
        paths[sy][sx] = 1

        for y in range(self.height):
            for x in range(self.width):
                current_paths = paths[y][x]
                if current_paths == 0:
                    continue

                if y + 1 < self.height:
                    cell_below = self.data[y + 1][x]

                    if cell_below == ".":
                        paths[y + 1][x] += current_paths

                    elif cell_below == "^":
                        if x - 1 >= 0:
                            paths[y + 1][x - 1] += current_paths
                        if x + 1 < self.width:
                            paths[y + 1][x + 1] += current_paths
        return sum(paths[-1])

    def solve(self):
        """Run both parts and print results."""
        print(f"Day 7 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
