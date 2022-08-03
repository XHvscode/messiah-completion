# -*- coding:utf-8 -*-
# Date: 2022-07-29 11:33:49
# Author: xiaohao@corp.netease.com
"""

"""

import os
import json
import utils
import logging

from define import *
from utils import PropertyType


class Relation(utils.Singleton):
    def init(self):
        self.ws_path = ""
        self.root_child_info = {}
        self.comp_2_root = {}
        self.relation_info = {}

    def get_relate_path(self, full_path):
        return full_path.replace(self.ws_path, "", 1).lstrip("/").lstrip("\\")

    def load_module_cls(self, module_file, cls_name):
        module_prop_dict = self.root_child_info.setdefault(module_file, {})
        if cls_name in module_prop_dict:
            return
        fullpath = os.path.join(self.ws_path, module_file)
        class_property = utils.get_file_class_property(fullpath, cls_name)
        logging.info("load: %s %s" % (fullpath, cls_name))
        module_prop_dict[cls_name] = {
            "cls_prop": class_property
        }

    def load_json_config(self, ls):
        if self.root_child_info:
            return True

        ws_rootpath = ls.workspace.root_path
        self.ws_path = os.path.normpath(ws_rootpath)
        json_file = os.path.join(self.ws_path, ".vscode", "class_relation.json")
        if not os.path.exists(json_file):
            logging.error("can not find config file:: %s" % json_file)
            return False

        with open(json_file, "r") as fp:
            self.relation_info = json.load(fp)

        for module_file, module_info in self.relation_info.items():
            module_file = os.path.normpath(module_file)
            for cls_name, cls_info in module_info.items():
                self.load_module_cls(module_file, cls_name)
                for tcomp in cls_info.get("comps", []):
                    comp_file, comp_cls_name = tcomp
                    comp_file = os.path.normpath(comp_file)
                    self.load_module_cls(comp_file, comp_cls_name)
                    self.comp_2_root[(comp_file, comp_cls_name)] = (module_file, cls_name)

        logging.info("---load_json_config end------")
        return True

    def find_location_def(self, cur_info):
        relat_path, class_name = cur_info
        cls_prop = self.root_child_info.get(relat_path, {}).get(class_name, {}).get("cls_prop")
        if not cls_prop:
            return
        if self.def_name in cls_prop:
            comp_pro = cls_prop[self.def_name]
            location = Location(
                uri=from_fs_path(comp_pro.path),
                range=Range(
                    start=Position(line=comp_pro.position[0], character=comp_pro.position[1]),
                    end=Position(line=comp_pro.position[0], character=comp_pro.position[2])
                )
            )
            self.location_lst.append(location)

    def dfs_find_definition(self, cur_info):
        if cur_info in self.dfs_info_visit:
            return
        self.dfs_info_visit[cur_info] = 1
        relat_path, class_name = cur_info
        cls_info = self.relation_info.get(relat_path.replace("\\", "/"), {}).get(class_name, {})
        if not cls_info:
            return
        self.find_location_def(cur_info)
        for key in ("bases", "comps"):
            for tmp_info in cls_info.get(key, []):
                relat_path, class_name = tmp_info
                relat_path = os.path.normpath(relat_path)
                tt = (relat_path, class_name)
                self.find_location_def(tt)
                self.dfs_find_definition(tt)

    def get_definition_list(self, full_path, class_name, def_name):
        full_path: str = os.path.normpath(full_path)
        relat_path = self.get_relate_path(full_path)
        relat_info = (relat_path, class_name)
        root_info = self.comp_2_root.get(relat_info, relat_info)

        self.dfs_info_visit = {}
        self.location_lst = []
        self.def_name = def_name

        self.dfs_find_definition(root_info)

        if len(self.location_lst) == 1:
            return self.location_lst[0]
        return self.location_lst

    def reload_pyfile(self, full_url):
        full_path = to_fs_path(full_url)
        all_prop_dict = utils.get_file_class_property(full_path)
        if not all_prop_dict:
            return

        relat_path = self.get_relate_path(full_path)

        file_prop = self.root_child_info.get(relat_path, {})

        set_del_cls = set(file_prop.keys()) - set(all_prop_dict.keys())
        for del_cls in set_del_cls:
            file_prop.pop(del_cls, None)

        for clsname, cls_prop_dict in all_prop_dict.items():
            file_prop[clsname] = {
                "cls_prop": cls_prop_dict,
            }

    def get_completions_list(self, ls, params):
        file_uri = params.text_document.uri
        text_doc = ls.workspace.get_document(file_uri)
        class_name = utils.get_class_name_by_pos(text_doc, params.position)
        if not class_name:
            return None
        full_path = to_fs_path(file_uri)
        full_path: str = os.path.normpath(full_path)
        relat_path = self.get_relate_path(full_path)
        relat_info = (relat_path, class_name)
        root_info = self.comp_2_root.get(relat_info, relat_info)

        self.dfs_completions_visit = {}
        self.completions_list = []

        def find_location_completions(cur_info):
            relat_path, class_name = cur_info
            cls_prop:dict = self.root_child_info.get(relat_path, {}).get(class_name, {}).get("cls_prop")
            if not cls_prop:
                return
            filename = os.path.basename(relat_path)
            base_detail = "文件名:%s\n类名:%s\n" % (filename, class_name)
            for def_name, comp_pro in cls_prop.items():
                if comp_pro.prop_type == PropertyType.PROPERTY:
                    ikind = CompletionItemKind.Variable
                    sdetail = base_detail + "类型: Messiah Property"
                elif comp_pro.prop_type == PropertyType.FUNCTION:
                    ikind = CompletionItemKind.Method
                    sdetail = base_detail + " -> " + "类型: 函数"
                elif comp_pro.prop_type == PropertyType.FUNCTION:
                    ikind = CompletionItemKind.Variable
                    sdetail = base_detail + " -> " + "类型: 变量"
                else:
                    logging.error("no define prop type class_name:%s def_name:%s prop_type:%s" % (class_name, def_name, comp_pro.prop_type))
                    continue
                item = CompletionItem(label=def_name, kind=ikind, detail=sdetail)
                self.completions_list.append(item)

        def dfs_find_completions(cur_info):
            if cur_info in self.dfs_completions_visit:
                return
            self.dfs_completions_visit[cur_info] = 1
            relat_path, class_name = cur_info
            cls_info = self.relation_info.get(relat_path.replace("\\", "/"), {}).get(class_name, {})
            if not cls_info:
                return
            find_location_completions(cur_info)
            for key in ("bases", "comps"):
                for tmp_info in cls_info.get(key, []):
                    relat_path, class_name = tmp_info
                    relat_path = os.path.normpath(relat_path)
                    tt = (relat_path, class_name)
                    find_location_completions(tt)
                    dfs_find_completions(tt)
        
        dfs_find_completions(root_info)
        return CompletionList(is_incomplete=False, items=self.completions_list)
