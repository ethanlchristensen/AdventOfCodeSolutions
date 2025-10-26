import os
import re
import math
import time
import networkx


def load_data(filename="data"):
    with open(filename, "r") as file:
        return [tuple(line.strip().split("-")) for line in file if line.strip() != ""]
    
data = load_data()
nodes = set()
edges = set()
for c1, c2 in data:
    nodes.add(c1)
    nodes.add(c2)
    edges.add((c1, c2))
    edges.add((c2, c1))

graph = networkx.Graph()
graph.add_nodes_from(nodes)
graph.add_edges_from(edges)


def part_one():
    start = time.time()
    networks = list(networkx.enumerate_all_cliques(graph))
    triples = [network for network in networks if len(network) == 3]
    valid_networks = [network for network in triples if any([node.startswith("t") for node in network])]
    total = len(valid_networks)
    end = time.time()
    return total, end - start


def part_two():
    start = time.time()
    networks = list(networkx.find_cliques(graph))
    largest_network = max(networks, key=len)
    password = ",".join(sorted(largest_network))
    end = time.time()
    return password, end - start


def solve():
    part_one_answer, part_one_time_to_complete = part_one()
    print(
        f"part one: {part_one_answer}\npart one time: {part_one_time_to_complete:.4f}s"
    )

    part_two_answer, part_two_time_to_complete = part_two()
    print(
        f"part two: {part_two_answer}\npart two time: {part_two_time_to_complete:.4f}s"
    )


if __name__ == "__main__":
    solve()
