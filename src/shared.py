import os
import shutil
import webbrowser
from platformdirs import *
from pathlib import Path
from hid_common import *

cmd_REPEAT = "REPEAT"
cmd_REM = "REM"
cmd_C_COMMENT = "//"

cmd_DEFAULTDELAY = "DEFAULTDELAY"
cmd_DEFAULTCHARDELAY = "DEFAULTCHARDELAY"
cmd_CHARJITTER = "CHARJITTER"
cmd_DELAY = "DELAY"
cmd_STRING = "STRING"
cmd_STRINGLN = "STRINGLN"

cmd_UARTPRINT = "UARTPRINT"
cmd_EMUK = "EMUK"
cmd_LOOP = "LOOP"
cmd_LCR = "LCR"
cmd_DP_SLEEP = "DP_SLEEP"
cmd_PREV_PROFILE = "PREV_PROFILE"
cmd_NEXT_PROFILE = "NEXT_PROFILE"
cmd_GOTO_PROFILE = "GOTO_PROFILE"
cmd_GOTO_PROFILE_NAME = "GOTO_PROFILE_NAME"
cmd_PEEK_PROFILE = "PEEK_PROFILE"

cmd_KEYDOWN = "KEYDOWN"
cmd_KEYUP = "KEYUP"
cmd_INJECT_MOD = "INJECT_MOD"

cmd_SWCOLOR = "SWCOLOR"
cmd_SWCC = "SWC_SET"
cmd_SWCF = "SWC_FILL"
cmd_SWCR = "SWC_RESET"

cmd_OLED_PRINT = "OLED_PRINT"
cmd_OLED_UPDATE = "OLED_UPDATE"
cmd_OLED_CURSOR = "OLED_CURSOR"
cmd_OLED_BLANK = "OLED_CLEAR"
cmd_OLED_RESTORE = "OLED_RESTORE"

cmd_OLED_LINE = "OLED_LINE"
cmd_OLED_RECT = "OLED_RECT"
cmd_OLED_CIRCLE = "OLED_CIRCLE"

cmd_BCLR = "BCLR"

cmd_LMOUSE = "LMOUSE"
cmd_RMOUSE = "RMOUSE"
cmd_MMOUSE = "MMOUSE"
cmd_MOUSE_MOVE = "MOUSE_MOVE"
cmd_MOUSE_WHEEL = "MOUSE_WHEEL"

cmd_VAR_DECLARE = "VAR"
cmd_VAR_ASSIGN = "$"
cmd_DEFINE = "DEFINE"

cmd_IF = "IF"
cmd_THEN = 'THEN'
cmd_ELSE_IF = "ELSE IF"
cmd_END_IF = "END_IF"
cmd_ELSE = "ELSE"

cmd_WHILE = "WHILE"
cmd_END_WHILE = "END_WHILE"

cmd_FUNCTION = "FUNCTION"
cmd_END_FUNCTION = "END_FUNCTION"

cmd_RETURN = "RETURN"
cmd_HALT = "HALT"

cmd_ESCAPE = "ESCAPE"
cmd_ESC = "ESC"
cmd_ENTER = "ENTER"
cmd_UP = "UP"
cmd_DOWN = "DOWN"
cmd_LEFT = "LEFT"
cmd_RIGHT = "RIGHT"
cmd_UPARROW = "UPARROW"
cmd_DOWNARROW = "DOWNARROW"
cmd_LEFTARROW = "LEFTARROW"
cmd_RIGHTARROW = "RIGHTARROW"
cmd_BACKSPACE = "BACKSPACE"
cmd_TAB = "TAB"
cmd_CAPSLOCK = "CAPSLOCK"
cmd_PRINTSCREEN = "PRINTSCREEN"
cmd_SCROLLLOCK = "SCROLLLOCK"
cmd_PAUSE = "PAUSE"
cmd_BREAK = "BREAK"
cmd_INSERT = "INSERT"
cmd_HOME = "HOME"
cmd_PAGEUP = "PAGEUP"
cmd_PAGEDOWN = "PAGEDOWN"
cmd_DELETE = "DELETE"
cmd_END = "END"
cmd_SPACE = "SPACE"

cmd_SHIFT = "SHIFT"
cmd_RSHIFT = "RSHIFT"

cmd_ALT = "ALT"
cmd_RALT = "RALT"
cmd_OPTION = "OPTION"
cmd_ROPTION = "ROPTION"

cmd_GUI = "GUI"
cmd_WINDOWS = "WINDOWS"
cmd_COMMAND = "COMMAND"
cmd_RWINDOWS = "RWINDOWS"
cmd_RCOMMAND = "RCOMMAND"

cmd_CONTROL = "CONTROL"
cmd_CTRL = "CTRL"
cmd_RCONTROL = "RCONTROL"
cmd_RCTRL = "RCTRL"

cmd_NUMLOCK = "NUMLOCK" # Keyboard Num Lock and Clear
cmd_KPSLASH = "KP_SLASH" # Keypad /
cmd_KPASTERISK = "KP_ASTERISK" # Keypad *
cmd_KPMINUS = "KP_MINUS" # Keypad -
cmd_KPPLUS = "KP_PLUS" # Keypad +
cmd_KPENTER = "KP_ENTER" # Keypad ENTER
cmd_KP1 = "KP_1" # Keypad 1 and End
cmd_KP2 = "KP_2" # Keypad 2 and Down Arrow
cmd_KP3 = "KP_3" # Keypad 3 and PageDn
cmd_KP4 = "KP_4" # Keypad 4 and Left Arrow
cmd_KP5 = "KP_5" # Keypad 5
cmd_KP6 = "KP_6" # Keypad 6 and Right Arrow
cmd_KP7 = "KP_7" # Keypad 7 and Home
cmd_KP8 = "KP_8" # Keypad 8 and Up Arrow
cmd_KP9 = "KP_9" # Keypad 9 and Page Up
cmd_KP0 = "KP_0" # Keypad 0 and Insert
cmd_KPDOT = "KP_DOT" # Keypad . and Delete
cmd_KPEQUAL = "KP_EQUAL" # Keypad EQUAL

cmd_MK_VOLUP = "MK_VOLUP"
cmd_MK_VOLDOWN = "MK_VOLDOWN"
cmd_MK_VOLMUTE = "MK_MUTE"
cmd_MK_PREV = "MK_PREV"
cmd_MK_NEXT = "MK_NEXT"
cmd_MK_PLAYPAUSE = "MK_PP"
cmd_MK_STOP = "MK_STOP"

cmd_KATAKANAHIRAGANA = "KATAKANAHIRAGANA"
cmd_HENKAN = "HENKAN"
cmd_MUHENKAN = "MUHENKAN"
cmd_KATAKANA = "KATAKANA"
cmd_HIRAGANA = "HIRAGANA"
cmd_ZENKAKUHANKAKU = "ZENKAKUHANKAKU"

cmd_MENU = "MENU"
cmd_APP = "APP"
cmd_POWER = "POWER"

cmd_LOOP_BREAK = "LBREAK"
cmd_CONTINUE = "CONTINUE"

cmd_REM_BLOCK = "REM_BLOCK"
cmd_END_REM = "END_REM"

cmd_STRINGLN_BLOCK = "STRINGLN_BLOCK"
cmd_END_STRINGLN = "END_STRINGLN"

cmd_STRING_BLOCK = "STRING_BLOCK"
cmd_END_STRING = "END_STRING"

english_alphabets = [
'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
'A', 'B', 'C', 'D', 'E','F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
valid_var_chars = ['0', '1', '2', '3', '4', '5', '6', '7','8', '9', '_'] + english_alphabets
valid_char_for_define_replacements = [' ', '=', '+', '-', '*', '/', '%', '^', '>', '<', '!', '|', '(', ')', '&']

valid_char_for_define_replacements = set(valid_char_for_define_replacements)
english_alphabets = set(english_alphabets)
valid_var_chars = set(valid_var_chars)

def replace_DEFINE(pgm_line, dd):
    if pgm_line.startswith(cmd_STRING+" ") or pgm_line.startswith(cmd_STRINGLN+" "):
        dd.pop("TRUE", None)
        dd.pop("FALSE", None)
    else:
        dd['TRUE'] = 1
        dd['FALSE'] = 0
    dd_list_longest_first = sorted(list(dd.keys()), key=len, reverse=True)
    temp_line = f" {pgm_line} "
    for key in dd_list_longest_first:
        start_index = 0
        loop_count = 0
        while 1:
            loop_count += 1
            # hacky way to detect recursive DEFINE
            if loop_count > 127:
                return False, ""
            # print("start_index", start_index)
            key_location = str(temp_line).find(key, start_index)
            if key_location == -1:
                break
            # print(key, "still in:", temp_line, 'at location', key_location)
            letter_before = temp_line[key_location - 1]
            letter_after = temp_line[key_location + len(key)]
            # print("letter_before:", letter_before)
            # print("letter_after:", letter_after)
            if letter_before in valid_char_for_define_replacements and letter_after in valid_char_for_define_replacements:
                # print("STRING BEFORE", temp_line[:key_location])
                # print("STRING AFTER", temp_line[key_location + len(key):])
                temp_line = temp_line[:key_location] + str(dd[key]) + temp_line[key_location + len(key):]
            else:
                start_index = key_location + len(key)
    # print("AFTER REPLACEMENT:", temp_line)
    return True, temp_line[1:len(temp_line)-1]

KEY_LEFT_CTRL =  0x01
KEY_LEFT_SHIFT = 0x02
KEY_LEFT_ALT =   0x04
KEY_LEFT_GUI =  0x08
KEY_RIGHT_CTRL =  0x10
KEY_RIGHT_SHIFT = 0x20
KEY_RIGHT_ALT =   0x40
KEY_RIGHT_GUI =  0x80

KEY_RETURN = 0X28
KEY_ESC = 0X29
KEY_BACKSPACE = 0X2A
KEY_TAB = 0X2B
KEY_CAPS_LOCK = 0X39
KEY_PRINT_SCREEN = 0X46
KEY_SCROLL_LOCK = 0X47
KEY_PAUSE = 0X48
KEY_INSERT = 0X49
KEY_HOME = 0X4A
KEY_PAGE_UP = 0X4B
KEY_DELETE = 0X4C
KEY_END = 0X4D
KEY_PAGE_DOWN = 0X4E
KEY_RIGHT_ARROW = 0X4F
KEY_LEFT_ARROW = 0X50
KEY_DOWN_ARROW = 0X51
KEY_UP_ARROW = 0X52

KEY_NUMLOCK = 0x53 # Keyboard Num Lock and Clear
KEY_KPSLASH = 0x54 # Keypad /
KEY_KPASTERISK = 0x55 # Keypad *
KEY_KPMINUS = 0x56 # Keypad -
KEY_KPPLUS = 0x57 # Keypad +
KEY_KPENTER = 0x58 # Keypad ENTER
KEY_KP1 = 0x59 # Keypad 1 and End
KEY_KP2 = 0x5a # Keypad 2 and Down Arrow
KEY_KP3 = 0x5b # Keypad 3 and PageDn
KEY_KP4 = 0x5c # Keypad 4 and Left Arrow
KEY_KP5 = 0x5d # Keypad 5
KEY_KP6 = 0x5e # Keypad 6 and Right Arrow
KEY_KP7 = 0x5f # Keypad 7 and Home
KEY_KP8 = 0x60 # Keypad 8 and Up Arrow
KEY_KP9 = 0x61 # Keypad 9 and Page Up
KEY_KP0 = 0x62 # Keypad 0 and Insert
KEY_KPDOT = 0x63 # Keypad . and Delete
KEY_KPEQUAL = 0x67 # Keypad =

KEY_MENU = 0x65
KEY_POWER = 0x66 # Keyboard Power

KEY_MK_VOLDOWN = 0x80
KEY_MK_VOLUP = 0x40
KEY_MK_VOLMUTE = 0x20
KEY_MK_PLAYPAUSE = 0x10
KEY_MK_STOP = 0x4
KEY_MK_PREV = 0x2
KEY_MK_NEXT = 0x1

KEY_KATAKANAHIRAGANA = 0x88
KEY_YEN = 0x89
KEY_HENKAN = 0x8a
KEY_MUHENKAN = 0x8b

KEY_HANGEUL = 0x90 # korea
KEY_HANJA = 0x91 # korea
KEY_KATAKANA = 0x92
KEY_HIRAGANA = 0x93
KEY_ZENKAKUHANKAKU = 0x94

KEY_TYPE_UNKNOWN = 0
KEY_TYPE_CHAR = 1
KEY_TYPE_MODIFIER = 2
KEY_TYPE_SPECIAL = 3
KEY_TYPE_MEDIA = 4
KEY_TYPE_DEAD_GRAVE_ACCENT = 5
KEY_TYPE_DEAD_ACUTE_ACCENT = 6
KEY_TYPE_DEAD_CIRCUMFLEX = 7
KEY_TYPE_DEAD_TILDE = 8
KEY_TYPE_DEAD_DIAERESIS = 9
KEY_TYPE_DEAD_CEDILLA = 10
KEY_TYPE_MOUSE_BUTTON = 11
KEY_TYPE_MOUSE_WHEEL = 12
KEY_TYPE_MOUSE_MOVEMENT = 13

# name, code, type
ds3_keyname_dict = {

cmd_LMOUSE : (1, KEY_TYPE_MOUSE_BUTTON),
cmd_RMOUSE : (2, KEY_TYPE_MOUSE_BUTTON),
cmd_MMOUSE : (4, KEY_TYPE_MOUSE_BUTTON),
# cmd_MOUSE_MOVE : (0, KEY_TYPE_MOUSE_MOVEMENT),
# cmd_MOUSE_WHEEL : (0, KEY_TYPE_MOUSE_WHEEL), # those are not keys

cmd_UP : (KEY_UP_ARROW, KEY_TYPE_SPECIAL),
cmd_DOWN : (KEY_DOWN_ARROW, KEY_TYPE_SPECIAL),
cmd_LEFT : (KEY_LEFT_ARROW, KEY_TYPE_SPECIAL),
cmd_RIGHT : (KEY_RIGHT_ARROW, KEY_TYPE_SPECIAL),
cmd_UPARROW : (KEY_UP_ARROW, KEY_TYPE_SPECIAL),
cmd_DOWNARROW : (KEY_DOWN_ARROW, KEY_TYPE_SPECIAL),
cmd_LEFTARROW : (KEY_LEFT_ARROW, KEY_TYPE_SPECIAL),
cmd_RIGHTARROW : (KEY_RIGHT_ARROW, KEY_TYPE_SPECIAL),
cmd_ESCAPE : (KEY_ESC, KEY_TYPE_SPECIAL),
cmd_ESC : (KEY_ESC, KEY_TYPE_SPECIAL),
cmd_ENTER : (KEY_RETURN, KEY_TYPE_SPECIAL),
cmd_BACKSPACE : (KEY_BACKSPACE, KEY_TYPE_SPECIAL),
cmd_TAB : (KEY_TAB, KEY_TYPE_SPECIAL),
cmd_CAPSLOCK : (KEY_CAPS_LOCK, KEY_TYPE_SPECIAL),
cmd_PRINTSCREEN : (KEY_PRINT_SCREEN, KEY_TYPE_SPECIAL),
cmd_SCROLLLOCK : (KEY_SCROLL_LOCK, KEY_TYPE_SPECIAL),
cmd_PAUSE : (KEY_PAUSE, KEY_TYPE_SPECIAL),
cmd_BREAK : (KEY_PAUSE, KEY_TYPE_SPECIAL),
cmd_INSERT : (KEY_INSERT, KEY_TYPE_SPECIAL),
cmd_HOME : (KEY_HOME, KEY_TYPE_SPECIAL),
cmd_PAGEUP : (KEY_PAGE_UP, KEY_TYPE_SPECIAL),
cmd_PAGEDOWN : (KEY_PAGE_DOWN, KEY_TYPE_SPECIAL),
cmd_DELETE : (KEY_DELETE, KEY_TYPE_SPECIAL),
cmd_END : (KEY_END, KEY_TYPE_SPECIAL),
cmd_NUMLOCK : (KEY_NUMLOCK, KEY_TYPE_SPECIAL),
cmd_KPSLASH : (KEY_KPSLASH, KEY_TYPE_SPECIAL),
cmd_KPASTERISK : (KEY_KPASTERISK, KEY_TYPE_SPECIAL),
cmd_KPMINUS : (KEY_KPMINUS, KEY_TYPE_SPECIAL),
cmd_KPPLUS : (KEY_KPPLUS, KEY_TYPE_SPECIAL),
cmd_KPENTER : (KEY_KPENTER, KEY_TYPE_SPECIAL),
cmd_KP1 : (KEY_KP1, KEY_TYPE_SPECIAL),
cmd_KP2 : (KEY_KP2, KEY_TYPE_SPECIAL),
cmd_KP3 : (KEY_KP3, KEY_TYPE_SPECIAL),
cmd_KP4 : (KEY_KP4, KEY_TYPE_SPECIAL),
cmd_KP5 : (KEY_KP5, KEY_TYPE_SPECIAL),
cmd_KP6 : (KEY_KP6, KEY_TYPE_SPECIAL),
cmd_KP7 : (KEY_KP7, KEY_TYPE_SPECIAL),
cmd_KP8 : (KEY_KP8, KEY_TYPE_SPECIAL),
cmd_KP9 : (KEY_KP9, KEY_TYPE_SPECIAL),
cmd_KP0 : (KEY_KP0, KEY_TYPE_SPECIAL),
cmd_KPDOT : (KEY_KPDOT, KEY_TYPE_SPECIAL),
cmd_KPEQUAL : (KEY_KPEQUAL, KEY_TYPE_SPECIAL),
cmd_POWER : (KEY_POWER, KEY_TYPE_SPECIAL),
cmd_MENU : (KEY_MENU, KEY_TYPE_SPECIAL),
cmd_APP : (KEY_MENU, KEY_TYPE_SPECIAL),
cmd_KATAKANAHIRAGANA : (KEY_KATAKANAHIRAGANA, KEY_TYPE_SPECIAL),
cmd_HENKAN : (KEY_HENKAN, KEY_TYPE_SPECIAL),
cmd_MUHENKAN : (KEY_MUHENKAN, KEY_TYPE_SPECIAL),
cmd_KATAKANA : (KEY_KATAKANA, KEY_TYPE_SPECIAL),
cmd_HIRAGANA : (KEY_HIRAGANA, KEY_TYPE_SPECIAL),
cmd_ZENKAKUHANKAKU : (KEY_ZENKAKUHANKAKU, KEY_TYPE_SPECIAL),
"F1" : (0x3A, KEY_TYPE_SPECIAL),
"F2" : (0x3B, KEY_TYPE_SPECIAL),
"F3" : (0x3C, KEY_TYPE_SPECIAL),
"F4" : (0x3D, KEY_TYPE_SPECIAL),
"F5" : (0x3E, KEY_TYPE_SPECIAL),
"F6" : (0x3F, KEY_TYPE_SPECIAL),
"F7" : (0x40, KEY_TYPE_SPECIAL),
"F8" : (0x41, KEY_TYPE_SPECIAL),
"F9" : (0x42, KEY_TYPE_SPECIAL),
"F10" : (0x43, KEY_TYPE_SPECIAL),
"F11" : (0x44, KEY_TYPE_SPECIAL),
"F12" : (0x45, KEY_TYPE_SPECIAL),
"F13" : (0x68, KEY_TYPE_SPECIAL),
"F14" : (0x69, KEY_TYPE_SPECIAL),
"F15" : (0x6a, KEY_TYPE_SPECIAL),
"F16" : (0x6b, KEY_TYPE_SPECIAL),
"F17" : (0x6c, KEY_TYPE_SPECIAL),
"F18" : (0x6d, KEY_TYPE_SPECIAL),
"F19" : (0x6e, KEY_TYPE_SPECIAL),
"F20" : (0x6f, KEY_TYPE_SPECIAL),
"F21" : (0x70, KEY_TYPE_SPECIAL),
"F22" : (0x71, KEY_TYPE_SPECIAL),
"F23" : (0x72, KEY_TYPE_SPECIAL),
"F24" : (0x73, KEY_TYPE_SPECIAL),
cmd_SPACE : (0x20, KEY_TYPE_CHAR),
cmd_SHIFT : (KEY_LEFT_SHIFT, KEY_TYPE_MODIFIER),
cmd_RSHIFT : (KEY_RIGHT_SHIFT, KEY_TYPE_MODIFIER),
cmd_ALT : (KEY_LEFT_ALT, KEY_TYPE_MODIFIER),
cmd_OPTION : (KEY_LEFT_ALT, KEY_TYPE_MODIFIER),
cmd_RALT : (KEY_RIGHT_ALT, KEY_TYPE_MODIFIER),
cmd_ROPTION : (KEY_RIGHT_ALT, KEY_TYPE_MODIFIER),
cmd_GUI : (KEY_LEFT_GUI, KEY_TYPE_MODIFIER),
cmd_WINDOWS : (KEY_LEFT_GUI, KEY_TYPE_MODIFIER),
cmd_RWINDOWS : (KEY_RIGHT_GUI, KEY_TYPE_MODIFIER),
cmd_COMMAND : (KEY_LEFT_GUI, KEY_TYPE_MODIFIER),
cmd_RCOMMAND : (KEY_RIGHT_GUI, KEY_TYPE_MODIFIER),
cmd_CTRL : (KEY_LEFT_CTRL, KEY_TYPE_MODIFIER),
cmd_CONTROL : (KEY_LEFT_CTRL, KEY_TYPE_MODIFIER),
cmd_RCTRL : (KEY_RIGHT_CTRL, KEY_TYPE_MODIFIER),
cmd_RCONTROL : (KEY_RIGHT_CTRL, KEY_TYPE_MODIFIER),
cmd_MK_VOLUP : (KEY_MK_VOLUP, KEY_TYPE_MEDIA),
cmd_MK_VOLDOWN : (KEY_MK_VOLDOWN, KEY_TYPE_MEDIA),
cmd_MK_VOLMUTE : (KEY_MK_VOLMUTE, KEY_TYPE_MEDIA),
cmd_MK_PREV : (KEY_MK_PREV, KEY_TYPE_MEDIA),
cmd_MK_NEXT : (KEY_MK_NEXT, KEY_TYPE_MEDIA),
cmd_MK_PLAYPAUSE : (KEY_MK_PLAYPAUSE, KEY_TYPE_MEDIA),
cmd_MK_STOP : (KEY_MK_STOP, KEY_TYPE_MEDIA),
}

GV_OFFSET = 64

internal_variable_dict = {
    '_DEFAULTDELAY': (0xffff - 0),
    '_DEFAULTCHARDELAY': (0xffff - 1),
    '_CHARJITTER': (0xffff - 2),
    "_RANDOM_MIN": (0xffff - 3),
    "_RANDOM_MAX": (0xffff - 4),
    "_RANDOM_INT": (0xffff - 5),
    "_TIME_MS": (0xffff - 6),
    "_READKEY": (0xffff - 7),
    "_LOOP_SIZE": (0xffff - 8),
    "_KEYPRESS_COUNT": (0xffff - 9),
    "_NEEDS_EPILOGUE": (0xffff - 10),
    "_TIME_S": (0xffff - 11),
    "_ALLOW_ABORT": (0xffff - 12),
    "_BLOCKING_READKEY": (0xffff - 13),
    "_IS_NUMLOCK_ON": (0xffff - 14),
    "_IS_CAPSLOCK_ON": (0xffff - 15),
    "_IS_SCROLLLOCK_ON": (0xffff - 16),
    "_DONT_REPEAT": (0xffff - 17),
    "_THIS_KEYID": (0xffff - 18),
    "_DP_MODEL": (0xffff - 19),
    "_RTC_IS_VALID": (0xffff - 20),
    "_RTC_UTC_OFFSET": (0xffff - 21),
    "_RTC_YEAR": (0xffff - 22),
    "_RTC_MONTH": (0xffff - 23),
    "_RTC_DAY": (0xffff - 24),
    "_RTC_HOUR": (0xffff - 25),
    "_RTC_MINUTE": (0xffff - 26),
    "_RTC_SECOND": (0xffff - 27),
    "_RTC_WDAY": (0xffff - 28),
    "_RTC_YDAY": (0xffff - 29),
    "_STR_PRINT_FORMAT": (0xffff - 30),
    "_STR_PRINT_PADDING": (0xffff - 31),
}

global_variable_dict = {
    "_GV0": (0xffff - GV_OFFSET - 0),
    "_GV1": (0xffff - GV_OFFSET - 1),
    "_GV2": (0xffff - GV_OFFSET - 2),
    "_GV3": (0xffff - GV_OFFSET - 3),
    "_GV4": (0xffff - GV_OFFSET - 4),
    "_GV5": (0xffff - GV_OFFSET - 5),
    "_GV6": (0xffff - GV_OFFSET - 6),
    "_GV7": (0xffff - GV_OFFSET - 7),
    "_GV8": (0xffff - GV_OFFSET - 8),
    "_GV9": (0xffff - GV_OFFSET - 9),
    "_GV10": (0xffff - GV_OFFSET - 10),
    "_GV11": (0xffff - GV_OFFSET - 11),
    "_GV12": (0xffff - GV_OFFSET - 12),
    "_GV13": (0xffff - GV_OFFSET - 13),
    "_GV14": (0xffff - GV_OFFSET - 14),
    "_GV15": (0xffff - GV_OFFSET - 15),
    "_GV16": (0xffff - GV_OFFSET - 16),
    "_GV17": (0xffff - GV_OFFSET - 17),
    "_GV18": (0xffff - GV_OFFSET - 18),
    "_GV19": (0xffff - GV_OFFSET - 19),
    "_GV20": (0xffff - GV_OFFSET - 20),
    "_GV21": (0xffff - GV_OFFSET - 21),
    "_GV22": (0xffff - GV_OFFSET - 22),
    "_GV23": (0xffff - GV_OFFSET - 23),
    "_GV24": (0xffff - GV_OFFSET - 24),
    "_GV25": (0xffff - GV_OFFSET - 25),
    "_GV26": (0xffff - GV_OFFSET - 26),
    "_GV27": (0xffff - GV_OFFSET - 27),
    "_GV28": (0xffff - GV_OFFSET - 28),
    "_GV29": (0xffff - GV_OFFSET - 29),
    "_GV30": (0xffff - GV_OFFSET - 30),
    "_GV31": (0xffff - GV_OFFSET - 31),
}

reserved_variable_dict = internal_variable_dict | global_variable_dict
MAX_NUMBER_OF_VARIABLES = 64

class ds_line:
    def __init__(self, content, lnum_sf1=-1, pplnum=-1):
        self.lnum_sf1 = lnum_sf1
        self.content = content
        self.preprocessed_lnum_ssf1 = pplnum

    def __repr__(self):
        return f"ds_line({self.lnum_sf1!r}, {self.content!r}, {self.preprocessed_lnum_ssf1!r})"

MAX_EXPANSION_MODULE_COUNT = 4
CHANNELS_PER_EXPANSION_MODULE = 8
MAX_EXPANSION_CHANNEL = MAX_EXPANSION_MODULE_COUNT * CHANNELS_PER_EXPANSION_MODULE

def ensure_dir(dir_path):
    os.makedirs(dir_path, exist_ok=1)

appname = 'duckypad_config'
appauthor = 'dekuNukem'
app_save_path = user_data_dir(appname, appauthor, roaming=True)
backup_path = os.path.join(app_save_path, 'profile_backups')
hid_dump_path = os.path.join(app_save_path, "hid_dump")
temp_dir_path = os.path.join(app_save_path, "temp_dir")

def open_discord_link():
    webbrowser.open("https://discord.gg/4sJCBx5")

def app_update_click(event):
    webbrowser.open('https://github.com/duckyPad/duckyPad-Configurator/releases/latest')

def open_profile_autoswitcher_url():
    webbrowser.open('https://github.com/duckyPad/duckyPad-profile-autoswitcher/blob/master/README.md')

def open_tindie_store():
    webbrowser.open('https://dekunukem.github.io/duckyPad-Pro/doc/store_links.html')

def open_mac_linux_instruction():
    webbrowser.open('https://dekunukem.github.io/duckyPad-Pro/doc/linux_macos_notes.html')

def script_instruction_click(event):
    webbrowser.open('https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html')

def open_dpp_page(event):
    webbrowser.open('https://dekunukem.github.io/duckyPad-Pro/README.html')

def open_duckypad_user_manual_url():
    webbrowser.open('https://dekunukem.github.io/duckyPad-Pro/doc/getting_started.html')

def open_duckypad_troubleshooting_url():
    webbrowser.open('https://dekunukem.github.io/duckyPad-Pro/doc/troubleshooting.html')

def rgb_to_hex(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

def make_list_of_ds_line_obj_from_str_listing(pgm_listing):
    obj_list = []
    for index, item in enumerate(pgm_listing):
        obj_list.append(ds_line(item, index+1))
    return obj_list

def make_final_script(ds_key, pgm_listing):
    final_listing = []
    if ds_key.allow_abort:
        final_listing.append("$_ALLOW_ABORT = 1")
    if ds_key.dont_repeat:
        final_listing.append("$_DONT_REPEAT = 1")
    final_listing += pgm_listing
    return final_listing

def last_two_levels(full_path):
    return os.path.join(*full_path.split(os.sep)[-2:])

"""
0 to 19: mechanical switches
20 to 25: rotary encoders
26 to 35: spare gpio pins, unused
36 to 65: expansion channels
"""

BUTTON_RE1_CW = 20
BUTTON_RE1_CCW = 21
BUTTON_RE1_PUSH = 22
BUTTON_RE2_CW = 23
BUTTON_RE2_CCW = 24
BUTTON_RE2_PUSH = 25

EXP_BUTTON_START = 36

def is_rotary_encoder_button(key_index_start_from_0):
    return BUTTON_RE1_CW <= key_index_start_from_0 <= BUTTON_RE2_PUSH

def is_expansion_button(key_index_start_from_0):
    return EXP_BUTTON_START <= key_index_start_from_0 <= EXP_BUTTON_START + MAX_EXPANSION_CHANNEL

KEY_NAME_MAX_CHAR_PER_LINE = 7

SW_MATRIX_NUM_COLS = 4
SW_MATRIX_NUM_ROWS = 5
MECH_OBSW_COUNT = (SW_MATRIX_NUM_COLS * SW_MATRIX_NUM_ROWS)
ROTARY_ENCODER_SW_COUNT = 6
ONBOARD_SPARE_GPIO_COUNT = 10
MAX_PROFILE_COUNT = 64
MAX_KEY_COUNT = (MECH_OBSW_COUNT + ROTARY_ENCODER_SW_COUNT + ONBOARD_SPARE_GPIO_COUNT + MAX_EXPANSION_CHANNEL)

profile_info_dot_txt = "profile_info.txt"

HID_COMMAND_READ_FILE = 11

HID_COMMAND_OPEN_FILE_FOR_WRITING = 14
HID_COMMAND_WRITE_FILE = 15
HID_COMMAND_CLOSE_FILE = 16
HID_COMMAND_DELETE_FILE = 17
HID_COMMAND_CREATE_DIR = 18
HID_COMMAND_DELETE_DIR = 19
HID_COMMAND_SW_RESET = 20

HID_COMMAND_DUMP_SD = 32
HID_COMMAND_OPEN_FILE_FOR_READING = 33

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64
DUCKYPAD_TO_PC_HID_BUF_SIZE = 64
HID_READ_FILE_PATH_SIZE_MAX = 55

class dp_file_op(object):
    def __str__(self):
        return (f"dp_file_op(\n"
                f"  action={self.action},\n"
                f"  local_dir={self.local_dir},\n"
                f"  source_parent={self.source_parent},\n"
                f"  source_path={self.source_path},\n"
                f"  destination_parent={self.destination_parent},\n"
                f"  destination_path={self.destination_path}\n"
                f")")

    def __init__(self):
        self.mkdir = "mkdir"
        self.rmdir = "rmdir"
        self.copy_file = "cpf"
        self.delete_file = "rmf"
        self.action = None
        self.source_parent = None
        self.source_path = None
        self.destination_parent = None
        self.destination_path = None
        self.local_dir = None
    
    def __eq__(self, other):
        if not isinstance(other, dp_file_op):
            return NotImplemented
        return (
            self.action == other.action and
            self.source_parent == other.source_parent and
            self.source_path == other.source_path and
            self.destination_parent == other.destination_parent and
            self.destination_path == other.destination_path and
            self.local_dir == other.local_dir
        )

    def __hash__(self):
        return hash((
            self.action,
            self.source_parent,
            self.source_path,
            self.destination_parent,
            self.destination_path,
            self.local_dir
        ))

def ui_print(text, tk_root_obj, ui_text_obj):
    if tk_root_obj is None or ui_text_obj is None:
        return
    ui_text_obj.set(str(text))
    tk_root_obj.update()

def delete_path(path):
    path = Path(path)
    try:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.is_file():
            path.unlink()
    except Exception as e:
        print("delete_path:", e)

import zipfile

def zip_directory(source_dir_path, output_zip_path):
    top_level_folder_name = os.path.basename(os.path.normpath(source_dir_path))
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, start=source_dir_path)
                arcname = os.path.join(top_level_folder_name, relative_path)
                zipf.write(file_path, arcname)

import platform
import subprocess
def open_directory_in_file_browser(path):
    system = platform.system()
    if system == 'Windows':
        os.startfile(path)
    elif system == 'Darwin':  # macOS
        subprocess.run(['open', path])
    elif system == 'Linux':
        subprocess.run(['xdg-open', path])

import zipfile

MAX_TOTAL_UNCOMPRESSED_SIZE = 10 * 1024 * 1024  # 50 MB
MAX_FILE_COUNT = 256
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB

def is_safe_path(base_path, target_path):
    # Prevent path traversal
    return os.path.realpath(target_path).startswith(os.path.realpath(base_path))

def reset_directory(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)

def unzip_to_own_directory(zip_file_path, output_dir_path):
    reset_directory(output_dir_path)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        infos = zip_ref.infolist()
        if len(infos) > MAX_FILE_COUNT:
            raise Exception("Too many files in zip archive")

        total_uncompressed_size = sum(info.file_size for info in infos)
        if total_uncompressed_size > MAX_TOTAL_UNCOMPRESSED_SIZE:
            raise Exception("Uncompressed size too large")

        for info in infos:
            if info.file_size > MAX_FILE_SIZE:
                raise Exception(f"File {info.filename} is too large")

            extracted_path = os.path.join(output_dir_path, info.filename)
            if not is_safe_path(output_dir_path, extracted_path):
                raise Exception(f"Unsafe file path detected: {info.filename}")

            zip_ref.extract(info, output_dir_path)

def get_profile_dir(dir_path):
    if not os.path.isdir(dir_path):
        return None
    for entry in os.listdir(dir_path):
        full_path = os.path.join(dir_path, entry)
        if os.path.isdir(full_path) and entry.startswith("profile"):
            return full_path
    return None

# unzip_to_own_directory("duckyPad_Profile_Photoshop.zip", "output")