import os
import hid
import time
import shutil
import hid_common
from shared import *

def millis():
    return time.time_ns() // 1000000

SD_WALK_OP_TYPE_INDEX = 1

SD_WALK_OP_ACK = 0
SD_WALK_OP_NEW_DIR = 1
SD_WALK_OP_FILE_CONTENT = 2
SD_WALK_OP_FILE_MD5 = 3
SD_WALK_OP_EOT = 4

def read_binary_file(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

def save_to_file(sd_path, pc_dump_dir_path, file_name, file_content):
    sd_path = sd_path.lstrip("\\/")
    # print("save_to_file:", sd_path, pc_dump_dir_path, file_name, file_content)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_dir_path = os.path.join(script_dir, pc_dump_dir_path, sd_path)
    full_file_path = os.path.join(full_dir_path, file_name)
    os.makedirs(full_dir_path, exist_ok=True)
    with open(full_file_path, 'wb') as file:
        file.write(file_content)

def hid_dump_file(sd_file_path, hid_obj):
    if len(sd_file_path) > HID_READ_FILE_PATH_SIZE_MAX:
        raise OSError("SD file path too long")

    print(f'Reading file: {sd_file_path} ', end='')

    pc_to_duckypad_buf = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
    pc_to_duckypad_buf[0] = 5   # HID Usage ID, always 5
    pc_to_duckypad_buf[1] = 0   # unused
    pc_to_duckypad_buf[2] = HID_COMMAND_OPEN_FILE_FOR_READING # Command type

    for index, value in enumerate(sd_file_path):
        pc_to_duckypad_buf[3+index] = ord(value)

    hid_obj.write(pc_to_duckypad_buf)
    duckypad_to_pc_buf = hid_obj.read(DUCKYPAD_TO_PC_HID_BUF_SIZE)
    if duckypad_to_pc_buf[2] != 0:
        raise OSError("HID open file for read failed")

    all_data = []
    while 1:
        pc_to_duckypad_buf = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
        pc_to_duckypad_buf[0] = 5   # HID Usage ID, always 5
        pc_to_duckypad_buf[1] = 0   # unused
        pc_to_duckypad_buf[2] = HID_COMMAND_READ_FILE
        hid_obj.write(pc_to_duckypad_buf)
        duckypad_to_pc_buf = hid_obj.read(DUCKYPAD_TO_PC_HID_BUF_SIZE)
        chunk_size = duckypad_to_pc_buf[2]
        if chunk_size == 0:
            break
        all_data += duckypad_to_pc_buf[3:3+chunk_size]
        print(len(all_data), " ", end='')

    print()
    return bytes(all_data)

def dump_sd(dp_path, dump_dir_path):
    current_dir = None
    pc_to_duckypad_buf = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
    pc_to_duckypad_buf[0] = 5   # HID Usage ID, always 5
    pc_to_duckypad_buf[1] = 0   # unused
    pc_to_duckypad_buf[2] = HID_COMMAND_DUMP_SD # Command type

    shutil.rmtree(dump_dir_path, ignore_errors=True)
    md5_miss_list = []

    dp20_h = hid.device()
    dp20_h.open_path(dp_path)

    while 1:
        dp20_h.write(pc_to_duckypad_buf)
        duckypad_to_pc_buf = dp20_h.read(DUCKYPAD_TO_PC_HID_BUF_SIZE)

        if len(duckypad_to_pc_buf) != DUCKYPAD_TO_PC_HID_BUF_SIZE:
            dp20_h.close()
            return False

        if duckypad_to_pc_buf[SD_WALK_OP_TYPE_INDEX] == SD_WALK_OP_ACK:
            continue

        elif duckypad_to_pc_buf[SD_WALK_OP_TYPE_INDEX] == SD_WALK_OP_EOT:
            break

        elif duckypad_to_pc_buf[SD_WALK_OP_TYPE_INDEX] == SD_WALK_OP_NEW_DIR:
            rawchar = duckypad_to_pc_buf[2:]
            current_dir = ''.join(chr(c) for c in rawchar[:rawchar.index(0)])
            print(current_dir)

        elif duckypad_to_pc_buf[SD_WALK_OP_TYPE_INDEX] == SD_WALK_OP_FILE_MD5:
            rawchar = duckypad_to_pc_buf[18:]
            this_file_name = ''.join(chr(c) for c in rawchar[:rawchar.index(0)])
            md5_list = duckypad_to_pc_buf[2:18]
            md5_string = ''.join(f'{x:02x}' for x in md5_list)
            print(this_file_name, md5_string)
            md5_miss_list.append((current_dir, this_file_name))

        elif duckypad_to_pc_buf[SD_WALK_OP_TYPE_INDEX] == SD_WALK_OP_FILE_CONTENT:
            file_name_end = duckypad_to_pc_buf[2] + 1
            file_content_end = duckypad_to_pc_buf[3] + 1
            raw_filename_list = duckypad_to_pc_buf[4:file_name_end]
            this_file_name = ''.join(chr(c) for c in raw_filename_list[:raw_filename_list.index(0)])
            print(this_file_name)
            raw_file_content_bytes = bytes(duckypad_to_pc_buf[file_name_end:file_content_end])
            save_to_file(current_dir, dump_dir_path, this_file_name, raw_file_content_bytes)

    md5_miss_list.append(('', 'profile_info.txt'))
    for item in md5_miss_list:
        sd_dir = item[0]
        sd_file_name = item[1]
        print("MD5 MISS:", sd_dir, sd_file_name)
        raw_bytes = hid_dump_file(f'{sd_dir}/{sd_file_name}', dp20_h)
        save_to_file(sd_dir, dump_dir_path, sd_file_name, raw_bytes)

    dp20_h.close()
    return True

this_dp_hid_path = hid_common.get_duckypad_path()

if len(this_dp_hid_path) == 0:
    print("duckypad not found")
    exit()

# this_dp_hid_path = this_dp_hid_path[0]

print(this_dp_hid_path)

dump_sd(this_dp_hid_path[0], "wtf")