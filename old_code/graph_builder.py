from __future__ import print_function

import networkx as nx
from collections import defaultdict
from redbaron_python_scoping import LocalBaronFinder

def build_graph(fst):
    graph = nx.Graph()
    try:
        line_number = 0
        while True:
            graph.add_node(line_number)
            fst.at(line_number)
            line_number += 1
    except:
        pass # TODO fix it to not use the exception as loop control
    scoped_fst = LocalBaronFinder(fst)
    used_dict = defaultdict(list)
    assigned_dict = defaultdict(list)
    for name_node in scoped_fst.find_all('name'):
        if name_node.on_attribute == 'target':
            assigned_dict[name_node.value].append(name_node)
        else:
            used_dict[name_node.value].append(name_node)

    for var_name in assigned_dict:
        used_lines = set()
        for name_node in assigned_dict[var_name]:
            used_lines.add(name_node.absolute_bounding_box.top_left.line)
        for name_node in used_dict[var_name]:
            used_lines.add(name_node.absolute_bounding_box.top_left.line)
        print(used_lines)
        for origin_line_number in used_lines:
            for destination_line_number in used_lines:
                if origin_line_number == destination_line_number:
                    continue
                if graph.has_edge(origin_line_number, destination_line_number):
                    graph[destination_line_number][origin_line_number]['weight'] += 1
                else:
                    graph.add_edge(destination_line_number, origin_line_number, weight=1)
    print(graph.edges(data=True))
    nx.write_graphml(graph, "test.graphml")