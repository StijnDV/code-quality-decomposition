from __future__ import print_function

from localbaronfinder import LocalBaronFinder
from baronfinder import find_function_parameters
from baronutil import name_nodes_to_dict

def create_dependance_graph(function_fst):
    filtered_fst = LocalBaronFinder(function_fst)


def get_slice_for_variable(function_fst, var_name):
    if var_name == "a":
        def test():
            print("test")

    slice = set()
    search_set = set()
    searched_set = set()
    search_set.add(var_name)

    filtered_fst = LocalBaronFinder(function_fst)
    while len(search_set) > 0:
        search_var = search_set.pop()
        if search_var in searched_set:
            continue
        name_nodes = filtered_fst.find_all('name').filter(lambda name_node: name_node.value == search_var)
        for name_node in name_nodes:
            searched_set.add(name_node.value)



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