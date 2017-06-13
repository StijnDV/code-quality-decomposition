from file_reader import FileReader
from collections import defaultdict


class CodeAnalyser:

    def __init__(self, separator_char='*'):
        self.separator_char = separator_char
        self.analyser_groups = defaultdict(lambda: defaultdict(list))

    def register_analysis(self, analyser, priority=1, group_name="no_grouping"):
        analyser_group = self.analyser_groups[group_name]
        priority_list = analyser_group[priority]
        priority_list.append(analyser)

    def deregister_analysis(self, analyser, priority=1, group_name="no_grouping"):
        analyser_group = self.analyser_groups[group_name]
        priority_list = analyser_group[priority]
        priority_list.remove(analyser)

    def print_separator(self):
        print(self.separator_char * 80)

    def analyse(self, file_name):
        file_reader = FileReader(file_name)
        feedback_data = defaultdict(dict)
        for func in file_reader.functions:
            for group in self.analyser_groups.values():
                for priority in sorted(group.keys()):
                    priority_gave_feedback = False
                    for analyser in group[priority]:
                        feedback = analyser.analyse(func, file_reader)
                        if feedback[0]:
                            priority_gave_feedback = True
                        feedback_data[func][analyser] = feedback
                    # Don't run the lower priority's if any of the higher priority gave feedback
                    if priority_gave_feedback:
                        break

        return feedback_data

    @staticmethod
    def contains_feedback(function_feedback_data):
        has_feedback = False
        for analyser in function_feedback_data:
            if function_feedback_data[analyser][0]:
                has_feedback = True
        return has_feedback

    def output_feedback(self, feedback_data):
        for func in feedback_data.keys():
            has_feedback = CodeAnalyser.contains_feedback(feedback_data[func])
            if has_feedback:
                print("Feedback on function <{0}>".format(func.name))
                for analyser in feedback_data[func].keys():
                    if feedback_data[func][analyser][0]:
                        analyser.output_feedback(feedback_data[func][analyser][1])

    def output_compact_feedback(self, feedback_data):
        analyser_to_feedback = defaultdict(dict)
        for func in feedback_data.keys():
            for analyser in feedback_data[func].keys():
                if not feedback_data[func][analyser][0]:
                    continue
                analyser_to_feedback[analyser][func] = feedback_data[func][analyser][1]
        for analyser in analyser_to_feedback.keys():
            analyser.output_compact_feedback(analyser_to_feedback[analyser])
