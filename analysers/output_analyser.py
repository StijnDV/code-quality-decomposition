from analysers.analyser import Analyser
from redbaron_filters import VariableFilter
from redbaron_python_scoping import LocalBaronFinder
from static_feedback import MIXED_PRINT_RETURN_FEEDBACK, MIXED_PRINT_RETURN_COMPACT_FEEDBACK


class OutputAnalyser(Analyser):
    variable_filter = None

    def __init__(self):
        Analyser.__init__(self)

    def clear_cache(self):
        self.variable_filter = None


    def count_non_empty_lines(self, string):
        non_empty_lines = 0
        for line in string.splitlines():
            if line.strip() != '':
                non_empty_lines += 1
        return non_empty_lines

    def analyse(self, function_def, file_reader):
        self.clear_cache()
        self.variable_filter = VariableFilter(file_reader.redbaron_fst).filter
        local_baron_finder = LocalBaronFinder(function_def)

        # Get the variables that where printed in the function
        printed_variables = set()
        for print_node in local_baron_finder.find_all('print'):
            for name_node in print_node.value.find_all('name').filter(self.variable_filter):
                printed_variables.add(name_node.value)
        # Get the variables that where returned in the function
        returned_variables = set()
        for return_statement in local_baron_finder.find_all('return'):
            for name_node in return_statement.find_all('name').filter(self.variable_filter):
                returned_variables.add(name_node.value)
        # Detect the intersection between the printed and the returned variables
        intersection = printed_variables.intersection(returned_variables)
        if len(intersection) > 0:
            return (True, [])
        return self.default_return

    def output_feedback(self, feedback_data):
        print(MIXED_PRINT_RETURN_FEEDBACK)

    def output_compact_feedback(self, feedback_data_dict):
        function_names = [node.name for node in feedback_data_dict.keys()]
        print(MIXED_PRINT_RETURN_COMPACT_FEEDBACK.format(', '.join(function_names)))