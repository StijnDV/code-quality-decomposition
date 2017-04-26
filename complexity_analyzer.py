from __future__ import print_function

import lizard

def analyze_complexity(filename):
    analyze_result = lizard.analyze_file(filename)
    for function in analyze_result.function_list:
        print(function.__dict__)