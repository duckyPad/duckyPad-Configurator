import os
import shutil
import webbrowser
from platformdirs import *
from pathlib import Path
from hid_common import *

from dsvm_common import *
import dsvm_make_bytecode

print("NOTE TO MYSELF: _pull_dsvm.py to download latest VM version")

MAX_PROFILE_NAME_LEN = 16
MAX_EXPANSION_MODULE_COUNT = 4
CHANNELS_PER_EXPANSION_MODULE = 8
MAX_EXPANSION_CHANNEL = MAX_EXPANSION_MODULE_COUNT * CHANNELS_PER_EXPANSION_MODULE

def ensure_dir(dir_path):
    os.makedirs(dir_path, exist_ok=True)

appname = 'duckypad_config'
appauthor = 'dekuNukem'
app_save_path = user_data_dir(appname, appauthor, roaming=True)
backup_path = os.path.join(app_save_path, 'profile_backups')
hid_dump_path = os.path.join(app_save_path, "hid_dump")
temp_dir_path = os.path.join(app_save_path, "temp_dir")

def open_discord_link():
    webbrowser.open("https://discord.gg/4sJCBx5")

def app_update_click(event):
    webbrowser.open('https://github.com/duckyPad/duckyPad-Configurator/releases/latest')

def open_profile_autoswitcher_url():
    webbrowser.open('https://github.com/duckyPad/duckyPad-profile-autoswitcher/blob/master/README.md')

def open_tindie_store():
    webbrowser.open('https://dekunukem.github.io/duckyPad-Pro/doc/store_links.html')

def open_mac_linux_instruction():
    webbrowser.open('https://dekunukem.github.io/duckyPad-Pro/doc/linux_macos_notes.html')

def script_instruction_click(event):
    webbrowser.open('https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html')

def open_dpp_page(event):
    webbrowser.open('https://dekunukem.github.io/duckyPad-Pro/README.html')

def open_duckypad_user_manual_url():
    webbrowser.open('https://dekunukem.github.io/duckyPad-Pro/doc/getting_started.html')

def open_duckypad_troubleshooting_url():
    webbrowser.open('https://dekunukem.github.io/duckyPad-Pro/doc/troubleshooting.html')

def rgb_to_hex(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

def make_list_of_ds_line_obj_from_str_listing(pgm_listing, source_fn=None):
    obj_list = []
    for index, item in enumerate(pgm_listing):
        obj_list.append(ds_line(item, index+1, source_fn=source_fn))
    return obj_list

def make_final_script(ds_key, pgm_listing):
    final_listing = []
    if ds_key.allow_abort:
        final_listing.append("$_ALLOW_ABORT = 1")
    if ds_key.dont_repeat:
        final_listing.append("$_DONT_REPEAT = 1")
    final_listing += pgm_listing
    return final_listing

def last_two_levels(full_path):
    return os.path.join(*full_path.split(os.sep)[-2:])

"""
0 to 19: mechanical switches
20 to 25: rotary encoders
26 to 35: spare gpio pins, unused
36 to 65: expansion channels
"""

BUTTON_RE1_CW = 20
BUTTON_RE1_CCW = 21
BUTTON_RE1_PUSH = 22
BUTTON_RE2_CW = 23
BUTTON_RE2_CCW = 24
BUTTON_RE2_PUSH = 25

EXP_BUTTON_START = 36

def is_rotary_encoder_button(key_index_start_from_0):
    return BUTTON_RE1_CW <= key_index_start_from_0 <= BUTTON_RE2_PUSH

def is_expansion_button(key_index_start_from_0):
    return EXP_BUTTON_START <= key_index_start_from_0 <= EXP_BUTTON_START + MAX_EXPANSION_CHANNEL

KEY_NAME_MAX_CHAR_PER_LINE = 7

SW_MATRIX_NUM_COLS = 4
SW_MATRIX_NUM_ROWS = 5
MECH_OBSW_COUNT = (SW_MATRIX_NUM_COLS * SW_MATRIX_NUM_ROWS)
ROTARY_ENCODER_SW_COUNT = 6
ONBOARD_SPARE_GPIO_COUNT = 10
MAX_PROFILE_COUNT = 64
MAX_KEY_COUNT = (MECH_OBSW_COUNT + ROTARY_ENCODER_SW_COUNT + ONBOARD_SPARE_GPIO_COUNT + MAX_EXPANSION_CHANNEL)

profile_info_dot_txt = "profile_info.txt"
global_header_dot_txt = "global_header.txt"

HID_COMMAND_READ_FILE = 11

HID_COMMAND_OPEN_FILE_FOR_WRITING = 14
HID_COMMAND_WRITE_FILE = 15
HID_COMMAND_CLOSE_FILE = 16
HID_COMMAND_DELETE_FILE = 17
HID_COMMAND_CREATE_DIR = 18
HID_COMMAND_DELETE_DIR = 19
HID_COMMAND_SW_RESET = 20

HID_COMMAND_DUMP_SD = 32
HID_COMMAND_OPEN_FILE_FOR_READING = 33

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64
DUCKYPAD_TO_PC_HID_BUF_SIZE = 64
HID_READ_FILE_PATH_SIZE_MAX = 55

class dp_file_op(object):
    def __str__(self):
        return (f"dp_file_op(\n"
                f"  action={self.action},\n"
                f"  local_dir={self.local_dir},\n"
                f"  source_parent={self.source_parent},\n"
                f"  source_path={self.source_path},\n"
                f"  destination_parent={self.destination_parent},\n"
                f"  destination_path={self.destination_path}\n"
                f")")

    def __init__(self):
        self.mkdir = "mkdir"
        self.rmdir = "rmdir"
        self.copy_file = "cpf"
        self.delete_file = "rmf"
        self.action = None
        self.source_parent = None
        self.source_path = None
        self.destination_parent = None
        self.destination_path = None
        self.local_dir = None
    
    def __eq__(self, other):
        if not isinstance(other, dp_file_op):
            return NotImplemented
        return (
            self.action == other.action and
            self.source_parent == other.source_parent and
            self.source_path == other.source_path and
            self.destination_parent == other.destination_parent and
            self.destination_path == other.destination_path and
            self.local_dir == other.local_dir
        )

    def __hash__(self):
        return hash((
            self.action,
            self.source_parent,
            self.source_path,
            self.destination_parent,
            self.destination_path,
            self.local_dir
        ))

def ui_print(text, tk_root_obj, ui_text_obj):
    if tk_root_obj is None or ui_text_obj is None:
        return
    ui_text_obj.set(str(text))
    tk_root_obj.update()

def delete_path(path):
    path = Path(path)
    try:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.is_file():
            path.unlink()
    except Exception as e:
        print("delete_path:", e)

import zipfile

def zip_directory(source_dir_path, output_zip_path):
    top_level_folder_name = os.path.basename(os.path.normpath(source_dir_path))
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, start=source_dir_path)
                arcname = os.path.join(top_level_folder_name, relative_path)
                zipf.write(file_path, arcname)

import platform
import subprocess
def open_directory_in_file_browser(path):
    system = platform.system()
    if system == 'Windows':
        os.startfile(path)
    elif system == 'Darwin':  # macOS
        subprocess.run(['open', path])
    elif system == 'Linux':
        subprocess.run(['xdg-open', path])

import zipfile

MAX_TOTAL_UNCOMPRESSED_SIZE = 10 * 1024 * 1024  # 50 MB
MAX_FILE_COUNT = 256
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB

def is_safe_path(base_path, target_path):
    # Prevent path traversal
    return os.path.realpath(target_path).startswith(os.path.realpath(base_path))

def reset_directory(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)

def unzip_to_own_directory(zip_file_path, output_dir_path):
    reset_directory(output_dir_path)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        infos = zip_ref.infolist()
        if len(infos) > MAX_FILE_COUNT:
            raise Exception("Too many files in zip archive")

        total_uncompressed_size = sum(info.file_size for info in infos)
        if total_uncompressed_size > MAX_TOTAL_UNCOMPRESSED_SIZE:
            raise Exception("Uncompressed size too large")

        for info in infos:
            if info.file_size > MAX_FILE_SIZE:
                raise Exception(f"File {info.filename} is too large")

            extracted_path = os.path.join(output_dir_path, info.filename)
            if not is_safe_path(output_dir_path, extracted_path):
                raise Exception(f"Unsafe file path detected: {info.filename}")

            zip_ref.extract(info, output_dir_path)

def get_profile_dir(dir_path):
    if not os.path.isdir(dir_path):
        return None
    for entry in os.listdir(dir_path):
        full_path = os.path.join(dir_path, entry)
        if os.path.isdir(full_path) and entry.startswith("profile"):
            return full_path
    return None

