#!/usr/bin/env python3

from graph import read_nodes
from collections import Counter
import numpy as np

nodes = read_nodes("tbontb")

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
