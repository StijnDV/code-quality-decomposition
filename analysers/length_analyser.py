from __future__ import print_function

from analysers.analyser import Analyser
from static_feedback import FUNCTION_TO_LONG_FEEDBACK, FUNCTION_TO_LONG_COMPACT_FEEDBACK


class LengthAnalyser(Analyser):
    max_length = 0

    def __init__(self, max_length):
        Analyser.__init__(self)
        self.max_length = max_length

    def count_non_empty_lines(self, string):
        non_empty_lines = 0
        for line in string.splitlines(False):
            if line.strip() != '':
                non_empty_lines += 1
        return non_empty_lines

    def analyse(self, function_def, file_reader):
        function_string = file_reader.get_clean_function(function_def).dumps()
        length = self.count_non_empty_lines(function_string)
        return (length > self.max_length, length)

    def output_feedback(self, feedback_data):
        print(FUNCTION_TO_LONG_FEEDBACK.format(feedback_data))

    def output_compact_feedback(self, feedback_data_dict):
        function_names = [node.name for node in feedback_data_dict.keys()]
        print(FUNCTION_TO_LONG_COMPACT_FEEDBACK.format(', '.join(function_names), str(self.max_length)))