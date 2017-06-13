def find_function_parameters(function_definition):
    function_parameters = set()
    for argument in function_definition.arguments:
        if argument.type == 'def_argument':
            function_parameters.add(argument.target)
        if argument.type == 'list_argument':
            function_parameters.add(argument.value)
        if argument.type == 'dict_argument':
            function_parameters.add(argument.value)
    return function_parameters


def name_nodes_to_set(name_nodes):
    return {node.value for node in name_nodes}
