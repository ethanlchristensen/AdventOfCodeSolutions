"""
Advent of Code 2025 - Day 8
"""

import math
import networkx as nx
import numpy as np
from scipy.spatial import KDTree


class Solution:
    def __init__(self, data_file="datasmall"):
        self.data = self.load_data(data_file)

    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, "r") as f:
            return [
                tuple((int(v) for v in l.split(",")))
                for l in f.read().strip().split("\n")
            ]

    def part1(self):
        """Solve part 1 of the puzzle."""
        # points = np.array(self.data)
        # kdtree = KDTree(points)

        # circuits = {}
        # point_to_circuit_mapping = {}

        # points_to_map = [p for p in self.data]

        # while points_to_map:
        #     closest_neighbors = {}
        #     for point in points_to_map:
        #         distances, indexes = kdtree.query(np.array(point), k=2)
        #         closest_distance, closest_index = distances[1], indexes[1]
        #         closest_neighbors[point] = (closest_distance, closest_index)
        #     closest_neighbors = sorted(closest_neighbors.items(), key=lambda x: x[1][0])

        #     item_to_connect_point, (distance, point_to_connect_to_idx) = closest_neighbors[0]

        #     if item_to_connect_point not in point_to_circuit_mapping and self.data[point_to_connect_to_idx] not in point_to_circuit_mapping:
        #         circuit_idx = len(circuits)
        #         circuits[circuit_idx] = [item_to_connect_point, self.data[point_to_connect_to_idx]]
        #         point_to_circuit_mapping[item_to_connect_point] = circuit_idx
        #         point_to_circuit_mapping[self.data[point_to_connect_to_idx]] = circuit_idx
        #         points_to_map.remove(item_to_connect_point)
        #         points_to_map.remove(self.data[point_to_connect_to_idx])
        #     elif item_to_connect_point not in point_to_circuit_mapping:
        #         circuit_idx = point_to_circuit_mapping[self.data[point_to_connect_to_idx]]
        #         circuits[circuit_idx].append(item_to_connect_point)
        #         point_to_circuit_mapping[item_to_connect_point] = circuit_idx
        #         points_to_map.remove(item_to_connect_point)

        # sorted_circuits = sorted(circuits.items(), key=lambda x: len(x[1]), reverse=True)

        # print(f"We have {len(sorted_circuits)} total circuits.")
        # for idx, circuit_data in enumerate(sorted_circuits):
        #     circuit_idx, points = circuit_data
        #     print(f"Circuit {circuit_idx} is {points}")

        # total = 1

        # for idx, circuit_data in enumerate(sorted_circuits):
        #     circuit_idx, points = circuit_data
        #     print(f"Circuit {circuit_idx} is {points}")
        #     total *= len(points)

        #     if idx == 2: break

        # return total

        points = np.array(self.data)
        kdtree = KDTree(points)

        point_to_circuit_mapping = {}
        connections_made = 0
        connections_to_make = 10

        while connections_made < connections_to_make:
            closest_neighbors = {}
            for point in self.data:
                # find many closest neighbors
                distances, indexes = kdtree.query(
                    np.array(point), k=min(20, len(self.data))
                )

                # need to find the closest neighbor that isn't in our circuit already
                circuit1 = point_to_circuit_mapping.get(point, point)
                for dist, idx in zip(distances[1:], indexes[1:]):
                    other_point = self.data[idx]
                    circuit2 = point_to_circuit_mapping.get(other_point, other_point)
                    if circuit1 != circuit2:
                        closest_neighbors[point] = (dist, idx)
                        break
                    else:
                        print("chat, we are in the same circuit")

            closest_neighbors = sorted(closest_neighbors.items(), key=lambda x: x[1][0])

            item_to_connect_point, (distance, point_to_connect_to_idx) = (
                closest_neighbors[0]
            )
            other_point = self.data[point_to_connect_to_idx]

            circuit1 = point_to_circuit_mapping.get(
                item_to_connect_point, item_to_connect_point
            )
            circuit2 = point_to_circuit_mapping.get(other_point, other_point)

            if circuit1 == circuit2:
                continue

            # move points from one circuit to another (merged)
            for p, c in point_to_circuit_mapping.items():
                if c == circuit2:
                    point_to_circuit_mapping[p] = circuit1
            point_to_circuit_mapping[item_to_connect_point] = circuit1
            point_to_circuit_mapping[other_point] = circuit1

            connections_made += 1

        circuits = {}
        for point in self.data:
            root = point_to_circuit_mapping.get(point, point)
            if root not in circuits:
                circuits[root] = []
            circuits[root].append(point)

        sorted_circuits = sorted(circuits.values(), key=len, reverse=True)

        print(f"We have {len(sorted_circuits)} total circuits.")

        for idx, points in enumerate(sorted_circuits):
            print(f"Circuit: {idx} -> {len(points)}")

        total = (
            len(sorted_circuits[0]) * len(sorted_circuits[1]) * len(sorted_circuits[2])
        )
        return total

    def part2(self):
        """Solve part 2 of the puzzle."""
        # TODO: Implement part 2
        return None

    def solve(self):
        """Run both parts and print results."""
        print(f"Day 8 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
