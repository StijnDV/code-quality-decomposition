from __future__ import print_function, division

import argparse
import os

from analysers.length_analyser import LengthAnalyser
from analysers.loop_analyser import LoopAnalyser
from analysers.output_analyser import OutputAnalyser
from analysers.scope_analyser import ScopeAnalyser
from analysers.plot_analyser import PlotAnalyser
from code_analyser import CodeAnalyser
from file_reader import PythonParsingFailure, RedBaronParsingFailure


def contains_feedback(file_feedback_data):
    has_feedback = False
    for func in file_feedback_data.keys():
        for analyser in file_feedback_data[func].keys():
            if file_feedback_data[func][analyser][0]:
                has_feedback = True
    return has_feedback


def get_python_files(folder_name):
    file_names = []
    for directory, subdirectories, files in os.walk(folder_name):
        for input_file in files:
            if not input_file.endswith(".py"):
                continue
            file_names.append(os.path.join(directory, input_file))
    return file_names


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", dest="filename")
    parser.add_argument('-folder')
    parser.add_argument('-main', action='store_true')
    parser.add_argument('-return_analyze', action='store_true')
    parser.add_argument('-loops', dest="loops_max_shared", nargs='?', const=2, type=int)
    parser.add_argument('-scopes', nargs='?', const=10, type=int)
    parser.add_argument('-length', nargs='?', const=30, type=int)
    parser.add_argument('-compact', action='store_true')
    return parser.parse_args()

settings = parse_arguments()
if settings.filename:
    python_files = [settings.filename]
else:
    python_files = get_python_files(settings.folder)

code_analyser = CodeAnalyser()
loop_analyser = LoopAnalyser(settings.loops_max_shared)
output_analyser = OutputAnalyser()
length_analyser = LengthAnalyser(settings.length)
scope_analyser = ScopeAnalyser(settings.scopes)
plot_analyser = PlotAnalyser()

code_analyser.register_analysis(plot_analyser, 1, "main_group")
code_analyser.register_analysis(loop_analyser, 1, "main_group")
code_analyser.register_analysis(output_analyser, 1, "main_group")
code_analyser.register_analysis(scope_analyser, 1, "main_group")
code_analyser.register_analysis(length_analyser, 2, "main_group")


for python_file in python_files:
    try:
        feedback_data = code_analyser.analyse(python_file)
    except RedBaronParsingFailure:
        print("This file could not be parsed by redbaron.")
        continue
    except PythonParsingFailure:
        print("This file is not valid python code")
        continue

    if contains_feedback(feedback_data):
        code_analyser.print_separator()
        print("Feedback for file {0}".format(python_file))
        if not settings.compact:
            code_analyser.output_feedback(feedback_data)
        else:
            code_analyser.output_compact_feedback(feedback_data)
        code_analyser.print_separator()
