import os
import time
import requests
from enum import IntEnum
import webbrowser
from shared import *

default_stdlib_code = """

FUN WAITKEY(key_id)
    WHILE 1
        VAR pressed = _BLOCKING_READKEY
        IF pressed == key_id
            RETURN 1
        END_IF
    END_WHILE
END_FUN

FUN MEMSET(addr, value, length)
    VAR i = 0
    WHILE i < length
        POKE8(addr + i, value)
        i = i + 1
    END_WHILE
END_FUN

FUN ABS(n)
    IF _UNSIGNED_MATH == 1
        RETURN n
    END_IF
    
    IF n < 0
        RETURN n * -1
    END_IF
    
    RETURN n
END_FUN

FUN MIN(a, b)
    IF a < b
        RETURN a
    END_IF
    RETURN b
END_FUN

FUN MAX(a, b)
    IF a > b
        RETURN a
    END_IF
    RETURN b
END_FUN

"""

std_lib_filename_prefix = "dpds_stdlib"

def ensure_dpds_stdlib(lib_dir_path):
    os.makedirs(lib_dir_path, exist_ok=True)
    file_exists = False
    for filename in os.listdir(lib_dir_path):
        if filename.startswith(std_lib_filename_prefix) and filename.endswith(".txt"):
            file_exists = True
            break

    if not file_exists:
        timestamp = int(time.time())
        new_filename = f"{std_lib_filename_prefix}_{timestamp}.txt"
        file_path = os.path.join(lib_dir_path, new_filename)
        with open(file_path, 'w') as f:
            f.write(default_stdlib_code)
        print(f"Created new stdlib file: {file_path}")

def get_latest_stdlib_lines(lib_dir_path):
    """
    Finds the file with the newest timestamp in lib_dir_path and returns its content.
    Returns default_stdlib_code (as list) on any error.
    """
    try:
        candidates = []
        search_prefix = f"{std_lib_filename_prefix}_"
        
        for filename in os.listdir(lib_dir_path):
            if filename.startswith(search_prefix) and filename.endswith(".txt"):
                timestamp_str = filename[len(search_prefix):-4]
                try:
                    timestamp = int(timestamp_str)
                    candidates.append((timestamp, filename))
                except ValueError:
                    continue

        if not candidates:
            raise FileNotFoundError("No matching library files found.")
        _, newest_filename = max(candidates, key=lambda item: item[0])
        
        full_path = os.path.join(lib_dir_path, newest_filename)
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read().splitlines()
    except Exception as e:
        print("get_latest_stdlib_lines:", e)
    return default_stdlib_code.splitlines()

class stdlib_fetch_result(IntEnum):
    SUCCESS = 0
    TOO_SOON = 1
    NETWORK_ERROR = 2
    OTHER_ERROR = 3

stdlib_readme_url = "https://github.com/duckyPad/DPDS-Standard-Library/blob/master/README.md"

def open_stdlib_doc_url():
    open_url_safe(stdlib_readme_url)

stdlib_url = 'https://raw.githubusercontent.com/duckyPad/DPDS-Standard-Library/refs/heads/master/releases/duckypad_stdlib_latest.txt'
STDLIB_CHECK_INTERVAL_HOURS = 12

def fetch_update(stdlib_path, force_fetch=False):
    """
    Downloads a copy of the latest stdlib source from a URL, if enough time has elapsed since last check, or if force_fetch is True.
    """
    try:
        current_time = int(time.time())
        existing_files = []
        latest_timestamp = 0

        # 1. Identify existing files and find the latest timestamp
        if os.path.exists(stdlib_path):
            for filename in os.listdir(stdlib_path):
                if filename.startswith(std_lib_filename_prefix) and filename.endswith(".txt"):
                    existing_files.append(filename)
                    try:
                        # Extract timestamp: remove prefix (len + 1 for underscore) and suffix (.txt is 4 chars)
                        ts_part = filename[len(std_lib_filename_prefix) + 1 : -4]
                        ts = int(ts_part)
                        if ts > latest_timestamp:
                            latest_timestamp = ts
                    except ValueError:
                        continue
        
        # 2. Check if we should download
        if not force_fetch and latest_timestamp > 0:
            hours_elapsed = (current_time - latest_timestamp) / 3600
            if hours_elapsed < STDLIB_CHECK_INTERVAL_HOURS:
                return stdlib_fetch_result.TOO_SOON

        # 3. Perform Download
        response = requests.get(stdlib_url, timeout=30)
        response.raise_for_status()

        # 4. Cleanup old files
        for filename in existing_files:
            file_path = os.path.join(stdlib_path, filename)
            try:
                os.remove(file_path)
            except OSError:
                pass # Best effort deletion

        # 5. Save new file
        new_filename = f"{std_lib_filename_prefix}_{current_time}.txt"
        new_file_path = os.path.join(stdlib_path, new_filename)
        
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)

        return stdlib_fetch_result.SUCCESS

    except requests.exceptions.RequestException:
        return stdlib_fetch_result.NETWORK_ERROR
    except Exception:
        return stdlib_fetch_result.OTHER_ERROR
    
# result = fetch_update("./test")
# print(result)