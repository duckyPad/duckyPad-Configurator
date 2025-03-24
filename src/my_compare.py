import os
import sys
import hashlib
import shutil
from pathlib import Path
from shared import *

tk_root = None
tk_strvar = None

duckypad_file_whitelist = [
	"profile",
	"dpp_config",
	"dpkm_",
	"config",
	"key",
    "profile_info"
]

duckypad_file_blacklist = [
	"keymaps",
]

def is_duckypad_file(name):
	for item in duckypad_file_blacklist:
		if item.lower().strip() in name.lower().strip():
			return False
	for item in duckypad_file_whitelist:
		if item.lower().strip() in name.lower().strip():
			return True
	return False

def is_file_different(file1, file2):
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        hash1 = hashlib.md5(f1.read()).hexdigest()
        hash2 = hashlib.md5(f2.read()).hexdigest()
    return hash1 != hash2

def compare_dir(old_path, new_path):
    old_items = set(os.listdir(old_path))
    new_items = set(os.listdir(new_path))

    # items in new but not old
    items_to_add = new_items - old_items
    # items in old but not new
    items_to_delete = old_items - new_items

    files_to_add = set([x for x in items_to_add if os.path.isdir(os.path.join(new_path, x)) is False])
    dirs_to_add = set([x for x in items_to_add if os.path.isdir(os.path.join(new_path, x))])

    files_to_delete = set([x for x in items_to_delete if os.path.isdir(os.path.join(old_path, x)) is False])
    dirs_to_delete = set([x for x in items_to_delete if os.path.isdir(os.path.join(old_path, x))])
    items_in_both = new_items.intersection(old_items)
    dir_in_both_not_checked = set()

    for item in items_in_both:
        new_full_path = os.path.join(new_path, item)
        old_full_path = os.path.join(old_path, item)

        if os.path.isdir(new_full_path) or os.path.isdir(old_full_path):
            dir_in_both_not_checked.add(item)
            continue
        if is_file_different(old_full_path, new_full_path):
            files_to_delete.add(item)
            files_to_add.add(item)
    
    result_dict = {}
    result_dict["files_to_add"] = files_to_add
    result_dict["files_to_delete"] = files_to_delete
    result_dict["dirs_to_add"] = dirs_to_add
    result_dict["dirs_to_delete"] = dirs_to_delete
    result_dict["dir_in_both_not_checked"] = dir_in_both_not_checked
    print(result_dict)

    
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

def duckypad_find_difference(sd_dir, modified_dir):
    # top level dirs
    top_level_item_to_add, top_level_item_to_delete, top_level_item_with_difference, common_items = compare_dir(sd_dir, modified_dir)
    print("top_level_item_to_add:", top_level_item_to_add)
    print("top_level_item_to_delete:", top_level_item_to_delete)
    print("top_level_item_with_difference:", top_level_item_with_difference)
    print("common_items:", common_items)

    exit()
    # common_items has BOTH FILES AND DIR
    top_level_to_copy = top_level_item_to_add | top_level_item_with_difference
    top_level_to_remove = top_level_item_to_delete | top_level_to_copy
    print('----------------')
    print("top_level_to_copy", top_level_to_copy)
    print("top_level_to_remove", top_level_to_remove)

    for item in top_level_to_copy:
        to_copy_source_path = os.path.join(modified_dir, item)
        to_copy_destination_path = os.path.join(sd_dir, item)
        print("to_copy_source_path:", to_copy_source_path)
        print("to_copy_destination_path:", to_copy_destination_path)
        if os.path.isfile(to_copy_source_path):
            continue

         

sd_path = "./sd_files"
modified_path = "./new_files"
# duckypad_find_difference(sd_path, modified_path)
compare_dir(sd_path, modified_path)