from __future__ import print_function

from itertools import combinations

from analysers.analyser import Analyser
from redbaron_filters import VariableFilter, ExcludeNamesFilter, NestingFilter
from redbaron_python_scoping import LocalBaronFinder
from redbaron_util import name_nodes_to_set, get_line_number
from static_feedback import LOOPS_FEEDBACK, LOOPS_COMPACT_FEEDBACK


class LoopAnalyser(Analyser):
    max_shared = 0

    variable_filter = None
    variable_cache = dict()

    def __init__(self, max_shared):
        Analyser.__init__(self)
        self.max_shared = max_shared

    def clear_cache(self):
        self.variable_filter = None
        self.variable_cache = dict()

    @staticmethod
    def get_non_nested_loops(function_def):
        loops = []
        scope_filter = NestingFilter(['for', 'while'])
        scoped_function_def = LocalBaronFinder(function_def)
        for_loops = scoped_function_def.find_all('for').filter(scope_filter.filter)
        while_loops = scoped_function_def.find_all('while').filter(scope_filter.filter)
        loops.extend(for_loops)
        loops.extend(while_loops)
        return loops

    def calculate_loop_variables(self, loop):
        excluded_variables = []
        if loop.type == 'for':
            excluded_variables.append(loop.iterator.value)
        exclude_filter = ExcludeNamesFilter(excluded_variables)
        variables = name_nodes_to_set(loop.find_all('name')
                                      .filter(exclude_filter.filter)
                                      .filter(self.variable_filter))
        return variables

    def get_loop_variables(self, loop):
        if loop not in self.variable_cache:
            self.variable_cache[loop] = self.calculate_loop_variables(loop)
        return self.variable_cache[loop]

    def shared_variables(self, loop1, loop2):
        var_set_1 = self.get_loop_variables(loop1)
        var_set_2 = self.get_loop_variables(loop2)
        return var_set_1.intersection(var_set_2)

    def analyse(self, function_def, file_reader):
        self.clear_cache()
        self.variable_filter = VariableFilter(file_reader.redbaron_fst).filter
        # get the top level loops in the function
        function_level_loops = self.get_non_nested_loops(function_def)

        if len(function_level_loops) < 1:
            return self.default_return

        feedback_list = []
        for loop_pair in combinations(function_level_loops, 2):
            shared_variables = self.shared_variables(loop_pair[0], loop_pair[1])
            if len(shared_variables) <= self.max_shared:
                loop1_information = (loop_pair[0], get_line_number(loop_pair[0]))
                loop2_information = (loop_pair[1], get_line_number(loop_pair[1]))
                feedback_list.append((shared_variables, loop1_information, loop2_information))
        if not feedback_list:
            return self.default_return
        return True, feedback_list

    def output_feedback(self, feedback_data):
        loop_lines = set()
        for loop_fault in feedback_data:
            loop_lines.add(loop_fault[1][1])
            loop_lines.add(loop_fault[2][1])
        sorted_lines = list(loop_lines)
        sorted_lines.sort()
        print(LOOPS_FEEDBACK.format(', '.join(map(str, sorted_lines))))

    def output_compact_feedback(self, feedback_data_dict):
        function_names = [node.name for node in feedback_data_dict.keys()]
        loop_lines = set()
        for feedback_data in feedback_data_dict.values():
            for loop_fault in feedback_data:
                loop_lines.add(loop_fault[1][1])
                loop_lines.add(loop_fault[2][1])
        sorted_lines = list(loop_lines)
        sorted_lines.sort()
        print(LOOPS_COMPACT_FEEDBACK.format(', '.join(map(str, function_names)),
                                            ', '.join(map(str, sorted_lines))))
