import os
import hid
import time
import sys
import psutil
import my_compare
from shared import *
from pathlib import Path

if 'win32' in sys.platform:
    import win32api

dp20_pid = 0xd11c
dpp_pid = 0xd11d
all_dp_pids = [dp20_pid, dpp_pid]

def is_duckypad_pid(this_pid):
    return this_pid in all_dp_pids

def get_duckypad_path():
    dp_path_list = set()
    if 'win32' in sys.platform:
        for device_dict in hid.enumerate():
            if device_dict['vendor_id'] == 0x0483 and \
            is_duckypad_pid(device_dict['product_id']) and \
            device_dict['usage'] == 58:
                dp_path_list.add(device_dict['path'])
    else:
        for device_dict in hid.enumerate():
            if device_dict['vendor_id'] == 0x0483 and \
            is_duckypad_pid(device_dict['product_id']):
                dp_path_list.add(device_dict['path'])
    return list(dp_path_list)

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64
DUCKYPAD_TO_PC_HID_BUF_SIZE = 64

HID_RESPONSE_OK = 0
HID_RESPONSE_ERROR = 1
HID_RESPONSE_BUSY = 2
HID_RESPONSE_EOF = 3

def duckypad_hid_sw_reset(dp_info_dict, reboot_into_usb_msc_mode=False):
    pc_to_duckypad_buf = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
    pc_to_duckypad_buf[0] = 5   # HID Usage ID, always 5
    pc_to_duckypad_buf[2] = HID_COMMAND_SW_RESET    # Command type
    if(reboot_into_usb_msc_mode):
        pc_to_duckypad_buf[3] = 1
    myh = hid.device()
    myh.open_path(dp_info_dict['hid_path'])
    myh.write(pc_to_duckypad_buf)
    myh.close()

def get_duckypad_drive_windows(vol_str):
    removable_drives = [x for x in psutil.disk_partitions() if ('removable' in x.opts.lower() and 'fat' in x.fstype.lower())]
    if len(removable_drives) == 0:
        return None
    for item in removable_drives:
        print("removable drives:", item)
    for item in removable_drives:
        vol_label = win32api.GetVolumeInformation(item.mountpoint)[0]
        if vol_str.strip().lower() in vol_label.strip().lower():
            return item.mountpoint
    return None

def get_duckypad_drive_mac(vol_str):
    vol_list = [x for x in psutil.disk_partitions() if vol_str.strip().lower() in x.mountpoint.strip().lower()]
    if len(vol_list) == 0:
        return None
    return vol_list[0].mountpoint

def get_duckypad_drive_linux(vol_str):
    return get_duckypad_drive_mac(vol_str)

def get_duckypad_drive(vol_str):
    if 'win32' in sys.platform:
        return get_duckypad_drive_windows(vol_str)
    elif 'darwin' in sys.platform:
        return get_duckypad_drive_mac(vol_str)
    elif 'linux' in sys.platform:
        return get_duckypad_drive_linux(vol_str)
    return None

def eject_drive(vol_str):
    print("ejecting...")
    if 'darwin' in sys.platform:
        os.system(f"diskutil unmountDisk force {vol_str}")
    elif 'linux' in sys.platform:
        os.system(f"umount -l {vol_str}")
    else:
        time.sleep(1) # well, good enough for windows

def make_dp_info_dict(hid_msg, hid_path):
    this_dict = {}
    this_dict['fw_version'] = f"{hid_msg[3]}.{hid_msg[4]}.{hid_msg[5]}"
    this_dict['dp_model'] = hid_msg[6]
    serial_number_uint32_t = int.from_bytes(hid_msg[7:11], byteorder='big')
    this_dict['serial'] = f'{serial_number_uint32_t:08X}'.upper()
    this_dict['hid_path'] = hid_path
    this_dict['hid_msg'] = hid_msg
    return this_dict

def get_all_dp_info(dp_path_list):
    dp_info_list = []
    pc_to_duckypad_buf = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
    pc_to_duckypad_buf[0] = 5   # HID Usage ID, always 5
    for this_path in dp_path_list:
        print(this_path)
        myh = hid.device()
        myh.open_path(this_path)
        myh.write(pc_to_duckypad_buf)
        result = myh.read(DUCKYPAD_TO_PC_HID_BUF_SIZE)
        myh.close()
        print(result)
        if result[2] != HID_RESPONSE_OK:
            continue
        this_dict = make_dp_info_dict(result, this_path)
        dp_info_list.append(this_dict)
    return dp_info_list

def scan_duckypads():
    all_dp_paths = get_duckypad_path()
    if len(all_dp_paths) == 0:
        return []
    try:
        dp_info_list = get_all_dp_info(all_dp_paths)
    except Exception:
        return None
    return dp_info_list

def make_file_path_for_hid(pc_path):
    path_parts = Path(pc_path).parts
    result = '/'
    for item in path_parts[1:]:
        result += f"{item}/"
    return result[:-1]

def make_fileop_hid_packet(this_op):
    print(this_op)
    pc_to_duckypad_buf = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
    pc_to_duckypad_buf[0] = 5   # HID Usage ID

    if this_op.type == this_op.delete_file:
        pc_to_duckypad_buf[2] = HID_COMMAND_DELETE_FILE
        file_path = make_file_path_for_hid(this_op.source_path)
        print(file_path)
        if len(file_path) > HID_READ_FILE_PATH_SIZE_MAX:
            raise OSError("file path too long")
        for index, value in enumerate(file_path):
            pc_to_duckypad_buf[3+index] = ord(value)

        print(pc_to_duckypad_buf)
        exit()

    print('-------------')

    return pc_to_duckypad_buf

def duckypad_file_sync_hid(hid_path, orig_path, modified_path):
    print(hid_path, orig_path, modified_path)

    sync_ops = my_compare.get_file_sync_ops(sd_path, modified_path)
    if len(sync_ops) == 0:
        return 0

    # myh = hid.device()
    # myh.open_path(hid_path)

    for item in sync_ops:
        to_send = make_fileop_hid_packet(item)

        
    # myh.close()

sd_path = "./dump"
modified_path = "./to_write_back"

dp_list = scan_duckypads()
if dp_list is None or len(dp_list) == 0:
    exit()

dp_path = dp_list[0]['hid_path']
duckypad_file_sync_hid(dp_path, sd_path, modified_path)