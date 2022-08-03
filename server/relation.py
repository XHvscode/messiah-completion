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


class Relation(utils.Singleton):
    def init(self):
        self.ws_path = ""
        self.root_child_info = {}
        self.comp_2_root = {}
        self.relation_info = {}

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
        json_file = os.path.join(self.ws_path, ".vscode", "g83_jump_config.json")
        if not os.path.exists(json_file):
            logging.error("can not find json file:: %s" % json_file)
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
        relat_path = full_path.replace(self.ws_path, "", 1).lstrip("/").lstrip("\\")
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

        relat_path = full_path.replace(self.ws_path, "", 1).lstrip("/").lstrip("\\")

        file_prop = self.root_child_info.get(relat_path, {})

        set_del_cls = set(file_prop.keys()) - set(all_prop_dict.keys())
        for del_cls in set_del_cls:
            file_prop.pop(del_cls, None)

        for clsname, cls_prop_dict in all_prop_dict.items():
            file_prop[clsname] = {
                "cls_prop": cls_prop_dict,
            }
