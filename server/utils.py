# -*- coding:utf-8 -*-
# Author: xiaohao@corp.netease.com

import ast
import jedi
import os

from enum import Enum
from define import *


class Singleton(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = object.__new__(cls, *args, **kwargs)
            cls._instance.init(*args, **kwargs)
        return cls._instance


class PropertyType(Enum):
    PROPERTY = 1
    FUNCTION = 2
    VARIABLE = 3


class CompontentProperty(object):

    def __init__(self, name, path, position, prop_type=PropertyType.PROPERTY) -> None:
        self.prop_name = name
        self.prop_type = prop_type
        self.path = os.path.normpath(path)
        self.position = self.position_change(position)

    def path_clear(self, path):
        str_list = path.split('\\')
        _new_str_list = []
        for _str in str_list:
            if _str:
                _new_str_list.append(_str)
        ans_path = '\\'.join(_new_str_list)
        return ans_path

    def position_change(self, position):
        if self.prop_type == PropertyType.FUNCTION:
            line, _start, _end = position
            return (line, _start + 4, _start + 4 + len(self.prop_name))
        return position


def get_filter_print_txt(file_path):
    lines = []
    with open(file_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        line = lines[i]
        if line.lstrip().startswith("print "):
            lines[i] = line.replace("print ", "pass # print ", 1)
    return "".join(lines)


def get_file_class_property(file_path, clsname) -> dict:
    try:
        reads = get_filter_print_txt(file_path)
        ast_root_node = ast.parse(reads)
        for body_node in ast_root_node.body:
            if type(body_node) == ast.ClassDef:
                class_name = body_node.name
                if class_name != clsname:
                    continue
                class_body_list = body_node.body
                class_prop_dict = {}
                for prop_body in class_body_list:
                    if type(prop_body) == ast.Expr:
                        expr_value = prop_body.value
                        if hasattr(expr_value, 'func') and type(expr_value.func) == ast.Name and expr_value.func.id == 'Property':
                            prop_name = expr_value.args[0].value
                            prop_lineno = prop_body.lineno
                            prop_offset = prop_body.col_offset
                            prop_end_offset = prop_body.end_col_offset
                            position = (prop_lineno - 1, prop_offset, prop_end_offset)
                            class_prop_dict[prop_name] = CompontentProperty(
                                prop_name, file_path, position, PropertyType.PROPERTY)
                    elif type(prop_body) == ast.FunctionDef:
                        func_name = prop_body.name
                        func_lineno = prop_body.lineno
                        func_offset = prop_body.col_offset
                        func_end_offset = prop_body.end_col_offset
                        position = (func_lineno - 1, func_offset, func_end_offset)
                        class_prop_dict[func_name] = CompontentProperty(
                            func_name, file_path, position, PropertyType.FUNCTION)
                    elif type(prop_body) == ast.Assign:
                        if len(prop_body.targets) == 1:
                            ast_name = prop_body.targets[0]
                            avr_name = ast_name.id
                            func_lineno = ast_name.lineno
                            func_offset = ast_name.col_offset
                            func_end_offset = ast_name.end_col_offset
                            position = (func_lineno - 1, func_offset, func_end_offset)
                            class_prop_dict[avr_name] = CompontentProperty(
                                avr_name, file_path, position, PropertyType.VARIABLE)
                return class_prop_dict
    except Exception as e:
        print(file_path)
        print(e)
    print("no find class_prop_dict:%s", file_path, clsname)
    return {}


def get_definition_name_and_class(text_doc, text_pos: Position):
    """
    判断该位置后的属性是否为class的属性，即是否以'self.'开头, 返回类名和跳转函数名
    character的位置为光标所在位置
    返回，第一个为类名，第二个为函数名
    """
    line_num = text_pos.line
    chr = text_pos.character
    lines = text_doc.lines
    if line_num < 0 or line_num >= len(lines):
        return None
    line = lines[line_num]
    if chr <= 5 or chr >= len(line):
        return None
    f_str = ''.join(lines)
    script = jedi.Script(f_str)
    node_name = script.get_context(line_num + 1, chr)
    class_name = ''
    if type(node_name) == jedi.api.classes.Name and node_name.type == 'function':
        parent = node_name.parent()
        if type(parent) == jedi.api.classes.Name and parent.type == 'class':
            class_name = parent.name
    if not class_name:
        return None
    pos = (line_num + 1, chr)
    leaf = script._module_node.get_name_of_position(pos)
    if not leaf or leaf.type != 'name':
        return None
    p_leaf = leaf.get_previous_leaf()
    if not p_leaf or p_leaf.value != '.':
        return None
    pre_leaf = p_leaf.get_previous_leaf()
    if not pre_leaf or pre_leaf.value != 'self':
        return None
    return class_name, leaf.value
