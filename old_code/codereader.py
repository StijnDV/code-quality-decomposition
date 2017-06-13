from __future__ import print_function, division

import argparse
import os
import traceback

from redbaron import RedBaron

from static_feedback import *
from redbaron_python_scoping import LocalBaronFinder
from complexity_analyser import create_for_dict, create_while_dict
from returnprint_analyser import analyse_function_print_return
from complexity_analyser import analyse_complexity
from redbaron_util import name_nodes_to_set
from redbaron_filters import ExcludeNamesFilter

reserved_words = {
    "and", "assert", "break", "class", "continue", "def", "del", "elif", "else", "except",
    "exec", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda", "not",
    "or", "pass", "print", "raise", "return", "try", "while", "Data", "Float", "Int", "Numeric",
    "Oxphys", "array", "close", "float", "int", "input", "open", "range", "type", "write",
    "zeros", "acos", "asin", "atan", "cos", "e", "exp", "fabs", "floor", "log", "log10", "pi",
    "sin", "sqrt", "tan", "len", "xrange", "True", "False"
}

import_reserved_words = set()

def remove_old_feedback(root_folder):
    for directory, subdirectories, files in os.walk(root_folder):
        for input_file in files:
            # remove old file feedback_ is to remove old files that where once used
            if input_file.endswith(os.path.splitext(input_file)[0] + "_feedback.txt") \
                    or input_file.startswith("feedback_" + input_file):
                os.remove(os.path.join(directory, file))


def generate_top_level_statement_feedback(top_level_function):
    cyclomatic_complexity, halstead_metrics, raw_metrics = analyse_complexity(top_level_function)
    if top_level_function[0].value == "pass":
        return False, []
    ifs = top_level_function.find_all('if')
    main_if = ifs.filter(lambda if_node: if_node.test.find('name').value == "__name__")
    lines_in_main_if = 0
    if main_if:
        lines_in_main_if = 1 + main_if[0].absolute_bounding_box.bottom_right.line\
                           - main_if[0].absolute_bounding_box.top_left.line
    leftover_lines = raw_metrics.sloc - lines_in_main_if
    return True, [leftover_lines]


def generate_top_level_statement_function(file_name):
    # generate the function that is all code that is not in a function
    # assumes no classes where used
    fst = read_fst(file_name)

    while fst.find('def', lambda node: node.parent.parent is None) is not None:
        fst.remove(fst.find('def', lambda node: node.parent.parent is None))
    while fst.find('class', lambda node: node.parent.parent is None) is not None:
        fst.remove(fst.find('class', lambda node: node.parent.parent is None))
    while fst.find('import', lambda node: node.parent.parent is None) is not None:
        fst.remove(fst.find('import', lambda node: node.parent.parent is None))

    non_function_function = RedBaron("def main():\n    pass")
    if len(fst) > 0:
        non_function_function[0].value = fst.dumps()
    return non_function_function[0]


def get_all_functions(full_fst):
    local_baron_finder = LocalBaronFinder(full_fst, None)
    defs_to_search = local_baron_finder.find_all('def')
    function_definitions = list(defs_to_search)
    # function_definitions.append(top_level_as_function)
    while len(defs_to_search) > 0:
        local_baron_finder_func = LocalBaronFinder(defs_to_search.pop())
        nested_functions = local_baron_finder_func.find_all('def')
        for func_def in nested_functions:
            defs_to_search.append(func_def)
            function_definitions.append(func_def)
    return function_definitions


def get_top_level_loops(for_nodes, while_nodes, level):
    loops = []
    loops.extend(get_top_level_for_loops(for_nodes, level))
    loops.extend(get_top_level_while_loops(while_nodes, level))
    return loops


def get_top_level_for_loops(for_nodes, level):
    level_for_loops = []
    for for_info in for_nodes:
        if for_info.node.parent == level:
            level_for_loops.append(for_info)
    return level_for_loops


def get_top_level_while_loops(while_nodes, level):
    level_while_loops = []
    for while_info in while_nodes:
        if while_info.node.parent == level:
            level_while_loops.append(while_info)
    return level_while_loops


def get_var_scope(var_name, func_def):
    first_use = float('inf')
    last_use = 0
    name_node_list = func_def.find_all('name', value=var_name)
    for name_node in name_node_list:
        line = name_node.absolute_bounding_box.top_left.line
        if line < first_use:
            first_use = line
        if line > last_use:
            last_use = line
    return (first_use, last_use), var_name


def get_all_variable_scopes(func_def):
    scope_list = []
    variables = name_nodes_to_set(func_def.find_all('name').filter(is_variable))
    for variable in variables:
        scope_list.append(get_var_scope(variable, func_def))

    return scope_list


def line_is_in_box(box, line_number):
    return box[0] <= line_number <= box[1]


def is_variable(name_node):
    if name_node.value in reserved_words: #Reserved python keyword probably not a variable
        return False
    if name_node.value in import_reserved_words: #Variable name was used as a import variable not a variable
        return False
    if name_node.on_attribute == 'target' and name_node.parent.type == "call_argument": # function call named argument
        return False
    if name_node.on_attribute == 'name': #function call
        return False
    if name_node.parent.type == 'atomtrailers' and name_node.index_on_parent != 0: #member of object the var is the object not its members
        return False
    #detect function calls
    if name_node.parent.type == 'atomtrailers' and len(name_node.parent.value) > 1 and name_node.parent.value[1].type == 'call':
        return False
    return True


def generate_loop_feedback(for_dict, while_dict, function_def, line_lookup, arg):
    # get the top level fors in the function
    function_level_loops = get_top_level_loops(for_dict.values(), while_dict.values(), function_def)

    # calculate shared variables between loops
    loop_cohesion_list = []
    if len(function_level_loops) > 1:
        for index, main_loop in enumerate(function_level_loops):
            main_loop_exclude = set()
            if main_loop.node.type == 'for':
                main_loop_exclude.add(main_loop.node.iterator.value)
            for compare_loop in function_level_loops[index:]:
                # prevent loops being compared to themself
                compare_loop_exclude = set()
                if compare_loop.node.type == 'for':
                    compare_loop_exclude.add(compare_loop.node.iterator.value)

                if main_loop.node == compare_loop.node:
                    continue

                main_varset = name_nodes_to_set(main_loop.node.find_all('name')
                                                .filter(is_variable)
                                                .filter(ExcludeNamesFilter([main_loop_exclude]).filter))
                compare_varset = name_nodes_to_set(compare_loop.node.find_all('name')
                                                   .filter(is_variable)
                                                   .filter(ExcludeNamesFilter([compare_loop_exclude]).filter))
                shared_variables = main_varset.intersection(compare_varset)
                if len(shared_variables) <= arg.loops:
                    loop_cohesion_list.append((shared_variables,
                                                (main_loop, line_lookup[main_loop.node]),
                                                (compare_loop, line_lookup[compare_loop.node])))
    if loop_cohesion_list:
        return True, loop_cohesion_list
    return False, []


def clean_function_definitions(function_definitions, ignored_function_names):
    cleaned_functions = []

    for function_definition in function_definitions:
        if function_definition.name in ignored_function_names:
            continue

        problematic_comments = set()
        comment = function_definition.find('comment')
        while comment is not None:
            try:
                comment.parent.remove(comment)
            except:
                # one of the comments in redbaron i cant deal with just forget this comment
                problematic_comments.add(comment)
            comment = function_definition.find('comment', lambda node: node not in problematic_comments)
        docstring = function_definition.find('string', lambda x: x.parent == function_definition)
        while docstring is not None:
            docstring.parent.remove(docstring)
            docstring = function_definition.find('string', lambda x: x.parent == function_definition)

        cleaned_functions.append(function_definition)

    return cleaned_functions


def analyze_break_points(fst, function_definition, arg):
    top_line = function_definition.absolute_bounding_box.top_left.line
    bottom_line = function_definition.absolute_bounding_box.bottom_right.line
    size = bottom_line - top_line

    if size < arg.scopes:
        return False, []
    scopes_list = get_all_variable_scopes(function_definition)
    break_points_analyze = []
    for line in xrange((top_line + (size // 3)), (bottom_line - (size // 3))):
        # Don't break in the middle of a control structure
        if function_definition.at(line).parent_find(['for', 'while', 'if', 'else', 'elif']):
            continue
        top_scopes = []
        in_scopes = []
        bottom_scopes = []
        for scope in scopes_list:
            if line < scope[0][0]:
                top_scopes.append(scope)
            elif line > scope[0][1]:
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
        break_points_analyze.append((line, in_scopes, top_scopes, bottom_scopes))
    if break_points_analyze:
        return True, break_points_analyze
    return False, break_points_analyze

def set_reserved_import_names(fst):
    global import_reserved_words
    named_imports = fst.find_all(['name_as_name', 'dotted_as_name'])
    for named_import in named_imports:
        if named_import.target != '':
            import_reserved_words.add(named_import.target)

def generate_loop_line_lookup(fst):
    line_lookup_dict = {}
    loops = fst.find_all(['for', 'while'])
    for loop in loops:
        line_lookup_dict[loop] = (loop.absolute_bounding_box.top_left.line, loop.absolute_bounding_box.bottom_right.line)
    return line_lookup_dict

def count_non_empty_lines(string):
    non_empty_lines = 0
    for line in string.split('\n'):
        if line.strip() != '':
            non_empty_lines += 1
    return non_empty_lines

def generate_length_feedback(function_definition, max_length):
    function_string = function_definition.dumps()
    size = count_non_empty_lines(function_string)
    return (size > max_length, size)

def generate_feedback_file(file_name, arg):
    fst = read_fst(file_name)
    feedback = {}

    set_reserved_import_names(fst)
    function_definitions = get_all_functions(fst)
    ignored_function_names = set()
    loops_lines_dict = generate_loop_line_lookup(fst)

    cleaned_functions = clean_function_definitions(function_definitions, ignored_function_names)

    if arg.main:
        top_level_as_function = generate_top_level_statement_function(file_name)
        function_definitions.append(top_level_as_function)
        # Do something with this info
        # generate_top_level_statement_feedback(top_level_as_function)

    for function_definition in cleaned_functions:
        feedback_dict = {
            "function_to_long": (False, []),
            "return_print": (False, []),
            "multiple_top_level_loops": (False, []),
            "can_break_at_line": (False, [])
        }
        if arg.loops:
            for_dict = create_for_dict(function_definition)
            while_dict = create_while_dict(function_definition)
            feedback_dict["multiple_top_level_loops"] = generate_loop_feedback(for_dict, while_dict, function_definition, loops_lines_dict, arg)

        if arg.scopes:
            feedback_dict["can_break_at_line"] = analyze_break_points(fst, function_definition, arg)

        if arg.return_analyze:
            feedback_dict["return_print"] = analyse_function_print_return(function_definition)

        if arg.length:
            feedback_dict["function_to_long"] = generate_length_feedback(function_definition, arg.length)
        feedback[function_definition] = feedback_dict

    return feedback

def has_feedback(feedback_dict):
    for function_feedback in feedback_dict.values():
        if has_function_feedback(function_feedback):
            return True
    return False

def has_function_feedback(function_feedback_dict):
    for single_feedback in function_feedback_dict.values():
        if single_feedback[0]:
            return True
    return False

def find_line_numbers(filename, strings):
    line_numbers = [None] * len(strings)
    with open(filename) as file:
        for line_number, line in enumerate(file, start=1):
            for index, search_term in enumerate(strings):
                if line.find(search_term) != -1:
                    line_numbers[index] = line_number
    return line_numbers


def list_to_string(input_list, separator):
    return separator.join(map(str, input_list))


def output_loop_feedback(filename, feedback_data):
    loop_lines = set()
    for loop_fault in feedback_data:
        loop_lines.add(loop_fault[1][1][0])
        loop_lines.add(loop_fault[2][1][0])
    sorted_lines = list(loop_lines)
    sorted_lines.sort()
    print(LOOPS_FEEDBACK.format(list_to_string(sorted_lines, ', ')))

def get_best_split(feedback_data):
    best_split = feedback_data[0]
    for split_option in feedback_data:
        if split_option[1] < best_split[1]:
            best_split = split_option
    return best_split

def output_break_feedback(filename, feedback_data):
    best_split = get_best_split(feedback_data)
    print(BREAK_FEEDBACK.format(str(best_split[0]), list_to_string([info[1] for info in best_split[1]], ', ')))
    print(BREAK_DISCLAIMER)

def get_function_names(function_def_list):
    return [node.name for node in function_def_list]

def print_separator():
    print('*' * 80)

def output_compact_feedback(filename, feedback_dict, args):
    if has_feedback(feedback_dict):
        print_separator()
        print(filename)
    else:
        return
    to_long = []
    top_loops = []
    break_at = []
    return_print = []
    for func_def in feedback_dict.keys():
        function_feedback = feedback_dict[func_def]
        if function_feedback["function_to_long"][0]:
            to_long.append(func_def)
        if function_feedback["multiple_top_level_loops"][0]:
            top_loops.append(func_def)
        if function_feedback["can_break_at_line"][0]:
            break_at.append(func_def)
        if function_feedback["return_print"][0]:
            return_print.append(func_def)
    if len(top_loops) > 0:
        loop_lines = set()
        for func_def in top_loops:
            feedback_data = feedback_dict[func_def]["multiple_top_level_loops"][1]
            for loop_fault in feedback_data:
                loop_lines.add(loop_fault[1][1][0])
                loop_lines.add(loop_fault[2][1][0])
        sorted_lines = list(loop_lines)
        sorted_lines.sort()
        print(LOOPS_COMPACT_FEEDBACK.format(list_to_string(get_function_names(top_loops), ', '),
                                            list_to_string(sorted_lines, ', ')))
    if len(return_print) > 0:
        print(MIXED_PRINT_RETURN_COMPACT_FEEDBACK.format(list_to_string(get_function_names(return_print), ', ')))
    if len(break_at) > 0:
        for func_def in break_at:
            feedback_data = feedback_dict[func_def]["can_break_at_line"][1]
            best_split = get_best_split(feedback_data)
            print(BREAK_COMPACT_FEEDBACK.format(
                list_to_string(get_function_names(break_at), ', '),
                str(best_split[0]),
                list_to_string([info[1] for info in best_split[1]], ', ')
            ))
        print(BREAK_DISCLAIMER)
    if len(to_long) > 0:
        print(FUNCTION_TO_LONG_COMPACT_FEEDBACK.format(', '.join(get_function_names(to_long)), str(arg.length)))
    print_separator()

def output_feedback(filename, feedback_dict, args):
    if has_feedback(feedback_dict):
        print_separator()
        print(filename)
    else:
        return
    for func_def in feedback_dict.keys():
        function_name = func_def.name
        function_feedback = feedback_dict[func_def]
        if not has_function_feedback(function_feedback):
            continue

        good_feedback_given = False
        print('Feedback on function: <' + function_name + '>')
        if function_feedback["multiple_top_level_loops"][0]:
            good_feedback_given = True
            feedback_data = function_feedback["multiple_top_level_loops"][1]
            output_loop_feedback(filename, feedback_data)
        if function_feedback["can_break_at_line"][0]:
            good_feedback_given = True
            feedback_data = function_feedback["can_break_at_line"][1]
            output_break_feedback(filename, feedback_data)
        if function_feedback["return_print"][0]:
            good_feedback_given = True
            print(MIXED_PRINT_RETURN_FEEDBACK)
        if not good_feedback_given and function_feedback["function_to_long"][0]:
            feedback_data = function_feedback["function_to_long"][1]
            print(FUNCTION_TO_LONG_FEEDBACK.format(feedback_data))
    print_separator()


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
    parser.add_argument('-main', action='store_true', default=False)
    parser.add_argument('-return_analyze', action='store_true', default=False)
    parser.add_argument('-loops', nargs='?', const=2, type=int)
    parser.add_argument('-scopes', nargs='?', const=10, type=int)
    parser.add_argument('-length', nargs='?', const=50, type=int)
    parser.add_argument('-compact', action='store_true')

    return parser.parse_args()


def main(parsed_args):
    if parsed_args.folder:
        files = get_python_files(parsed_args.folder)
    else:
        files = [parsed_args.file]
    for file_name in files:
        print("Starting Parsing of:", file_name)
        try:
            feedback = generate_feedback_file(file_name, parsed_args)
        except Exception:
            print(traceback.format_exc())
        else:
            if parsed_args.compact:
                output_compact_feedback(file_name, feedback, arg)
            else:
                output_feedback(file_name, feedback, arg)
        print("Done parsing:", file_name)


def read_fst(filename):
    with open(filename, 'r') as input_file:
        fst = RedBaron(input_file.read())
    return fst


if __name__ == '__main__':
    arg = parse_arguments()
    # print(arg)
    main(arg)
