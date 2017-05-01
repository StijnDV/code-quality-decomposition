from __future__ import print_function

import argparse
import sys
import os
import time
from redbaron import RedBaron
from localbaronfinder import LocalBaronFinder
from data_slices import find_slice_seeds, get_slice_for_variable
from returnprint_analyzer import analyze_function_print_return


def remove_old_feedback(root_folder):
    for directory, subdirectories, files in os.walk(root_folder):
        for input_file in files:
            # remove old file feedback_ is to remove old files that where once used
            if input_file.endswith(os.path.splitext(input_file)[0] + "_feedback.txt") \
                    or input_file.startswith("feedback_" + input_file):
                os.remove(os.path.join(directory, file))


def generate_feedback_file(file_name):
    # Redirect all print statements to the feedback file
    fst = read_fst(file_name)
    local_baron_finder = LocalBaronFinder(fst, None)
    function_definitions = local_baron_finder.find_all('def')

    for function_definition in function_definitions:
        print('Feedback on function', function_definition.name, ':')
        print('Mixing of return and print: ')
        analyze_function_print_return(function_definition)
        print('Functional cohesion: ')
        slice_seeds = find_slice_seeds(function_definition)
        slices = list()
        for slice_seed in slice_seeds:
            slices.append(set(get_slice_for_variable(function_definition, slice_seed)))

        print()


def analyze_slices(slices):
    slice_count = len(slices)
    return slice_count


def create_new_feedback(root_folder, output_to_file=False):
    parsed_files = list()
    failed_files = list()
    for directory, subdirectories, files in os.walk(root_folder):
        for input_file in files:
            # Create new feedback
            if not input_file.endswith(".py"):
                continue
            file_name = os.path.join(directory, input_file)
            print('parsing:', file_name)
            orig_stdout = sys.stdout
            if output_to_file:
                output_file = open(os.path.join(directory, os.path.splitext(input_file)[0] + "_feedback.txt"), 'w')
                sys.stdout = output_file
            try:
                generate_feedback_file(file_name)
            except Exception as inst:
                failed_files.append(file_name)
                print("Failed to generate feedback exeption:")
                print(inst)
            finally:
                if output_to_file:
                    output_file.close()
                    sys.stdout = orig_stdout
            parsed_files.append(file_name)
    return parsed_files, failed_files


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", dest="filename")
    parser.add_argument('-folder', action='store_true', default=False)
    return parser.parse_args()


def main(parsed_args):
    if parsed_args.folder:
        start_time = time.clock()
        remove_old_feedback("../ProgNs2014")
        parsed_files, failed_files = create_new_feedback("../ProgNs2014", output_to_file=True)
        end_time = time.clock()
        print("Took", end_time - start_time, "seconds to analyze", len(parsed_files) + len(failed_files),
              "files of which", len(failed_files), "failed.")
        print("Failed files:", failed_files)
    else:
        generate_feedback_file(parsed_args.filename)


def read_fst(filename):
    with open(filename, 'r') as input_file:
        fst = RedBaron(input_file.read())
    return fst


if __name__ == '__main__':
    args = parse_arguments()
    main(args)
