# -*- coding:utf-8 -*-
# Author: xiaohao@corp.netease.com


import ast
import os
import json
import argparse
import logging

import jedi
import utils

from cProfile import label
from unicodedata import name
from enum import Enum
from typing import Optional

from pygls.server import LanguageServer
from define import *
from relation import Relation


logging.basicConfig(filename="pygls.log", level=logging.DEBUG, filemode="w")



class PythonLanguageServer(LanguageServer):
    CMD_COUNT_DOWN_BLOCKING = 'countDownBlocking'
    CMD_COUNT_DOWN_NON_BLOCKING = 'countDownNonBlocking'
    CMD_PROGRESS = 'progress'
    CMD_REGISTER_COMPLETIONS = 'registerCompletions'
    CMD_SHOW_CONFIGURATION_ASYNC = 'showConfigurationAsync'
    CMD_SHOW_CONFIGURATION_CALLBACK = 'showConfigurationCallback'
    CMD_SHOW_CONFIGURATION_THREAD = 'showConfigurationThread'
    CMD_UNREGISTER_COMPLETIONS = 'unregisterCompletions'
    CMD_PARSING_COMPONENTS = 'parsingComponents'
    CONFIGURATION_SECTION = 'pythonServer'


python_server = PythonLanguageServer()


@python_server.command('myVerySpecialCommandName')
def cmd_return_hello_world(ls, *args):
    return 'Hello World!'


# @python_server.feature(COMPLETION, CompletionOptions(trigger_characters=['.']))
# def completions(ls, params: Optional[CompletionParams] = None) -> CompletionList:
#     """Returns completion items."""
#     if not component_relation_dict or not main_class_components_dict or not main_class_property_dict:
#         if not parsing_components_props(ls):
#             return None
#     completions_list = get_completions_list(ls, params.text_document, params.position)
#     return completions_list


@python_server.feature(DEFINITION)
def definition(ls, params: DefinitionParams = None) -> Union[Location, List[Location], List[LocationLink], None]:
    def_uri = params.text_document.uri
    start_pos = params.position
    work_down_token = params.work_done_token
    if work_down_token:
        return None
    text_doc = ls.workspace.get_document(def_uri)
    name_info = utils.get_definition_name_and_class(text_doc, start_pos)
    if not name_info:
        return None
    if not Relation().load_json_config(ls):
        return None
    return Relation().get_definition_list(text_doc.path, name_info[0], name_info[1])


# @python_server.command(PythonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
# def count_down_10_seconds_blocking(ls, *args):
#     """Starts counting down and showing message synchronously.
#     It will `block` the main thread, which can be tested by trying to show
#     completion items.
#     """
#     for i in range(COUNT_DOWN_START_IN_SECONDS):
#         ls.show_message(f'Counting down... {COUNT_DOWN_START_IN_SECONDS - i}')
#         time.sleep(COUNT_DOWN_SLEEP_IN_SECONDS)


# @python_server.command(PythonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
# async def count_down_10_seconds_non_blocking(ls, *args):
#     """Starts counting down and showing message asynchronously.
#     It won't `block` the main thread, which can be tested by trying to show
#     completion items.
#     """
#     for i in range(COUNT_DOWN_START_IN_SECONDS):
#         ls.show_message(f'Counting down... {COUNT_DOWN_START_IN_SECONDS - i}')
#         await asyncio.sleep(COUNT_DOWN_SLEEP_IN_SECONDS)


# @python_server.command(PythonLanguageServer.CMD_PARSING_COMPONENTS)
# async def parsing_components(ls, *arg):
#     ws_rootpath = ls.workspace.root_path
#     global components_relation_path_dict
#     print('-----<parsing_components>----')
#     global src_path
#     get_search_dir_path(ws_rootpath, 'src')
#     with open(src_path + "\\" + LINTER_CACHE_JSON, 'r') as load_f:
#         components_relation_path_dict = json.load(load_f)
#         components_property_handle_func(components_relation_path_dict)
#     print(src_path)


# @python_server.feature(TEXT_DOCUMENT_DID_CHANGE)
# def did_change(ls, params: DidChangeTextDocumentParams):
#     """Text document did change notification."""
#     pass


# @python_server.feature(TEXT_DOCUMENT_DID_CLOSE)
# def did_close(server: PythonLanguageServer, params: DidCloseTextDocumentParams):
#     """Text document did close notification."""
#     pass
#     # server.show_message('Text Document Did Close')


# @python_server.feature(TEXT_DOCUMENT_DID_OPEN)
# async def did_open(ls, params: DidOpenTextDocumentParams):
#     """Text document did open notification."""
#     pass
#     # ls.show_message('Text Document Did Open')
#     # ls.show_message_log('open file: ' + params.text_document.uri)


@python_server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls, params: DidSaveTextDocumentParams):
    """Text document did save notification."""
    if not using_flag:
        return
    # ls.show_message('Text Document Did Save.')
    file_uri = params.text_document.uri
    text_doc = ls.workspace.get_document(file_uri)
    update_class_property(ls, text_doc)
    return


# @python_server.feature(WORKSPACE_DID_CHANGE_WATCHED_FILES)
# async def workspace_did_change_watched_files(ls, params: DidChangeWatchedFilesParams):
#     """ Watched files change notification. """
#     print('workspace watched files change:', params, params.changes[0].uri)


# @python_server.feature(
#     TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
#     SemanticTokensLegend(
#         token_types = ["operator"],
#         token_modifiers = []
#     )
# )

# def semantic_tokens(ls: PythonLanguageServer, params: SemanticTokensParams):
#     """See https://microsoft.github.io/language-server-protocol/specification#textDocument_semanticTokens
#     for details on how semantic tokens are encoded."""

#     TOKENS = re.compile('".*"(?=:)')

#     uri = params.text_document.uri
#     doc = ls.workspace.get_document(uri)

#     last_line = 0
#     last_start = 0

#     data = []

#     for lineno, line in enumerate(doc.lines):
#         last_start = 0

#         for match in TOKENS.finditer(line):
#             start, end = match.span()
#             data += [
#                 (lineno - last_line),
#                 (start - last_start),
#                 (end - start),
#                 0,
#                 0
#             ]

#             last_line = lineno
#             last_start = start

#     return SemanticTokens(data=data)


# @python_server.command(PythonLanguageServer.CMD_PROGRESS)
# async def progress(ls: PythonLanguageServer, *args):
#     """Create and start the progress on the client."""
#     token = 'token'
#     # Create
#     await ls.progress.create_async(token)
#     # Begin
#     ls.progress.begin(token, WorkDoneProgressBegin(title='Indexing', percentage=0))
#     # Report
#     for i in range(1, 10):
#         ls.progress.report(
#             token,
#             WorkDoneProgressReport(message=f'{i * 10}%', percentage= i * 10),
#         )
#         await asyncio.sleep(2)
#     # End
#     ls.progress.end(token, WorkDoneProgressEnd(message='Finished'))


# @python_server.command(PythonLanguageServer.CMD_REGISTER_COMPLETIONS)
# async def register_completions(ls: PythonLanguageServer, *args):
#     """Register completions method on the client."""
#     params = RegistrationParams(registrations=[
#                 Registration(
#                     id=str(uuid.uuid4()),
#                     method=COMPLETION,
#                     register_options={"triggerCharacters": "[':']"})
#              ])
#     response = await ls.register_capability_async(params)
#     if response is None:
#         ls.show_message('Successfully registered completions method')
#     else:
#         ls.show_message('Error happened during completions registration.',
#                         MessageType.Error)


# @python_server.command(PythonLanguageServer.CMD_SHOW_CONFIGURATION_ASYNC)
# async def show_configuration_async(ls: PythonLanguageServer, *args):
#     """Gets exampleConfiguration from the client settings using coroutines."""
#     try:
#         config = await ls.get_configuration_async(
#             ConfigurationParams(items=[
#                 ConfigurationItem(
#                     scope_uri='',
#                     section=PythonLanguageServer.CONFIGURATION_SECTION)
#         ]))

#         example_config = config[0].get('exampleConfiguration')

#         ls.show_message(f'pythonServer.exampleConfiguration value: {example_config}')

#     except Exception as e:
#         ls.show_message_log(f'Error ocurred: {e}')


# @python_server.command(PythonLanguageServer.CMD_SHOW_CONFIGURATION_CALLBACK)
# def show_configuration_callback(ls: PythonLanguageServer, *args):
#     """Gets exampleConfiguration from the client settings using callback."""
#     def _config_callback(config):
#         try:
#             example_config = config[0].get('exampleConfiguration')

#             ls.show_message(f'pythonServer.exampleConfiguration value: {example_config}')

#         except Exception as e:
#             ls.show_message_log(f'Error ocurred: {e}')

#     ls.get_configuration(ConfigurationParams(items=[
#         ConfigurationItem(
#             scope_uri='',
#             section=PythonLanguageServer.CONFIGURATION_SECTION)
#     ]), _config_callback)


# @python_server.thread()
# @python_server.command(PythonLanguageServer.CMD_SHOW_CONFIGURATION_THREAD)
# def show_configuration_thread(ls: PythonLanguageServer, *args):
#     """Gets exampleConfiguration from the client settings using thread pool."""
#     try:
#         config = ls.get_configuration(ConfigurationParams(items=[
#             ConfigurationItem(
#                 scope_uri='',
#                 section=PythonLanguageServer.CONFIGURATION_SECTION)
#         ])).result(2)

#         example_config = config[0].get('exampleConfiguration')

#         ls.show_message(f'pythonServer.exampleConfiguration value: {example_config}')

#     except Exception as e:
#         ls.show_message_log(f'Error ocurred: {e}')


# @python_server.command(PythonLanguageServer.CMD_UNREGISTER_COMPLETIONS)
# async def unregister_completions(ls: PythonLanguageServer, *args):
#     """Unregister completions method on the client."""
#     params = UnregistrationParams(unregisterations=[
#         Unregistration(id=str(uuid.uuid4()), method=COMPLETION)
#     ])
#     response = await ls.unregister_capability_async(params)
#     if response is None:
#         ls.show_message('Successfully unregistered completions method')
#     else:
#         ls.show_message('Error happened during completions unregistration.',
#                         MessageType.Error)


# 获得补全列表
def get_completions_list(ls: PythonLanguageServer, text_document, text_position):
    text_doc = ls.workspace.get_document(text_document.uri)
    prop_class_name = get_class_name_by_pos(text_doc, text_position)
    if not prop_class_name:
        return None
    if prop_class_name in component_relation_dict:
        return get_completions_list_by_component_name(prop_class_name)
    elif prop_class_name in main_class_components_dict:
        return get_completions_list_by_main_class_name(prop_class_name)
    else:
        return None


# 获得补全列表，此时类名为组件类名
def get_completions_list_by_component_name(component_name):
    prop_list = []
    main_class_list = component_relation_dict.get(component_name, [])
    components_name_list = set()
    for class_name in main_class_list:
        prop_list.extend(get_class_all_prop(class_name))
        components_name_list.update(main_class_components_dict.get(class_name, []))
    for _class_name in components_name_list:
        if _class_name == component_name:
            prop_list.extend(get_class_msh_prop(_class_name))
            continue
        prop_list.extend(get_class_all_prop(_class_name))
    return CompletionList(is_incomplete=False, items=prop_list)


# 获得补全列表，此时类名为主类类名
def get_completions_list_by_main_class_name(main_class_name):
    prop_list = []
    prop_list.extend(get_class_msh_prop(main_class_name))
    completions_name_list = main_class_components_dict.get(main_class_name)
    for comp_name in completions_name_list:
        prop_list.extend(get_class_all_prop(comp_name))
    return CompletionList(is_incomplete=False, items=prop_list)


def get_class_all_prop(class_name):
    prop_list = []
    prop_dict = main_class_property_dict.get(class_name, {})
    for prop_name, prop_info in prop_dict.items():
        if prop_info.prop_type == PropertyType.PROPERTY:
            item = CompletionItem(
                label=prop_name,
                kind=CompletionItemKind.Variable,
                detail='From: ' + class_name + '-> ' + 'Type: ' + 'Messiah Property')
        else:
            item = CompletionItem(
                label=prop_name,
                kind=CompletionItemKind.Method,
                detail='From: ' + class_name + '-> ' + 'Type: ' + 'Method')
        prop_list.append(item)
    return prop_list


def get_class_msh_prop(class_name):
    prop_list = []
    class_prop_dict = main_class_property_dict.get(class_name, {})
    for p_name, p_info in class_prop_dict.items():
        if p_info.prop_type == PropertyType.PROPERTY:
            prop_list.append(CompletionItem(
                label=p_name,
                kind=CompletionItemKind.Variable,
                detail='From: ' + class_name + '-> ' + 'Type: ' + 'Messiah Property'))
    return prop_list


def get_all_prop_pos(class_name, def_name):
    prop_pos_list = []
    prop_dict = main_class_property_dict.get(class_name, {})
    for prop_name, prop_info in prop_dict.items():
        if prop_name == def_name:
            location = Location(
                uri=from_fs_path(prop_info.path),
                range=Range(
                    start=Position(line=prop_info.position[0], character=prop_info.position[1]),
                    end=Position(line=prop_info.position[0], character=prop_info.position[2])
                )
            )
            prop_pos_list.append(location)
    return prop_pos_list


def get_msh_prop_pos(class_name, def_name):
    prop_pos_list = []
    prop_dict = main_class_property_dict.get(class_name, {})
    for prop_name, prop_info in prop_dict.items():
        # if prop_name == def_name and prop_info.prop_type == PropertyType.PROPERTY:
        if prop_name == def_name:
            location = Location(
                uri=from_fs_path(prop_info.path),
                range=Range(
                    start=Position(line=prop_info.position[0], character=prop_info.position[1]),
                    end=Position(line=prop_info.position[0], character=prop_info.position[2])
                )
            )
            prop_pos_list.append(location)
    return prop_pos_list


# 获得定义跳转位置列表
def get_definition_list(class_name, def_name):
    if not class_name or not def_name:
        return None
    if class_name in component_relation_dict:
        return get_definition_list_by_component_name(class_name, def_name)
    elif class_name in main_class_components_dict:
        return get_definition_list_by_main_class_name(class_name, def_name)
    return None


def get_definition_list_by_component_name(component_name, def_name):
    prop_pos_list = []
    main_class_list = component_relation_dict.get(component_name, [])
    components_name_list = set()
    for _main_class_name in main_class_list:
        prop_pos_list.extend(get_all_prop_pos(_main_class_name, def_name))
        components_name_list.update(main_class_components_dict.get(_main_class_name, []))
    for _class_name in components_name_list:
        if _class_name == component_name:
            prop_pos_list.extend(get_msh_prop_pos(_class_name, def_name))
            continue
        prop_pos_list.extend(get_all_prop_pos(_class_name, def_name))
    if not prop_pos_list:
        return None
    if len(prop_pos_list) == 1:
        return prop_pos_list[0]
    else:
        return prop_pos_list


def get_definition_list_by_main_class_name(class_name, def_name):
    prop_pos_list = []
    prop_pos_list.extend(get_msh_prop_pos(class_name, def_name))
    completions_name_list = main_class_components_dict.get(class_name)
    for _comp_name in completions_name_list:
        prop_pos_list.extend(get_all_prop_pos(_comp_name, def_name))
    if not prop_pos_list:
        return None
    if len(prop_pos_list) == 1:
        return prop_pos_list[0]
    else:
        return prop_pos_list


# 获得输入位置从属的类，并根据位置判断是否属于函数内
def get_class_name_by_pos(text_doc, text_position: Position):
    line_num = text_position.line
    chr = text_position.character
    lines = text_doc.lines
    f_str = ''.join(lines)
    script = jedi.Script(f_str)
    node_name = script.get_context(line_num + 1, chr)
    class_name = ''
    if type(node_name) == jedi.api.classes.Name and node_name.type == 'function':
        parent = node_name.parent()
        if type(parent) == jedi.api.classes.Name and parent.type == 'class':
            class_name = parent.name
    return class_name


# 扫描工作区的root_path获得src的path
def get_search_dir_path(dir_path, search_name):
    global src_path
    print(dir_path)
    print(os.walk(dir_path))
    for root, dirs, files in os.walk(dir_path):
        if search_name in dirs:
            src_path = '{0}\\{1}'.format(root, search_name)
            print(src_path)
            return True
    return False
    # if os.path.isdir(dir_path):
    #     split_1 = os.path.split(dir_path)
    #     if split_1[1] == search_name:
    #         src_path = dir_path
    #         return
    #     dir_files = os.listdir(dir_path)
    #     while dir_files:
    #         new_dir_files = []
    #         for file in dir_files:
    #             file_path = os.path.join(dir_path, file)
    #             if file == search_name:
    #                 src_path = file_path
    #                 return
    #             if os.path.isdir(file_path):
    #                 new_dir_files.extend(os.listdir(file_path))

    # if os.path.isdir(dir_path):
    #     split_1 = os.path.split(dir_path)
    #     if split_1[1] == search_name:
    #         src_path = dir_path
    #         return
    #     dir_files = os.listdir(dir_path)
    #     for file in dir_files:
    #         file_path = os.path.join(dir_path, file)
    #         if os.path.isdir(file_path):
    #             get_search_dir_path(file_path, search_name)


def get_class_property_list(compontent_path, compontent_class_name):
    class_name_list = [compontent_class_name]
    return get_file_class_property(compontent_path, class_name_list)





# 文件保存时扫描改文件，更新组件关系和类的属性
def update_class_property(ls, text_doc):
    if not component_relation_dict or not main_class_components_dict or not main_class_property_dict:
        parsing_components_props(ls)
    lines = text_doc.lines
    f_str = ''.join(lines)
    f_uri = text_doc.uri
    f_path = to_fs_path(f_uri)
    try:
        update_class_property_dict(f_str, f_path)
    except Exception as e:
        f_str = remove_str_print(f_str)
        try:
            update_class_property_dict(f_str, f_path)
        except Exception as e:
            print(e)


def update_class_property_dict(f_str, f_path):
    global main_class_property_dict
    ast_root_node = ast.parse(f_str)
    for body_node in ast_root_node.body:
        if type(body_node) == ast.ClassDef:
            class_name = body_node.name
            has_components_list_falg = False
            class_body_list = body_node.body
            class_prop_dict = {}
            _component_path_list = []
            for prop_body in class_body_list:
                if type(prop_body) == ast.Assign:
                    # '_components' 列表读取 此时更新组件关系
                    if len(prop_body.targets) != 1 or type(prop_body.targets[0]) != ast.Name:
                        continue
                    _name_node = prop_body.targets[0]
                    if _name_node.id != '_components':
                        continue
                    _value_node = prop_body.value
                    if type(_value_node) != ast.List:
                        continue
                    has_components_list_falg = True
                    for _const in _value_node.elts:
                        _component_path_list.append(_const.value)
                elif type(prop_body) == ast.Expr:
                    # 'property'属性读取
                    expr_value = prop_body.value
                    if hasattr(expr_value, 'func') and type(expr_value.func) == ast.Name and expr_value.func.id == 'Property':
                        prop_name = expr_value.args[0].value
                        prop_lineno = prop_body.lineno
                        prop_offset = prop_body.col_offset
                        prop_end_offset = prop_body.end_col_offset
                        position = (prop_lineno - 1, prop_offset, prop_end_offset)
                        class_prop_dict[prop_name] = CompontentProperty(
                            prop_name, f_path, position, PropertyType.PROPERTY)
                elif type(prop_body) == ast.FunctionDef:
                    # 函数读取
                    func_name = prop_body.name
                    func_lineno = prop_body.lineno
                    func_offset = prop_body.col_offset
                    func_end_offset = prop_body.end_col_offset
                    position = (func_lineno - 1, func_offset, func_end_offset)
                    class_prop_dict[func_name] = CompontentProperty(func_name, f_path, position, PropertyType.FUNCTION)
            if not has_components_list_falg and class_name not in component_relation_dict:
                continue
            main_class_property_dict[class_name] = class_prop_dict
            # 更新组件关系
            if has_components_list_falg:
                update_components_relation(class_name, f_path, _component_path_list)


def update_components_relation(class_name, f_path, _component_path_list):
    global components_relation_path_dict
    new_relation_dict = {}
    for _path in _component_path_list:
        _path_name_list = _path.split('.')
        new_path = src_path + '\\' + '\\'.join(_path_name_list[:-1]) + '.py' + '&' + _path_name_list[-1]
        new_relation_dict[new_path] = f_path + '&' + class_name
    print('-----update_components_relation----')
    for _key, _value in new_relation_dict.items():
        if _key in components_relation_path_dict and _value in components_relation_path_dict[_key]:
            continue
        elif _key in components_relation_path_dict and _value not in components_relation_path_dict[_key]:
            components_relation_path_dict[_key].append(_value)
            update_global_dict(_key, _value)
        else:
            components_relation_path_dict[_key] = [_value]
            update_global_dict(_key, _value)
    print('----update_components_relation end----')


def update_global_dict(component_path_and_name, main_class_path_and_name):
    global component_relation_dict
    global main_class_components_dict
    global main_class_property_dict
    sp_1 = component_path_and_name.split('&')
    sp_2 = main_class_path_and_name.split('&')
    if len(sp_1) < 2 or len(sp_2) < 2:
        return
    component_path, component_name = sp_1[0], sp_1[1]
    main_class_path, main_class_name = sp_2[0], sp_2[1]
    _class_name, class_property_dict = get_class_property_list(component_path, component_name)
    if not _class_name or not class_property_dict:
        return
    main_class_property_dict[_class_name] = class_property_dict
    if component_name not in component_relation_dict:
        component_relation_dict[component_name] = [main_class_name]
    elif main_class_name not in component_relation_dict[component_name]:
        component_relation_dict[component_name].append(main_class_name)
    if main_class_name in main_class_components_dict and component_name not in main_class_components_dict[main_class_name]:
        main_class_components_dict[main_class_name].append(component_name)
    else:
        main_class_components_dict[main_class_name] = [component_name]


def remove_str_print(f_read):
    f_str = f_read
    f_str_list = f_str.split('\n')
    for i in range(len(f_str_list)):
        start_index = f_str_list[i].find('print ')
        start_index = start_index if start_index != -1 else f_str_list[i].find('exec ')
        if start_index != -1 and start_index > 0:
            f_str_list[i] = f_str_list[i][:start_index] + 'pass'
        elif start_index == 0:
            f_str_list[i] = ''
    return '\n'.join(f_str_list)


def extend_prop_dict(prop_dict, prop_dict_tmp):
    tmp_dict = prop_dict
    if not prop_dict_tmp:
        return tmp_dict
    for prop_name, prop_pos_list in prop_dict_tmp.items():
        if prop_name in tmp_dict:
            tmp_dict[prop_name].extend(prop_pos_list)
        else:
            tmp_dict[prop_name] = prop_pos_list
    return tmp_dict


def path_clear(path):
    str_list = path.split('\\')
    _new_str_list = []
    for _str in str_list:
        if _str:
            _new_str_list.append(_str)
    ans_path = '\\'.join(_new_str_list)
    return ans_path


if __name__ == '__main__':
    python_server.start_tcp("127.0.0.1", 16471)
