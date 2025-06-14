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
					elif line.startswith("UPPER_HS 1"):
						self.is_upper_re_halfstep = True
					elif line.startswith("LOWER_HS 1"):
						self.is_lower_re_halfstep = True
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
		if not folder_name.startswith('profile'):
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

	def __init__(self):
		super(dp_profile, self).__init__()
		self.path = None
		self.name = None
		self.keylist = [None] * MAX_KEY_COUNT
		self.bg_color = (84,22,180)
		self.kd_color = None
		self.dim_unused = True
		self.is_landscape = False
		self.is_upper_re_halfstep = False
		self.is_lower_re_halfstep = False

def read_profile_order_file(txt_path):
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
			if pf_number >= MAX_PROFILE_COUNT:
				continue
			profile_num_dict[pf_name] = pf_number
	profile_info_list = []
	for key in profile_num_dict:
		profile_info_list.append((profile_num_dict[key], key))
	profile_info_list.sort(key=lambda tup: tup[0])
	return profile_info_list

def build_profile_with_pfinfo_txt(root_dir_path, profile_info_txt_path):
	my_dirs = [d for d in os.listdir(root_dir_path) if os.path.isdir(os.path.join(root_dir_path, d))]
	my_dirs = [x for x in my_dirs if x.startswith('profile_')]
	profile_info_list = read_profile_order_file(profile_info_txt_path)

	profile_list = []
	for item in profile_info_list:
		pf_number = item[0]
		pf_name = item[1]
		this_profile_folder_name = f"profile_{pf_name}"
		if this_profile_folder_name not in my_dirs:
			continue
		this_profile_folder_path = os.path.join(root_dir_path, this_profile_folder_name)
		this_profile = dp_profile()
		this_profile.load_from_path(this_profile_folder_path)
		profile_list.append(this_profile)

	return profile_list

def build_profile_without_pfinfo_txt(root_dir_path):
	my_dirs = [d for d in os.listdir(root_dir_path) if os.path.isdir(os.path.join(root_dir_path, d))]
	my_dirs = [x for x in my_dirs if x.startswith('profile') and x[7].isnumeric() and '_' in x]
	my_dirs.sort(key=lambda s: int(s[7:].split("_")[0]))
	my_dirs = [os.path.join(root_dir_path, d) for d in my_dirs if d.startswith("profile")]
	my_dirs = my_dirs[:MAX_PROFILE_COUNT]
	profile_list = []
	for item in my_dirs:
		this_profile = dp_profile()
		this_profile.load_from_path(item)
		profile_list.append(this_profile)
	return profile_list

def build_profile(root_dir_path):
	profile_info_txt_path = os.path.join(root_dir_path, profile_info_dot_txt)
	if os.path.exists(profile_info_txt_path) and os.path.isfile(profile_info_txt_path):
		return build_profile_with_pfinfo_txt(root_dir_path, profile_info_txt_path)
	return build_profile_without_pfinfo_txt(root_dir_path)

def import_profile_single(root_dir_path):
	this_profile = dp_profile()
	this_profile.load_from_path(root_dir_path)
	return this_profile


