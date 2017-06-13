from __future__ import print_function

from collections import defaultdict

from redbaron_python_scoping import LocalBaronFinder
from old_code.redbaron_util import find_function_parameters
from static_feedback import MIXED_PRINT_RETURN_FEEDBACK


def analyse_function_print_return(function_definition):
    local_baron_finder = LocalBaronFinder(function_definition)

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
    if len(intersection) > 0:
        return (True, (function_definition.name, intersection, printed_variables, returned_variables))
    return (False, ())



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
