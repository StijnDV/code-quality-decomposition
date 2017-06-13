import os
import ast
import argparse
import traceback
from redbaron import RedBaron

redbaron_fails = 0
invalid_python_fails = 0
redbaron_files = []
invalid_python_files = []

def check_file(file_name):
    global redbaron_fails
    global invalid_python_fails
    global redbaron_files
    global invalid_python_files
    with open(file_name, 'r') as input_file:
        code_snippet = input_file.read()
    try:
        ast.parse(code_snippet)
    except:
        invalid_python_fails += 1
        invalid_python_files.append(file_name)
        return

    try:
        RedBaron(code_snippet)
    except Exception as inst:
        redbaron_fails += 1
        redbaron_files.append(file_name)
        traceback_string = traceback.format_exc()
        if 'ParsingError: Error, got an unexpected token STRING here:' in traceback_string:
            print('*' * 120)
            print(traceback_string)
            print('*' * 120)
        return

def main(parsed_args):
    global redbaron_fails
    global invalid_python_fails
    global redbaron_files
    global invalid_python_files

    for directory, subdirectories, files in os.walk(parsed_args.folder):
        for input_file in files:
            # Create new feedback
            if not input_file.endswith(".py"):
                continue
            file_name = os.path.join(directory, input_file)
            print("Checking :" + file_name)
            check_file(file_name)
    print("invalid python in :" + str(invalid_python_fails) + "files")
    print("file list :" + str(invalid_python_files))
    print("RedBaron_fail in :" + str(redbaron_fails) + "files")
    print("file list :" + str(redbaron_files))

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", dest="folder")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    main(args)