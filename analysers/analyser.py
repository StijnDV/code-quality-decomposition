class Analyser:
    default_return = (False, [])


    def __init__(self):
        pass

    def analyse(self, function_def, file_reader):
        raise NotImplementedError(
            "Class {} doesn't implement analyse()".format(self.__class__.__name__)
        )

    def output_feedback(self, feedback_data):
        raise NotImplementedError(
            "Class {} doesn't implement output_feedback(feedback_data)".format(self.__class__.__name__)
        )

    def output_compact_feedback(self, feedback_data_list):
        raise NotImplementedError(
            "Class {} doesn't implement output_compact_feedback(feedback_data_list)".format(self.__class__.__name__)
        )
