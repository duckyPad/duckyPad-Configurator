import os
import hid
import time
import sys
import psutil
import my_compare
from shared import *
from pathlib import Path
from hid_common import *

if 'win32' in sys.platform:
    import win32api

def duckypad_hid_sw_reset(dp_dict, reboot_into_usb_msc_mode=False):
    print("duckypad_hid_sw_reset", dp_dict)
    dp_list = scan_duckypads() # scan again because HID path might have changed
    if dp_list is None or len(dp_list) == 0:
        return
    dp_to_reset_hid_path = []
    for this_dp in dp_list:
        if this_dp["serial"] == dp_dict["serial"]:
            dp_to_reset_hid_path.append(this_dp["hid_path"])
    if len(dp_to_reset_hid_path) == 0:
        return
    print(dp_to_reset_hid_path)
    pc_to_duckypad_buf = get_empty_pc_to_duckypad_buf()
    pc_to_duckypad_buf[2] = HID_COMMAND_SW_RESET    # Command type
    if(reboot_into_usb_msc_mode):
        pc_to_duckypad_buf[3] = 1
    myh = hid.device()
    myh.open_path(dp_to_reset_hid_path[0])
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

def make_hid_file_path(file_op):
    result = os.path.join(file_op.local_dir, file_op.source_path)
    result = result.lstrip('\\/')
    result = '/' + result
    if len(result) > HID_READ_FILE_PATH_SIZE_MAX:
        raise OSError(f"HID file path too long: {result}")
    return result

def write_str_into_buf(text, buf):
    for index, value in enumerate(text):
        buf[3+index] = ord(value)

def write_bytes_into_buf(bin_buf, buf):
    for index, value in enumerate(bin_buf):
        buf[3+index] = value

def split_file_to_chunks(path, chunk_size=60):
    path = Path(path)
    with path.open('rb') as f:
        data = f.read()
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    return chunks

def hid_write_file(file_op, hid_obj):
    pc_to_duckypad_buf = get_empty_pc_to_duckypad_buf()
    pc_to_duckypad_buf[2] = HID_COMMAND_OPEN_FILE_FOR_WRITING
    file_path = make_hid_file_path(file_op)
    write_str_into_buf(file_path, pc_to_duckypad_buf)
    hid_txrx(pc_to_duckypad_buf, hid_obj)

    file_chunks = split_file_to_chunks(os.path.join(file_op.source_parent, file_op.source_path))

    for this_chunk in file_chunks:
        # print(len(this_chunk), this_chunk)
        this_chunk_buf = get_empty_pc_to_duckypad_buf()
        this_chunk_buf[1] = len(this_chunk)
        this_chunk_buf[2] = HID_COMMAND_WRITE_FILE
        write_bytes_into_buf(this_chunk, this_chunk_buf)
        # print(this_chunk_buf)
        hid_txrx(this_chunk_buf, hid_obj)

    pc_to_duckypad_buf = get_empty_pc_to_duckypad_buf()
    pc_to_duckypad_buf[2] = HID_COMMAND_CLOSE_FILE
    hid_txrx(pc_to_duckypad_buf, hid_obj)

def do_hid_fileop(this_op, hid_obj):
    pc_to_duckypad_buf = get_empty_pc_to_duckypad_buf()

    if this_op.action == this_op.delete_file:
        pc_to_duckypad_buf[2] = HID_COMMAND_DELETE_FILE
        file_path = make_hid_file_path(this_op)
        write_str_into_buf(file_path, pc_to_duckypad_buf)
        hid_txrx(pc_to_duckypad_buf, hid_obj)
    elif this_op.action == this_op.copy_file:
        hid_write_file(this_op, hid_obj)
    elif this_op.action == this_op.rmdir:
        pc_to_duckypad_buf[2] = HID_COMMAND_DELETE_DIR
        file_path = make_hid_file_path(this_op)
        write_str_into_buf(file_path, pc_to_duckypad_buf)
        hid_txrx(pc_to_duckypad_buf, hid_obj)
    elif this_op.action == this_op.mkdir:
        pc_to_duckypad_buf[2] = HID_COMMAND_CREATE_DIR
        file_path = make_hid_file_path(this_op)
        write_str_into_buf(file_path, pc_to_duckypad_buf)
        hid_txrx(pc_to_duckypad_buf, hid_obj)
    return pc_to_duckypad_buf

def duckypad_file_sync_hid(hid_path, orig_path, modified_path, tk_root=None, ui_text_obj=None):
    sync_ops = my_compare.get_file_sync_ops(orig_path, modified_path)
    if len(sync_ops) == 0:
        return 0

    myh = hid.device()
    myh.open_path(hid_path)

    for item in sync_ops:
        print(item)
        ui_print(f"Saving: {item.source_path}", tk_root, ui_text_obj)
        do_hid_fileop(item, myh)

    myh.close()

# sd_path = "./dump"
# modified_path = "./to_write_back"

# dp_list = scan_duckypads()
# if dp_list is None or len(dp_list) == 0:
#     print("no duckypad found")
#     exit()

# dp_path = dp_list[0]['hid_path']
# duckypad_file_sync_hid(dp_path, sd_path, modified_path)


# print(make_hid_file_path("/Users/allen/AppData/Roaming/dekuNukem/duckypad_config/hid_dump/profile_info.txt"))
