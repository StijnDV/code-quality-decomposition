from __future__ import print_function
from itertools import takewhile
from localbaronfinder import LocalBaronFinder
from baronfinder import find_function_parameters
from baronutil import name_nodes_to_dict
from programslice import slice_string


def lstripped(s):
    return ''.join(takewhile(str.isspace, s))

def get_indentation_function(function_fst):
    lines = function_fst.value.dumps().split("\n")
    first_not_empty_line = ""
    for line in lines:
        if line.strip() != "":
            first_not_empty_line = line
            break

    return lstripped(first_not_empty_line)

def get_slice_for_variable(function_fst, var_name):
    slice = list()
    indentation = get_indentation_function(function_fst)
    function_fst.value = indentation + var_name + ' = 0\n' + function_fst.value.dumps()
    first_node = function_fst.find('name', value=var_name)
    try:
        slice = slice_string(var_name,
                    first_node.absolute_bounding_box.top_left.line,
                    first_node.absolute_bounding_box.top_left.column - 1,
                    function_fst.dumps(), 'program')
    except:
        print("function could not be parsed by python ast is most likely not valid python")
    return slice



def find_slice_seeds(function_fst):
    filtered_fst = LocalBaronFinder(function_fst)

    parameters = find_function_parameters(function_fst)
    returns = filtered_fst.find_all('return')
    return_names = returns.find_all('name')
    prints = filtered_fst.find_all('print')
    print_names = prints.find_all('name')
    assigns = filtered_fst.find_all('assign')
    global_assigns = assigns.filter(lambda assign_node: assign_node.target.value in name_nodes_to_dict(filtered_fst.global_name_nodes()).keys())

    slice_seeds = set()
    for print_name in print_names:
        slice_seeds.add(print_name.value)
    for return_name in return_names:
        slice_seeds.add(return_name.value)
    for global_assign in global_assigns:
        slice_seeds.add(global_assign.target.value)

    return slice_seeds