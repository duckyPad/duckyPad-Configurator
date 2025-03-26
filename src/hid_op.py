import os
import hid
import time
import sys
import psutil

if 'win32' in sys.platform:
    import win32api

dp20_pid = 0xd11c
dpp_pid = 0xd11d
all_dp_pids = [dp20_pid, dpp_pid]

def is_duckypad_pid(this_pid):
    return this_pid in all_dp_pids

def get_duckypad_path():
    dp_path_list = []
    if 'win32' in sys.platform:
        for device_dict in hid.enumerate():
            if device_dict['vendor_id'] == 0x0483 and \
            is_duckypad_pid(device_dict['product_id']) and \
            device_dict['usage'] == 58:
                dp_path_list.append(device_dict['path'])
    else:
        for device_dict in hid.enumerate():
            if device_dict['vendor_id'] == 0x0483 and \
            is_duckypad_pid(device_dict['product_id']):
                dp_path_list.append(device_dict['path'])
    return dp_path_list

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64
DUCKYPAD_TO_PC_HID_BUF_SIZE = 64

HID_RESPONSE_OK = 0
HID_RESPONSE_ERROR = 1
HID_RESPONSE_BUSY = 2
HID_RESPONSE_EOF = 3

HID_COMMAND_SW_RESET = 20

# def is_dp_ready():
#     dp_info = get_dp_info()
#     if dp_info is None:
#         return False, 'duckyPad not Found!'
#     if dp_info[2] == 0:
#         return True, 'All good!'
#     return False, 'duckyPad is busy!\n\nMake sure no script is running.'

def duckypad_hid_sw_reset(reboot_into_usb_msc_mode=False):
    pc_to_duckypad_buf = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
    pc_to_duckypad_buf[0] = 5   # HID Usage ID, always 5
    pc_to_duckypad_buf[2] = HID_COMMAND_SW_RESET    # Command type
    if(reboot_into_usb_msc_mode):
        pc_to_duckypad_buf[3] = 1 
    h.write(pc_to_duckypad_buf)

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

def make_dp_info_dict(hid_msg):
    this_dict = {}
    this_dict['fw_version'] = f"{hid_msg[3]}.{hid_msg[4]}.{hid_msg[5]}"
    this_dict['dp_model'] = f"{hid_msg[6]}"
    serial_number_uint32_t = int.from_bytes(hid_msg[7:11], byteorder='big')
    this_dict['serial'] = f'{serial_number_uint32_t:08X}'.upper()
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
        if result[2] != 0: # status is not SUCCESS
            continue
        this_dict = make_dp_info_dict(result)
        dp_info_list.append(this_dict)
    return dp_info_list

# all_dp_paths = get_duckypad_path()
# all_dp_info = get_all_dp_info(all_dp_paths)
# print(all_dp_info)