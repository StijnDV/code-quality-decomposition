from __future__ import print_function


class LocalBaronFinder:
    def __init__(self, fst, scope=False):
        if scope is False:
            scope = fst
        self.scope = scope
        self.fst = fst

    def find_all(self, name):
        return self.fst.find_all(name).filter(self.scope_filter())

    def scope_filter(self):
        return lambda node: node.parent_find('def') == self.scope

    def global_name_nodes(self):
        global_names = set()
        global_statements = self.find_all('global')
        for global_statement in global_statements:
            global_names.update(global_statement.value)
        return global_names
