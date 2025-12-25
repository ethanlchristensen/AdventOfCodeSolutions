"""
Advent of Code 2025 - Day 8
"""

import math
import networkx as nx
import numpy as np
from scipy.spatial import KDTree


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)

    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, "r") as f:
            return [
                tuple((int(v) for v in l.split(",")))
                for l in f.read().strip().split("\n")
            ]

    def distance(self, p1, p2):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(p1, p2)))

    def part1(self):
        """Solve part 1 of the puzzle."""
        points = self.data
        edges = []
        seen = set()
        circuits = {}
        ptcm = {}
        connections = 0

        for i, p in enumerate(points):
            circuits[i] = [p]
            ptcm[p] = i

        for i, start in enumerate(points):
            neighbors = [p for p in points if p != start]
            for n in neighbors:
                if (start, n) not in seen and (n, start) not in seen:
                    edges.append(((start, n), self.distance(start, n)))
                    seen.add((start, n))

        edges.sort(key=lambda x: x[1])

        for pair, _ in edges[:1000]:
            start, end = pair

            start_id = ptcm[start]
            end_id = ptcm[end]

            if start_id == end_id:
                continue

            end_points = circuits[end_id]

            for p in end_points:
                ptcm[p] = start_id
                circuits[start_id].append(p)

            circuits[end_id] = []

        circuit_sizes = [len(v) for k, v in circuits.items() if len(v)]
        circuit_sizes.sort(reverse=True)
        return circuit_sizes[0] * circuit_sizes[1] * circuit_sizes[2]

    def part2(self):
        """Solve part 2 of the puzzle."""
        points = self.data
        edges = []
        seen = set()
        circuits = {}
        ptcm = {}
        connections = 0

        for i, p in enumerate(points):
            circuits[i] = [p]
            ptcm[p] = i

        for i, start in enumerate(points):
            neighbors = [p for p in points if p != start]
            for n in neighbors:
                if (start, n) not in seen and (n, start) not in seen:
                    edges.append(((start, n), self.distance(start, n)))
                    seen.add((start, n))

        edges.sort(key=lambda x: x[1])

        for pair, _ in edges:
            start, end = pair

            start_id = ptcm[start]
            end_id = ptcm[end]

            if start_id == end_id:
                continue

            end_points = circuits[end_id]

            for p in end_points:
                ptcm[p] = start_id
                circuits[start_id].append(p)

            del circuits[end_id]

            if len(circuits) == 1:
                return start[0] * end[0]

        circuit_sizes = [len(v) for k, v in circuits.items() if len(v)]
        circuit_sizes.sort(reverse=True)
        return circuit_sizes[0] * circuit_sizes[1] * circuit_sizes[2]

    def solve(self):
        """Run both parts and print results."""
        print(f"Day 8 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
