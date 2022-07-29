# -*- coding:utf-8 -*-
# Author: xiaohao@corp.netease.com

import os
import json
import utils

from define import *

class Relation(utils.Singleton):
    def init(self):
        self.ws_path = ""
        self.root_child_info = {}
        self.comp_2_root = {}

    def load_json_config(self, ls):
        if self.root_child_info:
            return True
        ws_rootpath = ls.workspace.root_path
        self.ws_path = os.path.normpath(ws_rootpath)
        json_file = os.path.join(self.ws_path, ".vscode", "g83_jump_config.json")
        if not os.path.exists(json_file):
            print("can not find json file:", json_file)
            return False
        relation_info = {}
        with open(json_file, "r") as fp:
            relation_info = json.load(fp)

        for component_name_and_path, child_class_list in relation_info.items():
            component_name_and_path = os.path.normpath(component_name_and_path)
            rootpath, clsname = component_name_and_path.split("&")
            fullpath = os.path.join(self.ws_path, rootpath)
            class_prop_dict = utils.get_file_class_property(fullpath, clsname)
            if not class_prop_dict:
                continue
            root_prop_dict: dict = self.root_child_info.setdefault(component_name_and_path, {})
            root_prop_dict[component_name_and_path] = class_prop_dict
            # todo check 同名函数

            for child_name_and_path in child_class_list:
                child_name_and_path = os.path.normpath(child_name_and_path)
                childpath, child_cls_name = child_name_and_path.split("&")
                childfullpath = os.path.join(self.ws_path, childpath)
                child_pro_dict = utils.get_file_class_property(childfullpath, child_cls_name)
                root_prop_dict[child_name_and_path] = child_pro_dict
                self.comp_2_root[child_name_and_path] = component_name_and_path

        print('---load_json_config end------')
        return True

    def get_definition_list(self, full_path, class_name, def_name):
        full_path:str = os.path.normpath(full_path)
        relat_path = full_path.replace(self.ws_path, "", 1).lstrip("/").lstrip("\\")
        relat_path_name = relat_path + "&" + class_name
        root_path_name = self.comp_2_root.get(relat_path_name, relat_path_name)
        root_child_info = self.root_child_info.get(root_path_name, {})
        location_lst = []
        for component_name_and_path, class_prop_dict in root_child_info.items():
            if def_name not in class_prop_dict:
                continue
            comp_pro = class_prop_dict[def_name]
            location = Location(
                uri = from_fs_path(comp_pro.path),
                range = Range(
                    start = Position(line=comp_pro.position[0], character=comp_pro.position[1]),
                    end = Position(line=comp_pro.position[0], character=comp_pro.position[2])
                )
            )
            location_lst.append(location)
        if len(location_lst) == 1:
            return location_lst[0]
        return location_lst
