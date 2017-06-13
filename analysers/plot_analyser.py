from __future__ import print_function, division

from analysers.analyser import Analyser
from redbaron_python_scoping import LocalBaronFinder
from redbaron_util import get_line_number

class PlotAnalyser(Analyser):
    def __init__(self):
        Analyser.__init__(self)

    def count_non_empty_lines(self, string):
        non_empty_lines = 0
        for line in string.splitlines():
            if line.strip() != '':
                non_empty_lines += 1
        return non_empty_lines

    def get_plotting_blocks(self, lines, threshold):
        sorted_lines = sorted(lines)
        blocks = []
        first_line = None
        for index, line in enumerate(sorted_lines):
            if not first_line:
                first_line = line
            if index + 1 >= len(sorted_lines):
                last_line = line
                blocks.append((first_line, last_line))
                first_line = None
                break
            if sorted_lines[index + 1] - line > threshold:
                last_line = line
                blocks.append((first_line, last_line))
                first_line = None
        return blocks


    def analyse(self, function_def, file_reader):
        total_code_lines = self.count_non_empty_lines(file_reader.get_clean_function(function_def).dumps())

        scoped_def = LocalBaronFinder(function_def)
        plot_nodes = scoped_def.find_all('name').filter(lambda node: node.value == 'plt')
        plot_lines = set()
        for plot_node in plot_nodes:
            plot_lines.add(get_line_number(plot_node))

        blocks = self.get_plotting_blocks(plot_lines, 5)
        plot_fraction = len(plot_lines) / total_code_lines
        if len(plot_lines) >= 1 and plot_fraction < 0.7:
            return (True, (len(plot_lines), total_code_lines, blocks))
        return self.default_return

    def output_feedback(self, feedback_data):
        print("This function has {0} lines of plotting code out of {1} lines of code.\n"
              "This indicates that this function is not a dedicated plotting function.\n"
              "The plotting is done in these code blocks:[{2}]\n"
              "It is often better to separate the plotting of data into its own function."
              .format(feedback_data[0], feedback_data[1], self.create_code_bloc_string(feedback_data[2])))

    def create_code_bloc_string(self, code_blocks):
        code_block_strings = []
        for code_block in code_blocks:
            code_block_strings.append(str(code_block[0]) + "-" + str(code_block[1]))
        return ', '.join(code_block_strings)

    def output_compact_feedback(self, feedback_data_dict):
        pass