#!/usr/bin/env python3

from graph import read_nodes, Node
from collections import Counter, defaultdict
import numpy as np

def to_adjacency_lists(nodes):
    node_lookup = {}
    for node in nodes:
        node_lookup[node.content_file] = node
    adjacency_lists = {}
    for node in nodes:
        adjacents = [node_lookup[link.dst] for link in node.links]
        adjacency_lists[node] = adjacents
    return adjacency_lists

def reverse_adjacency(adjacency_lists):
    reverse_lists = defaultdict(list)
    for src, adjacents in adjacency_lists.items():
        for dst in adjacents:
            reverse_lists[dst].append(src)
    return dict( (k, v) for (k, v) in reverse_lists.items() )

def shortest_paths(start, adjacency_lists, include_unreachable=True):
    path = {}
    path_len = {}
    for node in adjacency_lists:
        path_len[node] = len(adjacency_lists)
        if include_unreachable:
            path[node] = None
    distance = 0
    queue = [([], start)]
    while queue:
        to_add_nodes = set([])
        to_add = []
        for path_prefix, node in queue:
            if path_len[node] <= distance:
                continue
            path_len[node] = distance
            # distance == len(path[node])
            # (eg, 0 for start)
            path[node] = path_prefix
            # new nodes will be reached through path_prefix, node, then a link
            # out of node
            prefix = path_prefix + [node]
            for n in adjacency_lists[node]:
                if not n in to_add_nodes:
                    to_add_nodes.add(n)
                    to_add.append( (prefix, n) )
        queue = to_add
        distance += 1
    return path

def stat(name, num):
    name = name.replace(" ", "-")
    print(name + ":", num)
    if isinstance(num, float):
        stat(name + "-int", int(round(num)))

def get_in_degrees(nodes):
    counts = Counter()
    for node in nodes:
        for link in node.links:
            counts[link.dst] += 1
    in_degrees = []
    for node in nodes:
        in_degrees.append(counts[node.content_file])
    return np.array(in_degrees)

nodes = read_nodes("tbontb")
start = [node for node in nodes if node.is_start][0]

stat("nodes", len(nodes))

non_implicit_nodes = [node for node in nodes
        if not all([link.is_implicit for link in node.links])]

stat("non-implicit nodes", len(non_implicit_nodes))

out_degrees = np.array([len(node.links) for node in nodes])
in_degrees = get_in_degrees(nodes)

stat("links", sum(out_degrees))
mean_degree = sum(out_degrees)/len(non_implicit_nodes)
stat("mean non-implicit out-degree", mean_degree)
stat("mean non-implicit out-degree round", round(mean_degree, 1))
stat("zero-decision nodes", sum(out_degrees == 0))
stat("single-decision nodes", sum(out_degrees == 1))
stat("root nodes", sum(in_degrees == 0))
stat("single-entry nodes", sum(in_degrees == 1))
stat("endings", sum([node.is_ending for node in nodes]))

adjacency_lists = to_adjacency_lists(nodes)
paths = shortest_paths(start, adjacency_lists)

stat("unreachable nodes", sum([1 for path in paths.values()
    if path is None]))

ending_paths = [path
    for (node, path) in paths.items()
    if path is not None
    and node.is_ending]
stat("reachable endings", len(ending_paths))

# measure length by pages
ending_path_lens = np.array([len(path) for path in ending_paths])
stat("mean path to ending", ending_path_lens.mean())
stat("std dev path to ending", ending_path_lens.std())

# measure length by decisions
ending_path_decisions = np.array([
    sum([1 for node in path if len(node.links) > 1])
    for path in ending_paths])
stat("maean decisions to ending", ending_path_decisions.mean())
stat("std dev decisions to ending", ending_path_decisions.std())

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

# Analyze original Hamlet subgraph
hamlet_nodes = []
for node in nodes:
    if len(node.links) == 1:
        links = node.links
    else:
        links = [link for link in node.links
                if link.is_shakespeare or link.is_implicit]
    hamlet_nodes.append(Node(node.chapter, node.page, links))
hamlet_start = [node for node in hamlet_nodes if node.is_start][0]
hamlet_paths = shortest_paths(hamlet_start,
        to_adjacency_lists(hamlet_nodes),
        include_unreachable=False)
ending_path = max(hamlet_paths.values(), key=len)
stat("Shakespeare path len", len(ending_path))
