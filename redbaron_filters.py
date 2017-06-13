class RedBaronFilter:
    def __init__(self):
        pass

    def filter(self, node):
        return True


class VariableFilter(RedBaronFilter):
    reserved_words = {
        "and", "assert", "break", "class", "continue", "def", "del", "elif", "else", "except",
        "exec", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda", "not",
        "or", "pass", "print", "raise", "return", "try", "while", "Data", "Float", "Int", "Numeric",
        "Oxphys", "array", "close", "float", "int", "input", "open", "range", "type", "write",
        "zeros", "acos", "asin", "atan", "cos", "e", "exp", "fabs", "floor", "log", "log10", "pi",
        "sin", "sqrt", "tan", "len", "xrange", "True", "False"
    }

    @staticmethod
    def get_reserved_import_names(fst):
        reserved = set()
        named_imports = fst.find_all(['name_as_name', 'dotted_as_name'])
        for named_import in named_imports:
            if named_import.target != '':
                reserved.add(named_import.target)
        return reserved

    def __init__(self, fst):
        RedBaronFilter.__init__(self)
        self.import_reserved_words = VariableFilter.get_reserved_import_names(fst)

    def filter(self, name_node):
        # Reserved python keyword probably not a variable
        if name_node.value in self.reserved_words:
            return False
        # Variable name was used as a import variable not a variable
        if name_node.value in self.import_reserved_words:
            return False
        # Name of argument that is being assigned in a function call
        if name_node.on_attribute == 'target' and name_node.parent.type == "call_argument":
            return False
        # Detect function definitions
        if name_node.on_attribute == 'name':
            return False
        # Only the object is counted as a variable not its member variables
        if name_node.parent.type == 'atomtrailers' and name_node.index_on_parent != 0:
            return False
        # Detect function calls.
        possible_function_call = name_node.parent.type == 'atomtrailers' and len(name_node.parent.value) > 1
        if possible_function_call and name_node.parent.value[1].type == 'call':
            return False
        return True


class DocStringFilter(RedBaronFilter):
    docstring_parent_types = {'class', 'def', 'for', 'while', 'if', 'else', 'elif', 'try', 'except', 'finally', 'with'}

    def __init__(self):
        RedBaronFilter.__init__(self)

    def filter(self, node):
        if node.parent.type in DocStringFilter.docstring_parent_types:
            return True
        return False


class ExcludeNodesFilter(RedBaronFilter):
    def __init__(self, excluded_nodes):
        RedBaronFilter.__init__(self)
        self.excluded_nodes = excluded_nodes

    def filter(self, node):
        if node in self.excluded_nodes:
            return False
        return True


class ExcludeNamesFilter(RedBaronFilter):
    def __init__(self, excluded_names):
        RedBaronFilter.__init__(self)
        self.excluded_names = excluded_names

    def filter(self, node):
        if node.value in self.excluded_names:
            return False
        return True


class NestingFilter(RedBaronFilter):
    def __init__(self, excluded_parents):
        RedBaronFilter.__init__(self)
        self.excluded_parents = excluded_parents

    def filter(self, node):
        parent = node.parent_find(self.excluded_parents)
        if parent:
            return False
        return True
