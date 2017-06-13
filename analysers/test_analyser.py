from analysers.analyser import Analyser


class TestAnalyser(Analyser):
    feedback = (False, "")

    def __init__(self, feedback):
        Analyser.__init__(self)
        self.feedback = feedback

    def analyse(self, function_def, file_reader):
        return self.feedback

    def output_feedback(self, feedback_data):
        print(feedback_data)

    def output_compact_feedback(self, feedback_data_list):
        print(feedback_data_list[0])
