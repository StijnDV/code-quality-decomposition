from __future__ import print_function

from redbaron_filters import DocStringFilter


def get_line_number(node):
    return node.absolute_bounding_box.top_left.line


def remove_non_code(input_func, copy):
    func = input_func.copy() if copy else input_func
    func = remove_comments(func, False)
    func = remove_docstrings(func, False)
    return func


def remove_comments(input_func, copy):
    def is_removable_comment(comment_node):
        return comment_node not in non_removable_comments
    func = input_func.copy() if copy else input_func

    non_removable_comments = set()
    comment = func.find('comment')
    while comment is not None:
        try:
            comment.parent.remove(comment)
        except ValueError:
            # one of the comments in redbaron i cant deal with just forget this comment
            # these are comments at the end of lines that are control structures
            non_removable_comments.add(comment)
        comment = func.find('comment', is_removable_comment)
    return func


def remove_docstrings(input_func, copy):
    func = input_func.copy() if copy else input_func
    docstring_filter = DocStringFilter()
    docstring = func.find('string', docstring_filter.filter)
    while docstring is not None:
        docstring.parent.remove(docstring)
        docstring = func.find('string', docstring_filter.filter)
    return func


def name_nodes_to_dict(name_nodes):
    return {node.value: node for node in name_nodes}


def name_nodes_to_set(name_nodes):
    return {node.value for node in name_nodes}
