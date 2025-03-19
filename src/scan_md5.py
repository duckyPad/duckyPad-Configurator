import os
import time
import hashlib
from platformdirs import *

def get_md5_str(filepath):
    with open(filepath, "rb") as f:
        return hashlib.file_digest(f, "md5").hexdigest()

def list_all_files(directory):
    all_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)
    return all_files

def get_md5_dict(backup_dir_path):
    os.makedirs(backup_dir_path, exist_ok=1)
    all_backup_dirs = [name for name in os.listdir(backup_dir_path) if os.path.isdir(os.path.join(backup_dir_path, name))]
    duckypad_backup_dirs = sorted([x for x in all_backup_dirs if "duckyPad_backup" in x], reverse=1)[:5]
    duckypad_pro_backup_dirs = sorted([x for x in all_backup_dirs if "duckyPad_Pro_backup" in x], reverse=1)[:5]
    dir_to_search = duckypad_backup_dirs + duckypad_pro_backup_dirs
    md5_dict = {}
    for item in dir_to_search:
        fullpath = os.path.join(backup_dir_path, item)
        all_files = list_all_files(fullpath)
        for this_file in all_files:
            md5_dict[get_md5_str(this_file)] = this_file
    return md5_dict

