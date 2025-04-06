import json
from shared import *
import urllib.request

pc_app_release_url = "https://api.github.com/repos/duckyPad/duckyPad-Configurator/releases/latest"
firmware_url_dpp = 'https://api.github.com/repos/dekuNukem/duckyPad-Pro/contents/firmware?ref=master'
firmware_url_dp20 = 'https://api.github.com/repos/dekuNukem/duckyPad/contents/firmware?ref=master'

def versiontuple(v):
    return tuple(map(int, (v.strip('v').split("."))))

"""
0 no update
1 has update
2 unknown
"""
def get_pc_app_update_status(this_version):
	try:
		result_dict = json.loads(urllib.request.urlopen(pc_app_release_url, timeout=2).read())
		this_version = versiontuple(this_version)
		remote_version = versiontuple(result_dict['tag_name'])
		return int(remote_version > this_version)
	except Exception as e:
		print('get_pc_app_update_status:', e)
		return 2
"""
0 no update
1 has update
2 unknown
"""
def get_firmware_update_status_dpp(dp_info_dict):
	try:
		current_version = dp_info_dict['fw_version']
		file_list = json.loads(urllib.request.urlopen(firmware_url_dpp, timeout=2).read())
		dfu_list = [x['name'] for x in file_list if 'name' in x and 'type' in x and x['type'] == 'file']
		dfu_list = [d.replace('DPP_FW_', '').replace('.bin', '').split('_')[0] for d in dfu_list if d.startswith('DPP_FW_') and d.endswith('.bin')]
		dfu_list.sort(key=lambda s: list(map(int, s.split('.'))))
		this_version = versiontuple(current_version)
		remote_version = versiontuple(dfu_list[-1])
		print('DP24 this:', this_version, '\nremote:', remote_version)
		return int(remote_version > this_version)
	except Exception as e:
		print('get_firmware_update_status:', e)
		return 2

def get_firmware_update_status_dp20(dp_info_dict):
	try:
		current_version = dp_info_dict['fw_version']
		file_list = json.loads(urllib.request.urlopen(firmware_url_dp20).read())
		dfu_list = [x['name'] for x in file_list if 'name' in x and 'type' in x and x['type'] == 'file']
		dfu_list = [d.replace('duckypad_v', '').replace('.dfu', '') for d in dfu_list if d.startswith('duckypad_v') and d.endswith('.dfu')]
		dfu_list.sort(key=lambda s: list(map(int, s.split('.'))))
		this_version = versiontuple(current_version)
		remote_version = versiontuple(dfu_list[-1])
		print('DP20 this:', this_version, '\nremote:', remote_version)
		return int(remote_version > this_version)
	except Exception as e:
		print('get_firmware_update_status:', e)
		return 2

def get_firmware_update_status(dp_info_dict):
	if dp_info_dict['dp_model'] == DP_MODEL_OG_DUCKYPAD:
		return get_firmware_update_status_dp20(dp_info_dict)
	elif dp_info_dict['dp_model'] == DP_MODEL_DUCKYPAD_PRO:
		return get_firmware_update_status_dpp(dp_info_dict)
	return 2

# result = get_firmware_update_status('0.2.0')
# print(result)
