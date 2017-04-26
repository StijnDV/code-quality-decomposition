from localbaronfinder import LocalBaronFinder


def find_global_variable_name_nodes(fst):
    local_baron_finder = LocalBaronFinder(fst, None)
    global_variable_name_nodes = local_baron_finder.variable_name_nodes()
    global_statements = fst.find_all('global')
    for global_statement in global_statements:
        global_variable_name_nodes.update(global_statement.value)
    return global_variable_name_nodes


def find_function_parameters(function_definition):
    return set([arg.target for arg in function_definition.arguments])
