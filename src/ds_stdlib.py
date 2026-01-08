import os
import time

"""
Should not have HARD CODED memory address
Must be compatible with all duckyScript and duckyPad versions

DPDSSTDLIB

TODO:
bitread, set, clear, toggle?
math abs, min, max?
memcpy?
try_set_led?
show error and quit? for unsupported hardwares
"""

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
