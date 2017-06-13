from __future__ import print_function

from radon.complexity import cc_visit
from radon.metrics import h_visit
from radon.raw import analyze
from redbaron_python_scoping import LocalBaronFinder

class ControlInfo:
    start = 0
    end = 0
    size = 0

    contained_if = list()
    contained_for = list()
    contained_while = list()
    contained_elif = list()

    top_level_if = None
    top_level_for = None
    top_level_while = None
    top_level_elif = None

    complexity = 0
    nest_level = 0

    node = None
    def __init__(self, node):
        self.node = node
        self.start = node.absolute_bounding_box.top_left.line
        self.end = node.absolute_bounding_box.bottom_right.line
        self.size = self.end - self.start

        current_nest_node = node.parent_find(['for', 'if', 'while', 'else', 'elseif'])
        while current_nest_node:
            self.nest_level += 1
            current_nest_node = current_nest_node.parent_find(['for', 'if', 'while', 'else', 'elseif'])


        self.contained_if = node.value.find_all('if')
        self.contained_elif = node.value.find_all('elif')
        self.contained_for = node.value.find_all('for')
        self.contained_while = node.value.find_all('while')

        self.complexity = len(self.contained_if) + len(self.contained_elif)\
                          + len(self.contained_for) + len(self.contained_while)

    def get_top_level_if(self):
        if not self.top_level_if:
            self.top_level_if = self.contained_if.filter(self.top_level_filter(self.node))
        return self.top_level_if

    def get_top_level_elif(self):
        if not self.top_level_if:
            self.top_level_if = self.contained_elif.filter(self.top_level_filter(self.node))
        return self.top_level_if

    def get_top_level_for(self):
        if not self.top_level_if:
            self.top_level_if = self.contained_for.filter(self.top_level_filter(self.node))
        return self.top_level_if

    def get_top_level_while(self):
        if not self.top_level_if:
            self.top_level_if = self.contained_while.filter(self.top_level_filter(self.node))
        return self.top_level_if


    def top_level_filter(self, parent):
        return lambda node : node.parent.parent == parent


    def __str__(self):
        string_rep = "type: " + self.node.type + ", box: (" + str(self.start) + ", " + str(self.end) + ") -> " + str(self.size)
        string_rep += ", depth -> " + str(self.nest_level) + "\n"
        string_rep += "contains"
        string_rep += ": if -> " + str(len(self.contained_if))
        string_rep += ", elif -> " + str(len(self.contained_elif))
        string_rep += ", for -> " + str(len(self.contained_for))
        string_rep += ", while -> " + str(len(self.contained_while))
        return string_rep

def create_if_dict(function_fst):
    if_dict = dict()
    filtered_fst = LocalBaronFinder(function_fst)
    all_if_blocks = filtered_fst.find_all('if')
    for if_block in all_if_blocks:
        if_dict[if_block] = ControlInfo(if_block)
    return if_dict


def create_for_dict(function_fst):
    for_dict = dict()
    filtered_fst = LocalBaronFinder(function_fst)
    all_for_blocks = filtered_fst.find_all('for')
    for for_block in all_for_blocks:
        for_dict[for_block] = ControlInfo(for_block)
    return for_dict

def create_while_dict(function_fst):
    while_dict = dict()
    filtered_fst = LocalBaronFinder(function_fst)
    all_while_blocks = filtered_fst.find_all('while')
    for while_block in all_while_blocks:
        while_dict[while_block] = ControlInfo(while_block)
    return while_dict


def analyse_complexity(function_fst):
    code = function_fst.dumps()
    cycl = cc_visit(code)
    raw = analyze(code)
    halstead = h_visit(code)

    return cycl[0].complexity, halstead, raw
