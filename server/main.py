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


# @python_server.feature(COMPLETION, CompletionOptions(trigger_characters=['.']))
# def completions(ls, params: Optional[CompletionParams] = None) -> CompletionList:
#     """Returns completion items."""
#     if not component_relation_dict or not main_class_components_dict or not main_class_property_dict:
#         if not parsing_components_props(ls):
#             return None
#     completions_list = get_completions_list(ls, params.text_document, params.position)
#     return completions_list


@python_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    Relation().load_json_config(ls)


@python_server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls, params: DidSaveTextDocumentParams):
    """Text document did save notification."""
    file_uri = params.text_document.uri
    ls.show_message('Text Document Did Save.' + file_uri)
    # text_doc = ls.workspace.get_document(file_uri)
    Relation().reload_pyfile(file_uri)


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



if __name__ == '__main__':
    python_server.start_tcp("127.0.0.1", 16471)
