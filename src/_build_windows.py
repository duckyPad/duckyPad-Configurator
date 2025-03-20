from glob import glob
import os
import PyInstaller.__main__
import shutil
import sys

if 'win32' not in sys.platform:
    print("this script is for windows only!")
    exit()

def clean(additional=None):
	removethese = ['__pycache__','build','dist','*.spec']
	if additional:
		removethese.append(additional)
	for _object in removethese:
		target=glob(os.path.join('.', _object))
		for _target in target:
			try:
				if os.path.isdir(_target):
					shutil.rmtree(_target)
				else:
					os.remove(_target)
			except:
				print(f'Error deleting {_target}.')


THIS_VERSION = None
try:
	mainfile = open('duckypad_config.py')
	for line in mainfile:
		if "THIS_VERSION_NUMBER =" in line:
			THIS_VERSION = line.replace('\n', '').replace('\r', '').split("'")[-2]
	mainfile.close()
except Exception as e:
	print('build_windows exception:', e)
	exit()

if THIS_VERSION is None:
	print('could not find version number!')
	exit()

# --noconsole
clean(additional='duckypad*.zip')
PyInstaller.__main__.run(['duckypad_config.py','--icon=_icon.ico'])

output_folder_path = os.path.join('.', "dist")
original_name = os.path.join(output_folder_path, "duckypad_config")
new_name = os.path.join(output_folder_path, "duckypad_config_" + THIS_VERSION + "_win10_x64")

print(original_name)
print(new_name)

os.rename(original_name, new_name)
zip_file_name = "duckypad_config_" + THIS_VERSION + "_win10_x64"
shutil.make_archive(zip_file_name, 'zip', new_name)

clean()