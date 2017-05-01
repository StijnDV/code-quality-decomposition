from __future__ import print_function

from collections import defaultdict
from baronprinter import print_formatted_function_nodes
from static_feedback import MIXED_PRINT_RETURN_FEEDBACK
from localbaronfinder import LocalBaronFinder
from baronfinder import find_function_parameters


def analyze_function_print_return(function_definition):
    local_baron_finder = LocalBaronFinder(function_definition)
    global_defines = local_baron_finder.global_name_nodes()
    local_variables = local_baron_finder.variable_name_nodes(global_defines)
    local_variables.update(find_function_parameters(function_definition))
    local_functions = local_baron_finder.find_all('def')

    # Get the variables that where printed in the function
    # Get this as a dict of names to name nodes for later feedback
    printed_variables = defaultdict(list)
    for print_node in local_baron_finder.find_all('print'):
        for name_node in print_node.value.find_all('name'):
            printed_variables[name_node.value].append(name_node)

    # Get the variables that where returned in the function
    # Get this as a dict of names to name nodes for later feedback
    returned_variables = defaultdict(list)
    for return_statement in local_baron_finder.find_all('return'):
        for returned_variable in return_statement.find_all('name'):
            returned_variables[returned_variable.value].append(returned_variable)

    # Detect the intersection between the printed and the returned variables
    # If this is not empty give feedback on not mixing printing and calculation of variables
    intersection = set(printed_variables.keys()) & set(returned_variables.keys())
    output_feedback(function_definition.name, intersection, printed_variables, returned_variables)
    for local_function in local_functions:
        analyze_function_print_return(local_function)


def output_feedback(function_name, intersection, printed_nodes, returned_nodes):
    for problematic_variable in intersection:
        print_nodes = printed_nodes[problematic_variable]
        return_nodes = returned_nodes[problematic_variable]
        print("The variable", problematic_variable, "was returned form the function at", end=" ")
        if len(return_nodes) > 1:
            print("lines:", end=" ")
        else:
            print("line:", end=" ")
        for return_node in return_nodes:
            print(return_node.absolute_bounding_box.top_left.line, end=" ")

        print()
        print("This variable", problematic_variable, "was also printed form the function at", end=" ")
        if len(print_nodes) > 1:
            print("lines:", end=" ")
        else:
            print("line:", end=" ")
        for print_node in print_nodes:
            print(print_node.absolute_bounding_box.top_left.line, end=" ")
        print()

    if intersection:
        print(MIXED_PRINT_RETURN_FEEDBACK)
