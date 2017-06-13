from __future__ import print_function

from redbaron_util import name_nodes_to_dict
from redbaron_python_scoping import LocalBaronFinder
from old_code.redbaron_util import find_function_parameters


def get_non_name_slice_parts(target_node):
    slice_parts = set()
    for int_node in target_node.find_all('int'):
        slice_parts.add(int_node)
    for float_node in target_node.find_all('float'):
        slice_parts.add(float_node)
    for string_node in target_node.find_all('string'):
        slice_parts.add(string_node)
    return slice_parts


def get_slice_update_assignment(assignment_node, name_node):
    new_names = set()
    data_tokens = set()
    if name_node.on_attribute == 'target':
        data_tokens = get_non_name_slice_parts(assignment_node)
        for new_name_node in assignment_node.find_all('name'):
            if new_name_node.value == 'True' or new_name_node.value == 'False':
                data_tokens.add(new_name_node)
                continue
            new_names.add(new_name_node.value)
    else:
        new_names.add(assignment_node.target)
    return new_names, data_tokens

def get_slice_update_for(for_node, name_node):
    new_names = set()
    data_tokens = set()
    for new_name_node in for_node.iterator.find_all('name'):
        if new_name_node.value == 'True' or new_name_node.value == 'False':
            data_tokens.add(new_name_node)
            continue
        new_names.add(new_name_node.value)
    for new_name_node in for_node.target.find_all('name'):
        if new_name_node.value == 'True' or new_name_node.value == 'False':
            data_tokens.add(new_name_node)
            continue
        if new_name_node.value == 'range' or new_name_node.value == 'xrange':
            continue
        new_names.add(new_name_node.value)
    return new_names, data_tokens

def get_slice_update_if(if_node, name_node):
    new_names = set()
    data_tokens = get_non_name_slice_parts(if_node)
    for new_name_node in if_node.test.find_all('name'):
        if new_name_node.value == 'True' or new_name_node.value == 'False':
            data_tokens.add(new_name_node)
            continue
        new_names.add(new_name_node.value)
    return new_names, data_tokens

def get_slice_update_while(while_node, name_node):
    new_names = set()
    data_tokens = get_non_name_slice_parts(while_node)
    for new_name_node in while_node.test.find_all('name'):
        if new_name_node.value == 'True' or new_name_node.value == 'False':
            data_tokens.add(new_name_node)
            continue
        new_names.add(new_name_node.value)
    return new_names, data_tokens

def get_slice_update_else(else_node, name_node):
    if_else_block_node = else_node.parent
    if_node = if_else_block_node.find('if')
    new_names, data_tokens = get_slice_update_if(if_node, name_node)
    return new_names, data_tokens

def get_slice_update_elif(elif_node, name_node):
    new_names = set()
    data_tokens = get_non_name_slice_parts(elif_node)
    for new_name_node in elif_node.test.find_all('name'):
        if new_name_node.value == 'True' or new_name_node.value == 'False':
            data_tokens.add(new_name_node)
            continue
        new_names.add(new_name_node.value)
    if_else_block_node = elif_node.parent
    if elif_node.index_on_parent == 1:
        if_node = if_else_block_node.find('if')
        if_new_names, if_data_tokens = get_slice_update_if(if_node, name_node)
        for if_name in if_new_names:
            new_names.add(if_name)
        for if_data in if_data_tokens:
            data_tokens.add(if_data)
    else:
        prev_elif = if_else_block_node[elif_node.index_on_parent - 1]
        elif_new_names, elif_data_tokens = get_slice_update_elif(prev_elif, name_node)
        for if_name in elif_new_names:
            new_names.add(if_name)
        for if_data in elif_data_tokens:
            data_tokens.add(if_data)
    return new_names, data_tokens

def get_slice_for_variable(function_fst, var_name):
    slice = set()
    filtered_fst = LocalBaronFinder(function_fst)
    all_name_nodes = filtered_fst.find_all('name')
    variables = {var_name}
    used_variables = set()
    while len(variables) != 0:
        variable = variables.pop()
        if variable in used_variables:
            continue
        used_variables.add(variable)

        var_name_nodes = all_name_nodes.filter(lambda name_node: name_node.value == variable)
        slice.update(var_name_nodes)

        switch_dict = {'assignment': get_slice_update_assignment,
                       'if': get_slice_update_if,
                       'elif': get_slice_update_elif,
                       'else': get_slice_update_else,
                       'while': get_slice_update_while,
                       'for': get_slice_update_for}
        for name_node in var_name_nodes:
            nodes_of_interest = set()
            nodes_of_interest.add(name_node.parent)
            nodes_of_interest.add(name_node.parent_find('if'))
            nodes_of_interest.add(name_node.parent_find('elif'))
            nodes_of_interest.add(name_node.parent_find('else'))
            nodes_of_interest.add(name_node.parent_find('for'))
            nodes_of_interest.add(name_node.parent_find('while'))
            for node_of_interest in nodes_of_interest:
                if node_of_interest and node_of_interest.type in switch_dict:
                    new_name_nodes, data_tokens = switch_dict[node_of_interest.type](node_of_interest, name_node)
                    variables.update(new_name_nodes)
                    for data_token in data_tokens:
                        slice.add(data_token)
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
    assign_names = [node.target.value for node in assigns]

    slice_seeds = set()
    for print_name in print_names:
        slice_seeds.add(print_name.value)
    for return_name in return_names:
        slice_seeds.add(return_name.value)
    for global_assign in global_assigns:
        slice_seeds.add(global_assign.target.value)
    for parameter in parameters:
        if parameter.value in assign_names:
            slice_seeds.add(parameter.value)
    if 'True' in slice_seeds:
        slice_seeds.remove('True')
    if 'False' in slice_seeds:
        slice_seeds.remove('False')
    return slice_seeds