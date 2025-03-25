import os
import sys
from shared import *

class dp_key(object):
	def __str__(self):
		ret = ""
		ret += str('...............') + '\n'
		ret += "path:\t" + str(self.path) + '\n'
		ret += "name:\t" + str(self.name) + '\n'
		ret += "name2:\t" + str(self.name_line2) + '\n'
		ret += "index:\t" + str(self.index) + '\n'
		ret += "color:\t" + str(self.color) + '\n'
		ret += "abort:\t" + str(self.allow_abort) + '\n'
		ret += "norep:\t" + str(self.dont_repeat) + '\n'
		ret += "scr:\t" + str(len(self.script)) + " characters\n"
		ret += "scr_r:\t" + str(len(self.script_on_release)) + " characters\n"
		ret += str('...............') + '\n'
		return ret

	def __init__(self, path_on_press=None, path_on_release=None):
		super(dp_key, self).__init__()
		self.path = path_on_press
		self.path_on_release = path_on_release
		self.name = None
		self.name_line2 = None
		self.index = None
		self.color = None
		self.script = ''
		self.script_on_release = ''
		self.binary_array = None
		self.binary_array_on_release = None
		self.allow_abort = False
		self.dont_repeat = False

# -----------------------------------------------------------

def get_script(path):
	if path is None or os.path.exists(path) is False:
		return ""
	try:
		with open(path, encoding='utf8') as keyfile:
			return keyfile.read()
	except Exception as e:
		print('get_script exception:', e)
		return ""

class dp_profile(object):
	def add_key_if_doesnt_exist(self, index):
		if self.keylist[index] is None:
			self.keylist[index] = dp_key()
			self.keylist[index].index = index

	def read_config(self, path):
		try:
			with open(os.path.join(path, "config.txt")) as configfile:
				for line in configfile:
					line = line.replace('\n', '').replace('\r', '')
					while('  ' in line):
						line = line.replace('  ', ' ')					
					this_split = line.split(' ', 1)
					if line.startswith('BG_COLOR '):
						temp_split = line.split(' ')
						self.bg_color = (int(temp_split[1]), int(temp_split[2]), int(temp_split[3]))
					elif line.startswith('KEYDOWN_COLOR '):
						temp_split = line.split(' ')
						self.kd_color = (int(temp_split[1]), int(temp_split[2]), int(temp_split[3]))
					elif line.startswith("DIM_UNUSED_KEYS 0"):
						self.dim_unused = False
					elif line.startswith("IS_LANDSCAPE 1"):
						self.is_landscape = True
					elif this_split[0].startswith('z'):
						this_index = int(this_split[0][1:]) - 1
						self.add_key_if_doesnt_exist(this_index)
						self.keylist[this_index].name = this_split[1]
					elif this_split[0].startswith('x'):
						this_index = int(this_split[0][1:]) - 1
						self.add_key_if_doesnt_exist(this_index)
						self.keylist[this_index].name_line2 = this_split[1]
					elif this_split[0].startswith('ab'):
						this_index = int(this_split[1]) - 1
						self.add_key_if_doesnt_exist(this_index)
						self.keylist[this_index].allow_abort = True
					elif this_split[0].startswith('dr'):
						this_index = int(this_split[1]) - 1
						self.add_key_if_doesnt_exist(this_index)
						self.keylist[this_index].dont_repeat = True
					elif this_split[0].startswith('SWCOLOR_'):
						this_index = int(this_split[0].split("_")[-1]) - 1
						self.add_key_if_doesnt_exist(this_index)
						temp_split = line.split(' ')
						self.keylist[this_index].color = (int(temp_split[1]), int(temp_split[2]), int(temp_split[3]))
		except Exception as e:
			print('>>>>> read_config:', path, e)
			pass

	def load_from_path(self, path):
		folder_name = os.path.basename(os.path.normpath(path))
		if not folder_name.startswith('profile_'):
			print("invalid profile folder:", folder_name)
			return
		self.path = path
		self.name = folder_name.split('_', 1)[-1]
		self.read_config(path)
		for this_key in self.keylist:
			if this_key is not None:
				on_press_path = os.path.join(path, f'key{this_key.index+1}.txt')
				on_release_path = os.path.join(path, f'key{this_key.index+1}-release.txt')
				this_key.script = get_script(on_press_path)
				this_key.script_on_release = get_script(on_release_path)

	def __str__(self):
		ret = ""
		ret += str('-----Profile info-----') + '\n'
		ret += "path:\t" + str(self.path) + '\n'
		ret += "name:\t" + str(self.name) + '\n'
		ret += "bg_color:\t" + str(self.bg_color) + '\n'
		ret += "kd_color:\t" + str(self.kd_color) + '\n'
		ret += "dim_unused:\t" + str(self.dim_unused) + '\n'
		ret += "key count:\t" + str(len([x for x in self.keylist if x is not None])) + '\n'
		# ret += "keys:\n"
		# for item in [x for x in self.keylist]:
		# 	ret += str(item) + '\n'
		# ret += str('----------------------') + '\n'
		return ret

	def __init__(self, dp_descrip):
		super(dp_profile, self).__init__()
		self.path = None
		self.name = None
		self.keylist = [None] * (dp_descrip.MECH_OBSW_COUNT + dp_descrip.ROTARY_ENCODER_SW_COUNT + dp_descrip.ONBOARD_SPARE_GPIO_COUNT + dp_descrip.MAX_EXPANSION_CHANNEL)
		self.bg_color = (84,22,180)
		self.kd_color = None
		self.dim_unused = True
		self.is_landscape = False

def read_profile_order_file(txt_path, dp_descrip):
	profile_num_dict = {}
	with open(txt_path) as fff:
		for line in fff:
			line = line.strip(" \r\n")
			line_split = line.split(" ", 1)
			try:
				pf_number = int(line_split[0])
				pf_name = line_split[1]
			except Exception as e:
				continue
			if pf_number >= dp_descrip.MAX_PROFILE_COUNT:
				continue
			profile_num_dict[pf_name] = pf_number
	profile_info_list = []
	for key in profile_num_dict:
		profile_info_list.append((profile_num_dict[key], key))
	profile_info_list.sort(key=lambda tup: tup[0])
	return profile_info_list

def build_profile(root_dir_path, dp_descrip):
	my_dirs = [d for d in os.listdir(root_dir_path) if os.path.isdir(os.path.join(root_dir_path, d))]
	my_dirs = [x for x in my_dirs if x.startswith('profile_')]
	profile_info_txt_path = os.path.join(root_dir_path, profile_info_dot_txt)
	profile_info_list = read_profile_order_file(profile_info_txt_path, dp_descrip)

	profile_list = []
	for item in profile_info_list:
		pf_number = item[0]
		pf_name = item[1]
		this_profile_folder_name = f"profile_{pf_name}"
		if this_profile_folder_name not in my_dirs:
			continue
		this_profile_folder_path = os.path.join(root_dir_path, this_profile_folder_name)
		this_profile = dp_profile(dp_descrip)
		this_profile.load_from_path(this_profile_folder_path)
		profile_list.append(this_profile)

	return profile_list

def import_profile_single(root_dir_path, dp_descrip):
	this_profile = dp_profile(dp_descrip)
	this_profile.load_from_path(root_dir_path)
	return this_profile

def import_profile(root_dir_path, dp_descrip):
	try:
		key_file_list = [x for x in os.listdir(root_dir_path) if x.endswith('.txt') and x.startswith('key') and x[3].isnumeric()]
		if len(key_file_list) != 0:
			return True, [import_profile_single(root_dir_path, dp_descrip)]
	except Exception as e:
		return False, str(e)
	try:
		return True, build_profile(root_dir_path)
	except Exception as e:
		return False, str(e)
	return False, "unknown error"

# fff = import_profile("sample_profiles/profile1_windows")
# print(fff)

"""
build_profile()




SW_MATRIX_NUM_COLS = 4
SW_MATRIX_NUM_ROWS = 5
MECH_OBSW_COUNT = (SW_MATRIX_NUM_COLS * SW_MATRIX_NUM_ROWS)
ROTARY_ENCODER_SW_COUNT = 6
ONBOARD_SPARE_GPIO_COUNT = 10

dpp_descriptor = dp_descriptor()
dpp_descriptor.MECH_OBSW_COUNT = MECH_OBSW_COUNT
dpp_descriptor.ROTARY_ENCODER_SW_COUNT = ROTARY_ENCODER_SW_COUNT
dpp_descriptor.MAX_EXPANSION_CHANNEL = MAX_EXPANSION_CHANNEL
dpp_descriptor.ONBOARD_SPARE_GPIO_COUNT = ONBOARD_SPARE_GPIO_COUNT
dpp_descriptor.MAX_PROFILE_COUNT = 64


profile_list = build_profile("./sample_profiles", dpp_descriptor)

print(profile_list)

"""
