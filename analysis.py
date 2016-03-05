#!/usr/bin/env python3

from graph import read_nodes
from collections import Counter
import numpy as np

nodes = read_nodes("tbontb")
start = [node for node in nodes if node.is_start][0]

def to_adjacency_lists(nodes):
    node_lookup = {}
    for node in nodes:
        node_lookup[node.content_file] = node
    adjacency_lists = {}
    for node in nodes:
        adjacents = [node_lookup[link.dst] for link in node.links]
        adjacency_lists[node] = adjacents
    return adjacency_lists

def shortest_paths(adjacency_lists):
    shortest_path = {}
    for node in adjacency_lists:
        shortest_path[node] = len(adjacency_lists)
    distance = 0
    queue = [start]
    while queue:
        to_add = []
        for node in queue:
            if shortest_path[node] <= distance:
                continue
            shortest_path[node] = distance
            to_add.extend(adjacency_lists[node])
        queue = to_add
        distance += 1
    return shortest_path

def stat(name, num):
    print(name + ":", num)

def get_in_degrees():
    counts = Counter()
    for node in nodes:
        for link in node.links:
            counts[link.dst] += 1
    in_degrees = []
    for node in nodes:
        in_degrees.append(counts[node.content_file])
    return np.array(in_degrees)

stat("nodes", len(nodes))

out_degrees = np.array([len(node.links) for node in nodes])
in_degrees = get_in_degrees()

stat("links", sum(out_degrees))
stat("zero-decision nodes", sum(out_degrees == 1))
stat("single-decision nodes", sum(out_degrees == 1))
stat("unreachable nodes", sum(in_degrees == 0))
stat("single-entry nodes", sum(in_degrees == 1))
stat("endings", sum([node.is_ending for node in nodes]))

adjacency_lists = to_adjacency_lists(nodes)
shortest_path = shortest_paths(adjacency_lists)
ending_paths = np.array([shortest_path[node] for node in nodes
    if node.is_ending])
# filter out "infinity" shortest distances
ending_paths = ending_paths[ending_paths != len(nodes)]

stat("reachable endings", len(ending_paths))
stat("average path to ending", ending_paths.mean())
stat("std dev path to ending", ending_paths.std())

def choice_types(adjacency_lists):
    single = 0
    not_real = 0
    for node, adjacency in adjacency_lists.items():
        if len(adjacency) == 1 and not node.links[0].is_implicit:
            single += 1
        if len(adjacency) > 1:
            dsts = set([link.dst for link in node.links if not link.is_implicit])
            if len(dsts) == 1:
                not_real += 1
    return {"single": single, "not_real": not_real}

choice_counts = choice_types(adjacency_lists)
stat("single choices", choice_counts["single"])
stat("not a real choices", choice_counts["not_real"])
