import os
import sys
import hashlib
import shutil
from pathlib import Path
from shared import *

tk_root = None
tk_strvar = None

duckypad_file_whitelist = [
    "profile_",
    "dpkm_",
    "config.txt",
    "key",
    profile_info_dot_txt
]

duckypad_file_blacklist = [
    "keymaps",
]

def is_duckypad_file(name):
    for item in duckypad_file_blacklist:
        if item.lower().strip() in name.lower().strip():
            return False
    for item in duckypad_file_whitelist:
        if name.lower().strip().startswith(item.lower().strip()):
            return True
    return False

def is_file_different(file1, file2):
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        hash1 = hashlib.md5(f1.read()).hexdigest()
        hash2 = hashlib.md5(f2.read()).hexdigest()
    return hash1 != hash2

def compare_dir(orig_path, new_path):
    old_items = set(os.listdir(orig_path))
    new_items = set(os.listdir(new_path))

    # items in new but not old
    items_to_add = new_items - old_items
    # items in old but not new
    items_to_delete = old_items - new_items

    files_to_add = set([x for x in items_to_add if os.path.isdir(os.path.join(new_path, x)) is False])
    dirs_to_create = set([x for x in items_to_add if os.path.isdir(os.path.join(new_path, x))])

    files_to_delete = set([x for x in items_to_delete if os.path.isdir(os.path.join(orig_path, x)) is False])
    dirs_to_delete = set([x for x in items_to_delete if os.path.isdir(os.path.join(orig_path, x))])
    items_in_both = new_items.intersection(old_items)
    dir_in_both_not_checked = set()

    for item in items_in_both:
        new_full_path = os.path.join(new_path, item)
        old_full_path = os.path.join(orig_path, item)

        if os.path.isdir(new_full_path) or os.path.isdir(old_full_path):
            dir_in_both_not_checked.add(item)
            continue
        if is_file_different(old_full_path, new_full_path):
            files_to_delete.add(item)
            files_to_add.add(item)
    
    result_dict = {}
    result_dict['orig_path'] = orig_path
    result_dict['new_path'] = new_path
    result_dict["files_to_add"] = [x for x in files_to_add if is_duckypad_file(x)]
    result_dict["files_to_delete"] = [x for x in files_to_delete if is_duckypad_file(x)]
    result_dict["dirs_to_create"] = [x for x in dirs_to_create if is_duckypad_file(x)]
    result_dict["dirs_to_delete"] = [x for x in dirs_to_delete if is_duckypad_file(x)]
    result_dict["dir_in_both_not_checked"] = [x for x in dir_in_both_not_checked if is_duckypad_file(x)]
    return result_dict

"""
Files in new but not old: add to duckypad
Files in old but not new: delete from duckypad
Files in both but different content: delete from duckypad then write new version
"""

def delete_path(path):
    if os.path.exists(path) is False:
        return
    # if 'dpp_config.txt' in path:
    #     return
    # if profile_info_dot_txt in path:
    #     return
    
    this_msg = f"deleting {path}"
    print(this_msg)
    this_msg = f"deleting {last_two_levels(path)}"
    tk_strvar.set(this_msg)
    tk_root.update()

    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)

def get_file_content(file_path):
    this_file = open(file_path, 'rb')
    content = this_file.read()
    this_file.close()
    return content

def copy_file_if_exist(from_path, to_path):
    if os.path.exists(from_path):
        shutil.copy2(from_path, to_path)

class dp_file_op(object):
    def __str__(self):
        return (f"dp_file_op("
                f"type={self.type}, "
                f"source_root={self.source_root}, "
                f"source_path={self.source_path}, "
                f"destination_root={self.destination_root}, "
                f"destination_path={self.destination_path})")
    
    def __init__(self):
        self.mkdir = "mkdir"
        self.rmdir = "rmdir"
        self.copy_file = "copy_file"
        self.delete_file = "delete_file"
        self.type = None
        self.source_root = None
        self.source_path = None
        self.destination_root = None
        self.destination_path = None
        
def make_file_op(diff_dict):
    op_list = []
    for item in diff_dict["files_to_delete"]:
        this_op = dp_file_op()
        this_op.type = this_op.delete_file
        this_op.source_root = diff_dict['orig_path']
        this_op.source_path = item
        op_list.append(this_op)
    
    for item in diff_dict["files_to_add"]:
        this_op = dp_file_op()
        this_op.type = this_op.copy_file
        this_op.source_root = diff_dict['new_path']
        this_op.source_path = item
        this_op.destination_root = diff_dict['orig_path']
        this_op.destination_path = item
        op_list.append(this_op)

    for item in diff_dict["dirs_to_delete"]:
        this_op = dp_file_op()
        this_op.type = this_op.rmdir
        this_op.source_root = diff_dict['orig_path']
        this_op.source_path = item
        op_list.append(this_op)

    for item in diff_dict["dirs_to_create"]:
        this_op = dp_file_op()
        this_op.type = this_op.mkdir
        this_op.source_root = diff_dict['orig_path']
        this_op.source_path = item
        op_list.append(this_op)
    
    for item in op_list:
        print(item)

def duckypad_find_difference(original_dir_root, modified_dir_root):
    result_dict_top_lvl = compare_dir(original_dir_root, modified_dir_root)
    for key in result_dict_top_lvl:
        print(key, result_dict_top_lvl[key])
    make_file_op(result_dict_top_lvl)
    # for item in result_dict_top_lvl["dir_in_both_not_checked"]:
    #     subdir_orig_path = os.path.join(original_dir_root, item)
    #     subdir_modified_path = os.path.join(modified_dir_root, item)
    #     subdir_diff_dict = compare_dir(subdir_orig_path, subdir_modified_path)
    #     for key in subdir_diff_dict:
    #         print(key, subdir_diff_dict[key])

sd_path = "./sd_files"
modified_path = "./new_files"
duckypad_find_difference(sd_path, modified_path)
