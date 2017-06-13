import ast

from redbaron import RedBaron
from redbaron_util import remove_comments


class RedBaronParsingFailure(Exception):
    pass


class PythonParsingFailure(Exception):
    pass


class FileReader:
    def __init__(self, filename):
        self.filename = filename
        self._file_content = None
        self._redbaron_fst = None
        self._main_function = None
        self._function_list = None
        self._cleaned_function_dict = dict()

    @property
    def file_content(self):
        if not self._file_content:
            with open(self.filename) as f:
                self._file_content = f.read()
        return self._file_content

    @property
    def redbaron_fst(self):
        if not self._redbaron_fst:
            try:
                self._redbaron_fst = RedBaron(self.file_content)
            except Exception:
                try:
                    ast.parse(self._file_content)
                except Exception:
                    raise PythonParsingFailure(
                        "The python file {0} could not be parsed by python.".format(self.filename)
                    )
                else:
                    raise RedBaronParsingFailure(
                        "The python file {0} could not be parsed by redbaron.".format(self.filename)
                    )
        return self._redbaron_fst

    @property
    def functions(self):
        if not self._function_list:
            self._function_list = self.redbaron_fst.find_all('def')
        return self._function_list

    @property
    def main_function(self):
        if not self._main_function:
            # Get all top level nodes that are not imports or classes or functions
            nodes = self.redbaron_fst.filter(lambda node: node.type not in {'def', 'class', 'import'})
            generated_main = RedBaron("def generated_main():\n    pass")
            if len(nodes) > 0:
                main_string = nodes.dumps()
                cleaned_main = ""
                for line in main_string.splitlines():
                    if line.strip() != '':
                        cleaned_main += line + '\n'
                generated_main[0].value = cleaned_main
            self._main_function = generated_main
        return self._main_function

    @property
    def cleaned_functions(self):
        for func in self.functions:
            if func not in self._cleaned_function_dict:
                self._cleaned_function_dict[func] = remove_comments(func, True)
        return self._cleaned_function_dict.values()

    def get_clean_function(self, function_def):
        if function_def not in self._cleaned_function_dict:
            self._cleaned_function_dict[function_def] = remove_comments(function_def, True)
        return self._cleaned_function_dict[function_def]
