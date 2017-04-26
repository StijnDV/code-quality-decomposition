from __future__ import print_function

def print_formatted_name_nodes(name_nodes):
    for name_node in name_nodes:
        print(name_node.value, name_node.absolute_bounding_box)


def print_formatted_function_nodes(function_nodes):
    for function_node in function_nodes:
        print(function_node.name, function_node.absolute_bounding_box)