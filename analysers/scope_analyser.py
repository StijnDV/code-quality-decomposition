from __future__ import print_function, division

from analysers.analyser import Analyser
from redbaron_filters import VariableFilter
from redbaron_util import name_nodes_to_set
from static_feedback import BREAK_FEEDBACK


class ScopeAnalyser(Analyser):
    min_length = 0
    variable_filter = None

    def __init__(self, min_length):
        Analyser.__init__(self)
        self.min_length = min_length

    def clear_cache(self):
        self.variable_filter = None

    def count_non_empty_lines(self, string):
        non_empty_lines = 0
        for line in string.splitlines(False):
            if line.strip() != '':
                non_empty_lines += 1
        return non_empty_lines

    def get_all_variable_scopes(self, function_def):
        scope_list = []
        variables = name_nodes_to_set(function_def.find_all('name').filter(self.variable_filter))
        for variable in variables:
            scope_list.append(self.get_var_scope(variable, function_def))
        return scope_list

    def get_var_scope(self, var_name, function_def):
        first_use = float('inf')
        last_use = 0
        name_node_list = function_def.find_all('name', value=var_name)
        for name_node in name_node_list:
            line = name_node.absolute_bounding_box.top_left.line
            if line < first_use:
                first_use = line
            if line > last_use:
                last_use = line
        return var_name, (first_use, last_use)

    def analyse(self, function_def, file_reader):
        self.clear_cache()
        self.variable_filter = VariableFilter(file_reader.redbaron_fst).filter

        cleaned_function = file_reader.get_clean_function(function_def)
        length = self.count_non_empty_lines(cleaned_function.dumps())

        if length < self.min_length:
            return self.default_return
        scopes_list = self.get_all_variable_scopes(function_def)
        first_line = function_def.absolute_bounding_box.top_left.line
        last_line = function_def.absolute_bounding_box.bottom_right.line
        skip_lines = (last_line - first_line) // 3
        function_indentation = len(function_def.value[0].indentation)
        lines = file_reader.file_content.splitlines(False)

        possible_break_points = []
        for line in xrange((first_line + skip_lines), (last_line - skip_lines)):
            lines_index = line - 1
            # Don't break in the middle of a control structure
            # so check if the indentation of the line is the same as the function
            line_indentation = len(lines[lines_index]) - len(lines[lines_index].lstrip())
            if lines[lines_index].lstrip() != '' and line_indentation != function_indentation:
                continue
            top_scopes = []
            in_scopes = []
            bottom_scopes = []
            for scope in scopes_list:
                if line < scope[1][0]:
                    top_scopes.append(scope)
                elif line > scope[1][1]:
                    bottom_scopes.append(scope)
                else:
                    in_scopes.append(scope)
            # More shared variables than would be nice as function parameters
            if len(in_scopes) > 4:
                continue
            # more variables are split then are left in both functions together.
            if len(bottom_scopes) < len(in_scopes) or len(top_scopes) < len(in_scopes):
                continue
            if len(bottom_scopes) <= 1 or len(top_scopes) <= 1:
                continue
            possible_break_points.append((line, in_scopes, lines[lines_index]))
        if possible_break_points:
            return True, possible_break_points
        return self.default_return

    def get_best_split(self, feedback_data):
        best_split = feedback_data[0]
        best_split_line_value = "test"
        for split_option in feedback_data:
            if len(split_option[1]) < len(best_split[1]):
                best_split = split_option
                best_split_line_value = split_option[2].strip()
            if len(split_option[1]) == len(best_split[1]):
                if best_split_line_value != '' and split_option[2].strip() == '':
                    best_split = split_option
                    best_split_line_value = split_option[2].strip()

        return best_split

    def output_feedback(self, feedback_data):
        print(feedback_data)
        best_split = self.get_best_split(feedback_data)
        print(BREAK_FEEDBACK.format(str(best_split[0]), ', '.join(map(str, best_split[1]))))

    def output_compact_feedback(self, feedback_data_dict):
        pass
