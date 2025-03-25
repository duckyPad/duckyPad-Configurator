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

def delete_path(path):
    path = Path(path)
    try:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()
    except Exception as e:
        print("delete_path:", e)
    
class dp_file_op(object):
    def __str__(self):
        return (f"file_op("
                f"type={self.type}, "
                f"src_path={self.source_path}, "
                f"dest_path={self.destination_path})")
    
    def __init__(self):
        self.mkdir = "mkdir"
        self.rmdir = "rmdir"
        self.copy_file = "cpf"
        self.delete_file = "rmf"
        self.type = None
        self.source_path = None
        self.destination_path = None
        
def make_file_op(diff_dict):
    op_list = []
    for item in diff_dict["files_to_delete"]:
        this_op = dp_file_op()
        this_op.type = this_op.delete_file
        this_op.source_path = os.path.join(diff_dict['orig_path'], item)
        op_list.append(this_op)
    
    for item in diff_dict["files_to_add"]:
        this_op = dp_file_op()
        this_op.type = this_op.copy_file
        this_op.source_path = os.path.join(diff_dict['new_path'], item)
        this_op.destination_path = os.path.join(diff_dict['orig_path'], item)
        op_list.append(this_op)

    for item in diff_dict["dirs_to_delete"]:
        this_op = dp_file_op()
        this_op.type = this_op.rmdir
        this_op.source_path = os.path.join(diff_dict['orig_path'], item)
        op_list.append(this_op)

    for item in diff_dict["dirs_to_create"]:
        this_op = dp_file_op()
        this_op.type = this_op.mkdir
        this_op.source_path = os.path.join(diff_dict['orig_path'], item)
        op_list.append(this_op)
    
    return op_list

def get_file_sync_ops(original_dir_root, modified_dir_root):
    file_ops_all = []
    result_dict_top_lvl = compare_dir(original_dir_root, modified_dir_root)
    # for key in result_dict_top_lvl:
    #     print(key, result_dict_top_lvl[key])
    file_ops_all += make_file_op(result_dict_top_lvl)

    for this_dir in result_dict_top_lvl["dirs_to_create"]:
        subdir_modified_path = os.path.join(modified_dir_root, this_dir)
        for this_file in os.listdir(subdir_modified_path):
            this_op = dp_file_op()
            this_op.type = this_op.copy_file
            this_op.source_path = os.path.join(result_dict_top_lvl['new_path'], this_dir, this_file)
            this_op.destination_path = os.path.join(result_dict_top_lvl['orig_path'], this_dir, this_file)
            file_ops_all.append(this_op)

    for this_dir in result_dict_top_lvl["dir_in_both_not_checked"]:
        subdir_orig_path = os.path.join(original_dir_root, this_dir)
        subdir_modified_path = os.path.join(modified_dir_root, this_dir)
        subdir_diff_dict = compare_dir(subdir_orig_path, subdir_modified_path)
        subdir_diff_dict["dirs_to_add"] = []
        subdir_diff_dict["dirs_to_delete"] = []
        subdir_diff_dict["dir_in_both_not_checked"] = []

        # for key in subdir_diff_dict:
        #     print(key, subdir_diff_dict[key])
        
        file_ops_all += make_file_op(subdir_diff_dict)
    
    return file_ops_all

def execute_sync_ops_msc(op_list):
    for item in sync_ops:
        if item.type == item.mkdir:
            print("mkdir", item.source_path)
            this_path = Path(item.source_path)
            this_path.mkdir(parents=True, exist_ok=True)
        elif item.type == item.rmdir:
            print("rmdir", item.source_path)
            delete_path(item.source_path)
        elif item.type == item.delete_file:
            print("delete file", item.source_path)
            delete_path(item.source_path)
        elif item.type == item.copy_file:
            print("copy file", item.source_path, item.destination_path)
            src = Path(item.source_path)
            dst = Path(item.destination_path)
            shutil.copy(src, dst)

# sd_path = "./sd_files"
# modified_path = "./new_files"
# sync_ops = get_file_sync_ops(sd_path, modified_path)

# execute_sync_ops_msc(sync_ops)