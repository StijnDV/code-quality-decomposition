from __future__ import print_function

from baronutil import name_nodes_to_dict


class LocalBaronFinder:
    scope = None
    fst = None

    def __init__(self, fst, scope=False):
        if scope is False:
            scope = fst
        self.scope = scope
        self.fst = fst

    def find_all(self, name):
        return self.fst.find_all(name).filter(self.scope_filter())

    def variable_name_nodes(self, defined_as_global=None):
        if defined_as_global is None:
            defined_as_global = set()
        global_name_set = name_nodes_to_dict(defined_as_global).keys()

        local_variable_names = set()
        local_variable_assignments = self.find_all('assignment')
        for assignment in local_variable_assignments:
            if assignment.target.value not in global_name_set:
                local_variable_names.add(assignment.target)
        return local_variable_names

    def scope_filter(self):
        return lambda node: node.parent_find('def') == self.scope

    def global_name_nodes(self):
        global_names = set()
        global_statements = self.find_all('global')
        for global_statement in global_statements:
            global_names.update(global_statement.value)
        return global_names
