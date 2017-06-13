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
    parser.add_argument('-v', action='store_true')
    parser.add_argument('-main', action='store_true')
    parser.add_argument('-return_analyze', dest="output", action='store_true')
    parser.add_argument('-loops', dest="loops_max_shared", nargs='?', const=2, type=int)
    parser.add_argument('-scopes', nargs='?', const=10, type=int)
    parser.add_argument('-length', nargs='?', const=30, type=int)
    parser.add_argument('-plot', dest='clustering_threshold', nargs='?', const=5, type=int)
    parser.add_argument('-compact', action='store_true')
    return parser.parse_args()


def create_status_message(settings):
    message_subs = {"loop": "Disabled", "loop_conf": "N\A",
                    "scope": "Disabled", "scope_conf": "N\A",
                    "output": "Disabled",
                    "plot": "Disabled", "plot_conf": "N\A",
                    "length": "Disabled", "length_conf": "N\A"}
    status_message = "Configuration:\n" \
                     "\tOutput analyser ({output})\n" \
                     "\tLoop analyser ({loop}) conf: maximum shared variables = {loop_conf}\n" \
                     "\tScope analyser ({scope}) conf: minimum function length = {scope_conf}\n" \
                     "\tPlot analyser ({plot}) conf: clustering threshold = {plot_conf}\n" \
                     "\tLength analyser ({length}) conf: maximum function length = {length_conf}\n"
    if settings.loops_max_shared:
        message_subs["loop"] = "Active"
        message_subs["loop_conf"] = settings.loops_max_shared
    if settings.scopes:
        message_subs["scope"] = "Active"
        message_subs["scope_conf"] = settings.scopes
    if settings.output:
        message_subs["output"] = "Active"
        message_subs["output_conf"] = settings.output
    if settings.clustering_threshold:
        message_subs["plot"] = "Active"
        message_subs["plot_conf"] = settings.clustering_threshold
    if settings.length:
        message_subs["length"] = "Active"
        message_subs["length_conf"] = settings.length

    return status_message.format(**message_subs)

settings = parse_arguments()
if settings.filename:
    python_files = [settings.filename]
else:
    python_files = get_python_files(settings.folder)

code_analyser = CodeAnalyser()

if settings.loops_max_shared:
    loop_analyser = LoopAnalyser(settings.loops_max_shared)
    code_analyser.register_analysis(loop_analyser, 1, "main_group")
if settings.scopes:
    scope_analyser = ScopeAnalyser(settings.scopes)
    code_analyser.register_analysis(scope_analyser, 1, "main_group")
if settings.output:
    output_analyser = OutputAnalyser()
    code_analyser.register_analysis(output_analyser, 1, "main_group")
if settings.clustering_threshold:
    plot_analyser = PlotAnalyser(settings.clustering_threshold)
    code_analyser.register_analysis(plot_analyser, 1, "main_group")
if settings.length:
    length_analyser = LengthAnalyser(settings.length)
    code_analyser.register_analysis(length_analyser, 2, "main_group")

if settings.v:
    status_message = create_status_message(settings)
    print(status_message)

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
