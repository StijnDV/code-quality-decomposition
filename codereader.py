from __future__ import print_function

import argparse
from redbaron import RedBaron
from baronfinder import find_global_variable_name_nodes, find_function_parameters
from localbaronfinder import LocalBaronFinder
from returnprint_analyzer import analyze_function_print_return
from complexity_analyzer import analyze_complexity
from graph_builder import build_graph
from data_slices import find_slice_seeds, get_slice_for_variable

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", dest="filename")
    return parser.parse_args()


def main(parsed_args):
    analyze_complexity("TestFiles/complex_functions.py")
    fst = read_fst(parsed_args.filename)
    fst2 = read_fst("Testfiles/two_parts.py")
    local_baron_finder2 = LocalBaronFinder(fst2, None)
    function_definitions2 = local_baron_finder2.find_all('def')
    for function_definition in function_definitions2:
        print("Function: " + function_definition.name)
        # build_graph(function_definition)
        slice_seeds = find_slice_seeds(function_definition)
        for slice_seed in slice_seeds:
            get_slice_for_variable(function_definition, slice_seed)
        analyze_function_print_return(function_definition)

    local_baron_finder = LocalBaronFinder(fst, None)
    function_definitions = local_baron_finder.find_all('def')
    for function_definition in function_definitions:
        # build_graph(function_definition)
        analyze_function_print_return(function_definition)


def read_fst(filename):
    with open(filename, 'r') as input_file:
        fst = RedBaron(input_file.read())
    return fst


if __name__ == '__main__':
    args = parse_arguments()
    main(args)
