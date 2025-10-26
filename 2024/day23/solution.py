"""
Advent of Code 2024 - Day 23
"""

import os
import re
import math
import time
import networkx


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, filename="data"):
        with open(filename, "r") as file:
            return [tuple(line.strip().split("-")) for line in file if line.strip() != ""]
    
    self.data = self.load_data()
    nodes = set()
    edges = set()
    for c1, c2 in self.data:
        nodes.add(c1)
        nodes.add(c2)
        edges.add((c1, c2))
        edges.add((c2, c1))

    graph = networkx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)



    def part1(self):
        start = time.time()
        networks = list(networkx.enumerate_all_cliques(graph))
        triples = [network for network in networks if len(network) == 3]
        valid_networks = [network for network in triples if any([node.startswith("t") for node in network])]
        total = len(valid_networks)
        end = time.time()
        return total, end - start



    def part2(self):
        start = time.time()
        networks = list(networkx.find_cliques(graph))
        largest_network = max(networks, key=len)
        password = ",".join(sorted(largest_network))
        end = time.time()
        return password, end - start



    def solve(self):
        part_one_answer, part_one_time_to_complete = self.part1()
        print(
            f"part one: {part_one_answer}\npart one time: {part_one_time_to_complete:.4f}s"
        )

        part_two_answer, part_two_time_to_complete = self.part2()
        print(
            f"part two: {part_two_answer}\npart two time: {part_two_time_to_complete:.4f}s"
        )




if __name__ == "__main__":
    solution = Solution()
    solution.solve()
