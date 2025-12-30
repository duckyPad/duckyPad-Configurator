from enum import IntEnum
from dataclasses import dataclass
import struct
import keyword

DSVM_VERSION = 2

kw_REPEAT = "REPEAT"
kw_REM = "REM"
kw_C_COMMENT = "//"

kw_PEEK8 = "PEEK8"
kw_POKE8 = "POKE8" # POKE8(addr, val)
kw_RANDCHR = "RANDCHR"
kw_RANDINT = "RANDINT"
kw_PUTS = "PUTS"
kw_BUZZ = "BUZZ"

kw_RANDOM_LOWERCASE_LETTER = "RANDOM_LOWERCASE_LETTER"
kw_RANDOM_UPPERCASE_LETTER = "RANDOM_UPPERCASE_LETTER"
kw_RANDOM_LETTER = "RANDOM_LETTER"
kw_RANDOM_NUMBER = "RANDOM_NUMBER"
kw_RANDOM_SPECIAL = "RANDOM_SPECIAL"
kw_RANDOM_CHAR = "RANDOM_CHAR"

kw_DEFAULTDELAY = "DEFAULTDELAY"
kw_DEFAULTCHARDELAY = "DEFAULTCHARDELAY"
kw_CHARJITTER = "CHARJITTER"
kw_DELAY = "DELAY"
kw_STRING = "STRING"
kw_STRINGLN = "STRINGLN"

kw_LOOP = "LOOP"
kw_DP_SLEEP = "DP_SLEEP"
kw_PREV_PROFILE = "PREV_PROFILE"
kw_NEXT_PROFILE = "NEXT_PROFILE"
kw_GOTO_PROFILE = "GOTO_PROFILE"
kw_SKIP_PROFILE = "SKIP_PROFILE"

kw_KEYDOWN = "KEYDOWN"
kw_KEYUP = "KEYUP"
kw_INJECT_MOD = "INJECT_MOD"

kw_SWCOLOR = "SWCOLOR"
kw_SWCC = "SWC_SET"
kw_SWCF = "SWC_FILL"
kw_SWCR = "SWC_RESET"

kw_OLED_PRINT = "OLED_PRINT"
kw_OLED_UPDATE = "OLED_UPDATE"
kw_OLED_CURSOR = "OLED_CURSOR"
kw_OLED_CLEAR = "OLED_CLEAR"
kw_OLED_RESTORE = "OLED_RESTORE"

kw_OLED_LINE = "OLED_LINE"
kw_OLED_RECT = "OLED_RECT"
kw_OLED_CIRCLE = "OLED_CIRCLE"

kw_BCLR = "BCLR"

kw_LMOUSE = "LMOUSE"
kw_RMOUSE = "RMOUSE"
kw_MMOUSE = "MMOUSE"
kw_MOUSE_MOVE = "MOUSE_MOVE"
kw_MOUSE_WHEEL = "MOUSE_WHEEL"

kw_VAR_DECLARE = "VAR"
kw_VAR_PREFIX = "$"
kw_DEFINE = "DEFINE"

kw_IF = "IF"
kw_THEN = 'THEN'
kw_ELSE_IF = "ELSE IF"
kw_END_IF = "END_IF"
kw_ELSE = "ELSE"

kw_WHILE = "WHILE"
kw_END_WHILE = "END_WHILE"

kw_FUNCTION = "FUNCTION"
kw_END_FUNCTION = "END_FUNCTION"
kw_FUN = "FUN"
kw_END_FUN = "END_FUN"

kw_RETURN = "RETURN"
kw_HALT = "HALT"

kw_ESCAPE = "ESCAPE"
kw_ESC = "ESC"
kw_ENTER = "ENTER"
kw_UP = "UP"
kw_DOWN = "DOWN"
kw_LEFT = "LEFT"
kw_RIGHT = "RIGHT"
kw_UPARROW = "UPARROW"
kw_DOWNARROW = "DOWNARROW"
kw_LEFTARROW = "LEFTARROW"
kw_RIGHTARROW = "RIGHTARROW"
kw_BACKSPACE = "BACKSPACE"
kw_TAB = "TAB"
kw_CAPSLOCK = "CAPSLOCK"
kw_PRINTSCREEN = "PRINTSCREEN"
kw_SCROLLLOCK = "SCROLLLOCK"
kw_PAUSE = "PAUSE"
kw_BREAK = "BREAK"
kw_INSERT = "INSERT"
kw_HOME = "HOME"
kw_PAGEUP = "PAGEUP"
kw_PAGEDOWN = "PAGEDOWN"
kw_DELETE = "DELETE"
kw_END = "END"
kw_SPACE = "SPACE"

kw_SHIFT = "SHIFT"
kw_RSHIFT = "RSHIFT"

kw_ALT = "ALT"
kw_RALT = "RALT"
kw_OPTION = "OPTION"
kw_ROPTION = "ROPTION"

kw_GUI = "GUI"
kw_WINDOWS = "WINDOWS"
kw_COMMAND = "COMMAND"
kw_RWINDOWS = "RWINDOWS"
kw_RCOMMAND = "RCOMMAND"

kw_CONTROL = "CONTROL"
kw_CTRL = "CTRL"
kw_RCONTROL = "RCONTROL"
kw_RCTRL = "RCTRL"

kw_NUMLOCK = "NUMLOCK" # Keyboard Num Lock and Clear
kw_KPSLASH = "KP_SLASH" # Keypad /
kw_KPASTERISK = "KP_ASTERISK" # Keypad *
kw_KPMINUS = "KP_MINUS" # Keypad -
kw_KPPLUS = "KP_PLUS" # Keypad +
kw_KPENTER = "KP_ENTER" # Keypad ENTER
kw_KP1 = "KP_1" # Keypad 1 and End
kw_KP2 = "KP_2" # Keypad 2 and Down Arrow
kw_KP3 = "KP_3" # Keypad 3 and PageDn
kw_KP4 = "KP_4" # Keypad 4 and Left Arrow
kw_KP5 = "KP_5" # Keypad 5
kw_KP6 = "KP_6" # Keypad 6 and Right Arrow
kw_KP7 = "KP_7" # Keypad 7 and Home
kw_KP8 = "KP_8" # Keypad 8 and Up Arrow
kw_KP9 = "KP_9" # Keypad 9 and Page Up
kw_KP0 = "KP_0" # Keypad 0 and Insert
kw_KPDOT = "KP_DOT" # Keypad . and Delete
kw_KPEQUAL = "KP_EQUAL" # Keypad EQUAL

kw_MK_VOLUP = "MK_VOLUP"
kw_MK_VOLDOWN = "MK_VOLDOWN"
kw_MK_VOLMUTE = "MK_MUTE"
kw_MK_PREV = "MK_PREV"
kw_MK_NEXT = "MK_NEXT"
kw_MK_PLAYPAUSE = "MK_PP"
kw_MK_STOP = "MK_STOP"

kw_KATAKANAHIRAGANA = "KATAKANAHIRAGANA"
kw_HENKAN = "HENKAN"
kw_MUHENKAN = "MUHENKAN"
kw_KATAKANA = "KATAKANA"
kw_HIRAGANA = "HIRAGANA"
kw_ZENKAKUHANKAKU = "ZENKAKUHANKAKU"

kw_MENU = "MENU"
kw_APP = "APP"
kw_POWER = "POWER"

kw_LOOP_BREAK = "LBREAK"
kw_CONTINUE = "CONTINUE"

kw_REM_BLOCK = "REM_BLOCK"
kw_END_REM = "END_REM"

kw_STRINGLN_BLOCK = "STRINGLN_BLOCK"
kw_END_STRINGLN = "END_STRINGLN"

kw_STRING_BLOCK = "STRING_BLOCK"
kw_END_STRING = "END_STRING"

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
KEY_TYPE_MOUSE_BUTTON = 11

# name: (code, type)
ds_hid_keyname_dict = {

kw_LMOUSE : (1, KEY_TYPE_MOUSE_BUTTON),
kw_RMOUSE : (2, KEY_TYPE_MOUSE_BUTTON),
kw_MMOUSE : (4, KEY_TYPE_MOUSE_BUTTON),
kw_UP : (KEY_UP_ARROW, KEY_TYPE_SPECIAL),
kw_DOWN : (KEY_DOWN_ARROW, KEY_TYPE_SPECIAL),
kw_LEFT : (KEY_LEFT_ARROW, KEY_TYPE_SPECIAL),
kw_RIGHT : (KEY_RIGHT_ARROW, KEY_TYPE_SPECIAL),
kw_UPARROW : (KEY_UP_ARROW, KEY_TYPE_SPECIAL),
kw_DOWNARROW : (KEY_DOWN_ARROW, KEY_TYPE_SPECIAL),
kw_LEFTARROW : (KEY_LEFT_ARROW, KEY_TYPE_SPECIAL),
kw_RIGHTARROW : (KEY_RIGHT_ARROW, KEY_TYPE_SPECIAL),
kw_ESCAPE : (KEY_ESC, KEY_TYPE_SPECIAL),
kw_ESC : (KEY_ESC, KEY_TYPE_SPECIAL),
kw_ENTER : (KEY_RETURN, KEY_TYPE_SPECIAL),
kw_BACKSPACE : (KEY_BACKSPACE, KEY_TYPE_SPECIAL),
kw_TAB : (KEY_TAB, KEY_TYPE_SPECIAL),
kw_CAPSLOCK : (KEY_CAPS_LOCK, KEY_TYPE_SPECIAL),
kw_PRINTSCREEN : (KEY_PRINT_SCREEN, KEY_TYPE_SPECIAL),
kw_SCROLLLOCK : (KEY_SCROLL_LOCK, KEY_TYPE_SPECIAL),
kw_PAUSE : (KEY_PAUSE, KEY_TYPE_SPECIAL),
kw_BREAK : (KEY_PAUSE, KEY_TYPE_SPECIAL),
kw_INSERT : (KEY_INSERT, KEY_TYPE_SPECIAL),
kw_HOME : (KEY_HOME, KEY_TYPE_SPECIAL),
kw_PAGEUP : (KEY_PAGE_UP, KEY_TYPE_SPECIAL),
kw_PAGEDOWN : (KEY_PAGE_DOWN, KEY_TYPE_SPECIAL),
kw_DELETE : (KEY_DELETE, KEY_TYPE_SPECIAL),
kw_END : (KEY_END, KEY_TYPE_SPECIAL),
kw_NUMLOCK : (KEY_NUMLOCK, KEY_TYPE_SPECIAL),
kw_KPSLASH : (KEY_KPSLASH, KEY_TYPE_SPECIAL),
kw_KPASTERISK : (KEY_KPASTERISK, KEY_TYPE_SPECIAL),
kw_KPMINUS : (KEY_KPMINUS, KEY_TYPE_SPECIAL),
kw_KPPLUS : (KEY_KPPLUS, KEY_TYPE_SPECIAL),
kw_KPENTER : (KEY_KPENTER, KEY_TYPE_SPECIAL),
kw_KP1 : (KEY_KP1, KEY_TYPE_SPECIAL),
kw_KP2 : (KEY_KP2, KEY_TYPE_SPECIAL),
kw_KP3 : (KEY_KP3, KEY_TYPE_SPECIAL),
kw_KP4 : (KEY_KP4, KEY_TYPE_SPECIAL),
kw_KP5 : (KEY_KP5, KEY_TYPE_SPECIAL),
kw_KP6 : (KEY_KP6, KEY_TYPE_SPECIAL),
kw_KP7 : (KEY_KP7, KEY_TYPE_SPECIAL),
kw_KP8 : (KEY_KP8, KEY_TYPE_SPECIAL),
kw_KP9 : (KEY_KP9, KEY_TYPE_SPECIAL),
kw_KP0 : (KEY_KP0, KEY_TYPE_SPECIAL),
kw_KPDOT : (KEY_KPDOT, KEY_TYPE_SPECIAL),
kw_KPEQUAL : (KEY_KPEQUAL, KEY_TYPE_SPECIAL),
kw_POWER : (KEY_POWER, KEY_TYPE_SPECIAL),
kw_MENU : (KEY_MENU, KEY_TYPE_SPECIAL),
kw_APP : (KEY_MENU, KEY_TYPE_SPECIAL),
kw_KATAKANAHIRAGANA : (KEY_KATAKANAHIRAGANA, KEY_TYPE_SPECIAL),
kw_HENKAN : (KEY_HENKAN, KEY_TYPE_SPECIAL),
kw_MUHENKAN : (KEY_MUHENKAN, KEY_TYPE_SPECIAL),
kw_KATAKANA : (KEY_KATAKANA, KEY_TYPE_SPECIAL),
kw_HIRAGANA : (KEY_HIRAGANA, KEY_TYPE_SPECIAL),
kw_ZENKAKUHANKAKU : (KEY_ZENKAKUHANKAKU, KEY_TYPE_SPECIAL),
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
kw_SPACE : (0x20, KEY_TYPE_CHAR),
kw_SHIFT : (KEY_LEFT_SHIFT, KEY_TYPE_MODIFIER),
kw_RSHIFT : (KEY_RIGHT_SHIFT, KEY_TYPE_MODIFIER),
kw_ALT : (KEY_LEFT_ALT, KEY_TYPE_MODIFIER),
kw_OPTION : (KEY_LEFT_ALT, KEY_TYPE_MODIFIER),
kw_RALT : (KEY_RIGHT_ALT, KEY_TYPE_MODIFIER),
kw_ROPTION : (KEY_RIGHT_ALT, KEY_TYPE_MODIFIER),
kw_GUI : (KEY_LEFT_GUI, KEY_TYPE_MODIFIER),
kw_WINDOWS : (KEY_LEFT_GUI, KEY_TYPE_MODIFIER),
kw_RWINDOWS : (KEY_RIGHT_GUI, KEY_TYPE_MODIFIER),
kw_COMMAND : (KEY_LEFT_GUI, KEY_TYPE_MODIFIER),
kw_RCOMMAND : (KEY_RIGHT_GUI, KEY_TYPE_MODIFIER),
kw_CTRL : (KEY_LEFT_CTRL, KEY_TYPE_MODIFIER),
kw_CONTROL : (KEY_LEFT_CTRL, KEY_TYPE_MODIFIER),
kw_RCTRL : (KEY_RIGHT_CTRL, KEY_TYPE_MODIFIER),
kw_RCONTROL : (KEY_RIGHT_CTRL, KEY_TYPE_MODIFIER),
kw_MK_VOLUP : (KEY_MK_VOLUP, KEY_TYPE_MEDIA),
kw_MK_VOLDOWN : (KEY_MK_VOLDOWN, KEY_TYPE_MEDIA),
kw_MK_VOLMUTE : (KEY_MK_VOLMUTE, KEY_TYPE_MEDIA),
kw_MK_PREV : (KEY_MK_PREV, KEY_TYPE_MEDIA),
kw_MK_NEXT : (KEY_MK_NEXT, KEY_TYPE_MEDIA),
kw_MK_PLAYPAUSE : (KEY_MK_PLAYPAUSE, KEY_TYPE_MEDIA),
kw_MK_STOP : (KEY_MK_STOP, KEY_TYPE_MEDIA),
}

class SymType(IntEnum):
    GLOBAL_VAR = 0
    FUNC_ARG = 1
    FUNC_LOCAL_VAR = 2
    RESERVED_VAR = 3

@dataclass(frozen=True, slots=True)
class var_info:
    name: str
    type: SymType
    func: str

@dataclass(frozen=True, slots=True)
class Opcode:
    name: str
    code: int
    length: int
    is_virtual: bool = False

@dataclass(slots=True)
class fun_info:
    name: str
    args: set
    locals: set

@dataclass(slots=True)
class compile_result:
    is_success: bool = False
    error_comment: str = ""
    error_line_number_starting_from_1 : int = 0
    error_line_str: str = ""
    bin_array : bytes = bytes()

# CPU instructions
OP_NOP = Opcode("NOP", 0, 1)
OP_PUSHC16 = Opcode("PUSHC16", 1, 3)
OP_PUSHI = Opcode("PUSHI", 2, 3)
OP_PUSHR = Opcode("PUSHR", 3, 3)
OP_POPI = Opcode("POPI", 4, 3)
OP_POPR = Opcode("POPR", 5, 3)
OP_BRZ = Opcode("BRZ", 6, 3)
OP_JMP = Opcode("JMP", 7, 3)
OP_ALLOC = Opcode("ALLOC", 8, 3)
OP_CALL = Opcode("CALL", 9, 3)
OP_RET = Opcode("RET", 10, 3)
OP_HALT = Opcode("HALT", 11, 1)
OP_PEEK8 = Opcode("PEEK8", 12, 1)
OP_POKE8 = Opcode("POKE8", 13, 1)
OP_PUSH0 = Opcode("PUSH0", 14, 1)
OP_PUSH1 = Opcode("PUSH1", 15, 1)
OP_DROP = Opcode("DROP", 16, 1)
OP_DUP = Opcode("DUP", 17, 1)
OP_RANDINT = Opcode("RANDINT", 18, 1)
OP_PUSHC32 = Opcode("PUSHC32", 19, 5)
OP_VMVER = Opcode("VMVER", 255, 3)

# Binary Operators
OP_EQ = Opcode("EQ", 32, 1)
OP_NOTEQ = Opcode("NOTEQ", 33, 1)
OP_LT = Opcode("LT", 34, 1)
OP_LTE = Opcode("LTE", 35, 1)
OP_GT = Opcode("GT", 36, 1)
OP_GTE = Opcode("GTE", 37, 1)
OP_ADD = Opcode("ADD", 38, 1)
OP_SUB = Opcode("SUB", 39, 1)
OP_MULT = Opcode("MULT", 40, 1)
OP_DIV = Opcode("DIV", 41, 1)
OP_MOD = Opcode("MOD", 42, 1)
OP_POW = Opcode("POW", 43, 1)
OP_LSHIFT = Opcode("LSHIFT", 44, 1)
OP_RSHIFT = Opcode("RSHIFT", 45, 1)
OP_BITOR = Opcode("BITOR", 46, 1)
OP_BITXOR = Opcode("BITXOR", 47, 1)
OP_BITAND = Opcode("BITAND", 48, 1)
OP_LOGIAND = Opcode("LOGIAND", 49, 1)
OP_LOGIOR = Opcode("LOGIOR", 50, 1)

# Unary Operators
OP_BITINV = Opcode("BITINV", 55, 1)
OP_LOGINOT = Opcode("LOGINOT", 56, 1)
OP_USUB = Opcode("USUB", 57, 1)

# duckyScript Commands
OP_DELAY = Opcode("DELAY", 64, 1)
OP_KDOWN = Opcode("KDOWN", 65, 1)
OP_KUP = Opcode("KUP", 66, 1)
OP_MSCL = Opcode("MSCL", 67, 1)
OP_MMOV = Opcode("MMOV", 68, 1)
OP_SWCF = Opcode("SWCF", 69, 1)
OP_SWCC = Opcode("SWCC", 70, 1)
OP_SWCR = Opcode("SWCR", 71, 1)
OP_STR = Opcode("STR", 72, 1)
OP_STRLN = Opcode("STRLN", 73, 1)
OP_OLED_CUSR = Opcode("OLED_CUSR", 74, 1)
OP_OLED_PRNT = Opcode("OLED_PRNT", 75, 1)
OP_OLED_UPDE = Opcode("OLED_UPDE", 76, 1)
OP_OLED_CLR = Opcode("OLED_CLR", 77, 1)
OP_OLED_REST = Opcode("OLED_REST", 78, 1)
OP_OLED_LINE = Opcode("OLED_LINE", 79, 1)
OP_OLED_RECT = Opcode("OLED_RECT", 80, 1)
OP_OLED_CIRC = Opcode("OLED_CIRC", 81, 1)
OP_BCLR = Opcode("BCLR", 82, 1)
OP_SKIPP = Opcode("SKIPP", 83, 1)
OP_GOTOP = Opcode("GOTOP", 84, 1)
OP_SLEEP = Opcode("SLEEP", 85, 1)
OP_RANDCHR = Opcode("RANDCHR", 86, 1)
OP_PUTS = Opcode("PUTS", 87, 1)
OP_PWMCTRL = Opcode("PWMCTRL", 88, 1)

# Virtual Opcodes, to be resolved during compilation
OP_PUSHSTR = Opcode("PUSHSTR", 128, 3, is_virtual=True)

MEM_END_ADDR = 0xFFFF
USER_VAR_START_ADDRESS = 0xF800
USER_VAR_BYTE_WIDTH = 4
USER_VAR_END_ADDRESS_INCLUSIVE = 0xF9FF
MAX_UDV_COUNT = (USER_VAR_END_ADDRESS_INCLUSIVE - USER_VAR_START_ADDRESS + 1) // USER_VAR_BYTE_WIDTH

PGV_COUNT = 32
PGV_START_ADDRESS = 0xFD00
PGV_BYTE_WIDTH = 4
PGV_END_ADDRESS_INCLUSIVE = 0xFDFF

INTERAL_VAR_START_ADDRESS = 0xFE00
INTERAL_VAR_BYTE_WIDTH = 4
INTERAL_VAR_END_ADDRESS_INCLUSIVE = MEM_END_ADDR
OP_DROP_REPLACEMENT_ADDR = MEM_END_ADDR

STACK_BASE_ADDR = 0xF7FF
MIN_STACK_SIZE_BYTES = 512
STACK_MOAT_BYTES = 32
MAX_BIN_SIZE = STACK_BASE_ADDR - MIN_STACK_SIZE_BYTES - STACK_MOAT_BYTES
DUMMY_VAR_NAME = "_DSVM_DUMMY"

reserved_variables_dict = {
    '_DEFAULTDELAY': (INTERAL_VAR_START_ADDRESS + 0 * INTERAL_VAR_BYTE_WIDTH),
    '_DEFAULTCHARDELAY': (INTERAL_VAR_START_ADDRESS + 1 * INTERAL_VAR_BYTE_WIDTH),
    '_CHARJITTER': (INTERAL_VAR_START_ADDRESS + 2 * INTERAL_VAR_BYTE_WIDTH),
    "_RANDOM_MIN": (INTERAL_VAR_START_ADDRESS + 3 * INTERAL_VAR_BYTE_WIDTH),
    "_RANDOM_MAX": (INTERAL_VAR_START_ADDRESS + 4 * INTERAL_VAR_BYTE_WIDTH),
    "_RANDOM_INT": (INTERAL_VAR_START_ADDRESS + 5 * INTERAL_VAR_BYTE_WIDTH),
    "_TIME_MS": (INTERAL_VAR_START_ADDRESS + 6 * INTERAL_VAR_BYTE_WIDTH),
    "_READKEY": (INTERAL_VAR_START_ADDRESS + 7 * INTERAL_VAR_BYTE_WIDTH),
    "_LOOP_SIZE": (INTERAL_VAR_START_ADDRESS + 8 * INTERAL_VAR_BYTE_WIDTH),
    "_KEYPRESS_COUNT": (INTERAL_VAR_START_ADDRESS + 9 * INTERAL_VAR_BYTE_WIDTH),
    "_EPILOGUE_ACTIONS": (INTERAL_VAR_START_ADDRESS + 10 * INTERAL_VAR_BYTE_WIDTH),
    "_TIME_S": (INTERAL_VAR_START_ADDRESS + 11 * INTERAL_VAR_BYTE_WIDTH),
    "_ALLOW_ABORT": (INTERAL_VAR_START_ADDRESS + 12 * INTERAL_VAR_BYTE_WIDTH),
    "_BLOCKING_READKEY": (INTERAL_VAR_START_ADDRESS + 13 * INTERAL_VAR_BYTE_WIDTH),
    "_IS_NUMLOCK_ON": (INTERAL_VAR_START_ADDRESS + 14 * INTERAL_VAR_BYTE_WIDTH),
    "_IS_CAPSLOCK_ON": (INTERAL_VAR_START_ADDRESS + 15 * INTERAL_VAR_BYTE_WIDTH),
    "_IS_SCROLLLOCK_ON": (INTERAL_VAR_START_ADDRESS + 16 * INTERAL_VAR_BYTE_WIDTH),
    "_DONT_REPEAT": (INTERAL_VAR_START_ADDRESS + 17 * INTERAL_VAR_BYTE_WIDTH),
    "_THIS_KEYID": (INTERAL_VAR_START_ADDRESS + 18 * INTERAL_VAR_BYTE_WIDTH),
    "_DP_MODEL": (INTERAL_VAR_START_ADDRESS + 19 * INTERAL_VAR_BYTE_WIDTH),
    "_RTC_IS_VALID": (INTERAL_VAR_START_ADDRESS + 20 * INTERAL_VAR_BYTE_WIDTH),
    "_RTC_UTC_OFFSET": (INTERAL_VAR_START_ADDRESS + 21 * INTERAL_VAR_BYTE_WIDTH),
    "_RTC_YEAR": (INTERAL_VAR_START_ADDRESS + 22 * INTERAL_VAR_BYTE_WIDTH),
    "_RTC_MONTH": (INTERAL_VAR_START_ADDRESS + 23 * INTERAL_VAR_BYTE_WIDTH),
    "_RTC_DAY": (INTERAL_VAR_START_ADDRESS + 24 * INTERAL_VAR_BYTE_WIDTH),
    "_RTC_HOUR": (INTERAL_VAR_START_ADDRESS + 25 * INTERAL_VAR_BYTE_WIDTH),
    "_RTC_MINUTE": (INTERAL_VAR_START_ADDRESS + 26 * INTERAL_VAR_BYTE_WIDTH),
    "_RTC_SECOND": (INTERAL_VAR_START_ADDRESS + 27 * INTERAL_VAR_BYTE_WIDTH),
    "_RTC_WDAY": (INTERAL_VAR_START_ADDRESS + 28 * INTERAL_VAR_BYTE_WIDTH),
    "_RTC_YDAY": (INTERAL_VAR_START_ADDRESS + 29 * INTERAL_VAR_BYTE_WIDTH),
    "_UNSIGNED_MATH": (INTERAL_VAR_START_ADDRESS + 30 * INTERAL_VAR_BYTE_WIDTH),
    "_SW_BITFIELD": (INTERAL_VAR_START_ADDRESS + 31 * INTERAL_VAR_BYTE_WIDTH),
    
    "_GV0": (PGV_START_ADDRESS + 0 * PGV_BYTE_WIDTH),
    "_GV1": (PGV_START_ADDRESS + 1 * PGV_BYTE_WIDTH),
    "_GV2": (PGV_START_ADDRESS + 2 * PGV_BYTE_WIDTH),
    "_GV3": (PGV_START_ADDRESS + 3 * PGV_BYTE_WIDTH),
    "_GV4": (PGV_START_ADDRESS + 4 * PGV_BYTE_WIDTH),
    "_GV5": (PGV_START_ADDRESS + 5 * PGV_BYTE_WIDTH),
    "_GV6": (PGV_START_ADDRESS + 6 * PGV_BYTE_WIDTH),
    "_GV7": (PGV_START_ADDRESS + 7 * PGV_BYTE_WIDTH),
    "_GV8": (PGV_START_ADDRESS + 8 * PGV_BYTE_WIDTH),
    "_GV9": (PGV_START_ADDRESS + 9 * PGV_BYTE_WIDTH),
    "_GV10": (PGV_START_ADDRESS + 10 * PGV_BYTE_WIDTH),
    "_GV11": (PGV_START_ADDRESS + 11 * PGV_BYTE_WIDTH),
    "_GV12": (PGV_START_ADDRESS + 12 * PGV_BYTE_WIDTH),
    "_GV13": (PGV_START_ADDRESS + 13 * PGV_BYTE_WIDTH),
    "_GV14": (PGV_START_ADDRESS + 14 * PGV_BYTE_WIDTH),
    "_GV15": (PGV_START_ADDRESS + 15 * PGV_BYTE_WIDTH),
    "_GV16": (PGV_START_ADDRESS + 16 * PGV_BYTE_WIDTH),
    "_GV17": (PGV_START_ADDRESS + 17 * PGV_BYTE_WIDTH),
    "_GV18": (PGV_START_ADDRESS + 18 * PGV_BYTE_WIDTH),
    "_GV19": (PGV_START_ADDRESS + 19 * PGV_BYTE_WIDTH),
    "_GV20": (PGV_START_ADDRESS + 20 * PGV_BYTE_WIDTH),
    "_GV21": (PGV_START_ADDRESS + 21 * PGV_BYTE_WIDTH),
    "_GV22": (PGV_START_ADDRESS + 22 * PGV_BYTE_WIDTH),
    "_GV23": (PGV_START_ADDRESS + 23 * PGV_BYTE_WIDTH),
    "_GV24": (PGV_START_ADDRESS + 24 * PGV_BYTE_WIDTH),
    "_GV25": (PGV_START_ADDRESS + 25 * PGV_BYTE_WIDTH),
    "_GV26": (PGV_START_ADDRESS + 26 * PGV_BYTE_WIDTH),
    "_GV27": (PGV_START_ADDRESS + 27 * PGV_BYTE_WIDTH),
    "_GV28": (PGV_START_ADDRESS + 28 * PGV_BYTE_WIDTH),
    "_GV29": (PGV_START_ADDRESS + 29 * PGV_BYTE_WIDTH),
    "_GV30": (PGV_START_ADDRESS + 30 * PGV_BYTE_WIDTH),
    "_GV31": (PGV_START_ADDRESS + 31 * PGV_BYTE_WIDTH),

    DUMMY_VAR_NAME: OP_DROP_REPLACEMENT_ADDR,
}

class ds_line:
    def __init__(self, content, orig_lnum_sf1=0, indent_lvl=0):
        self.orig_lnum_sf1 = orig_lnum_sf1
        self.content = content
        self.py_lnum_sf1 = None
        self.indent_level = indent_lvl

    def __repr__(self):
        return f"ds_line({self.content!r}, ogl={self.orig_lnum_sf1!r}, pyl={self.py_lnum_sf1!r})"

PARSE_OK = 0
PARSE_ERROR = 1

english_alphabets = [
'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
'A', 'B', 'C', 'D', 'E','F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

valid_var_chars = set(['0', '1', '2', '3', '4', '5', '6', '7','8', '9', '_'] + english_alphabets)
english_alphabets = set(english_alphabets)

valid_combo_chars = {'!', '"', '#', '$', '%', '&', "'", '(',
')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
'8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~'}

STRING_MAX_SIZE = 256
REPEAT_MAX_SIZE = 256

@dataclass(frozen=True, slots=True)
class reserved_func_info:
    opcode: Opcode
    arg_len: int
    has_return_value: bool = False

ds_str_func_lookup = {
    kw_STRING : reserved_func_info(OP_STR, 1),
    kw_STRINGLN : reserved_func_info(OP_STRLN, 1),
    kw_OLED_PRINT : reserved_func_info(OP_OLED_PRNT, 1),
    kw_GOTO_PROFILE : reserved_func_info(OP_GOTOP, 1),
    }

ds_keypress_func_lookup = {
    kw_KEYDOWN : reserved_func_info(OP_KDOWN, 1),
    kw_KEYUP : reserved_func_info(OP_KUP, 1),
}

ds_builtin_func_lookup = {
    kw_HALT : reserved_func_info(OP_HALT, 0),
    kw_DELAY : reserved_func_info(OP_DELAY, 1),
    kw_MOUSE_WHEEL : reserved_func_info(OP_MSCL, 1),
    kw_MOUSE_MOVE : reserved_func_info(OP_MMOV, 2),
    kw_SWCF : reserved_func_info(OP_SWCF, 3),
    kw_SWCC : reserved_func_info(OP_SWCC, 4),
    kw_SWCR : reserved_func_info(OP_SWCR, 1),
    kw_OLED_CURSOR : reserved_func_info(OP_OLED_CUSR, 2),
    kw_OLED_UPDATE : reserved_func_info(OP_OLED_UPDE, 0),
    kw_OLED_CLEAR : reserved_func_info(OP_OLED_CLR, 0),
    kw_OLED_RESTORE : reserved_func_info(OP_OLED_REST, 0),
    kw_OLED_LINE : reserved_func_info(OP_OLED_LINE, 4),
    kw_OLED_RECT : reserved_func_info(OP_OLED_RECT, 5),
    kw_OLED_CIRCLE : reserved_func_info(OP_OLED_CIRC, 4),
    kw_BCLR : reserved_func_info(OP_BCLR, 0),
    kw_SKIP_PROFILE : reserved_func_info(OP_SKIPP, 1),
    kw_DP_SLEEP : reserved_func_info(OP_SLEEP, 0),
    kw_PEEK8 : reserved_func_info(OP_PEEK8, 1, has_return_value=True),
    kw_POKE8 : reserved_func_info(OP_POKE8, 2),
    kw_RANDCHR : reserved_func_info(OP_RANDCHR, 1),
    kw_RANDINT : reserved_func_info(OP_RANDINT, 2, has_return_value=True),
    kw_PUTS : reserved_func_info(OP_PUTS, 1),
    kw_BUZZ : reserved_func_info(OP_PWMCTRL, 1),
}

ds_func_to_parse_as_str = ds_str_func_lookup | ds_keypress_func_lookup

ds_reserved_funcs = ds_func_to_parse_as_str | ds_builtin_func_lookup 

ds2py_ignored_cmds = {kw_END_IF, kw_END_WHILE, kw_END_FUNCTION, kw_END_FUN}

def get_pretty_ds_line_list(dslist):
    lines = []
    for item in dslist:
        lines.append("    "*item.indent_level + item.content)
    return lines

def print_ds_line_list(dslist):
    print("OG PY")
    for item in dslist:
        print(f"{item.orig_lnum_sf1:02} {item.py_lnum_sf1:02} {"    "*item.indent_level} {item.content}")

def save_lines_to_file(dslist, filename):
    line_list = get_pretty_ds_line_list(dslist)
    with open(filename, "w") as file:
        file.writelines(line + "\n" for line in line_list)

def dsline_to_source(dslist):
    result = ""
    lines = get_pretty_ds_line_list(dslist)
    for line in lines:
        result += f"{line}\n"
    return result

class dsvm_instruction:
    LABEL_PREFIX = "~~~~"
    ADDR_WIDTH = 5
    OPCODE_WIDTH = 10
    PAYLOAD_STR_MAX = 14
    PAYLOAD_FIELD_WIDTH = 12
    PAYLOAD_BLOCK_WIDTH = 24
    COMMENT_MAX = 32

    def __init__(self,\
                opcode=OP_NOP,\
                payload=None,\
                label=None,\
                comment='',\
                addr=None,\
                parent_func=None,\
                var_type=None,\
                ):
        self.opcode = opcode
        self.payload = payload
        self.label = label
        self.comment = comment
        self.addr = addr
        self.parent_func = parent_func
        self.var_type = var_type

    def __str__(self) -> str:
        lines = []

        if self.label:
            lines.append(f"{self.LABEL_PREFIX}{self.label}:")

        parts = []
        if self.addr is not None:
            parts.append(str(self.addr).ljust(self.ADDR_WIDTH))

        parts.append(self.opcode.name.ljust(self.OPCODE_WIDTH))

        # payload section
        payload_block = ""
        payload = self.payload
        if payload is not None:
            if isinstance(payload, str) and len(payload) > self.PAYLOAD_STR_MAX:
                payload = f"{payload[:self.PAYLOAD_STR_MAX]}..."
            payload_block = f"{payload}".ljust(self.PAYLOAD_FIELD_WIDTH)
            if isinstance(payload, int):
                value_32bit = payload & 0xFFFFFFFF
                payload_block += f"0x{value_32bit:x}".ljust(self.PAYLOAD_FIELD_WIDTH)

        parts.append(payload_block.ljust(self.PAYLOAD_BLOCK_WIDTH))

        # comment section
        comment_items = []
        if self.comment:
            comment_items.append(str(self.comment).strip())

        comment = " | ".join(comment_items)
        comment_out = ""
        if len(comment) > self.COMMENT_MAX:
            comment_out = ";" + comment[:self.COMMENT_MAX] + "..."
        elif len(comment) > 0:
            comment_out = ";" + comment

        parts.append(comment_out)

        lines.append("".join(parts))
        return "\n".join(lines)

def get_orig_ds_lnumsf1_from_py_lnumsf1(rdict, this_pylnum_sf1, onerr=None):
    if this_pylnum_sf1 is None:
        return onerr
    og_index_sf1 = onerr
    for line_obj in rdict['ds2py_listing']:
        if line_obj.py_lnum_sf1 == this_pylnum_sf1:
            og_index_sf1 = line_obj.orig_lnum_sf1
            break
    return og_index_sf1

import uuid
notequal_str = "!="
op_placeholder = str(uuid.uuid4())

def replace_operators(this_line):
    if this_line.lstrip().startswith(kw_DEFINE):
        return this_line
    temp = this_line.replace(notequal_str, op_placeholder)
    temp = temp.replace(kw_VAR_PREFIX, "").replace("||", " or ").replace("&&", " and ").replace("!", " not ")
    temp = temp.replace(op_placeholder, notequal_str)
    return temp

def pack_to_two_bytes(value: int) -> bytes:
    if not isinstance(value, int):
        raise TypeError(f"Input must be an integer, but received {type(value)}")

    if value >= 0:
        # --- Handle as unsigned 16-bit integer (uint16_t) ---
        # Valid range: 0 to 65535 (2^16 - 1)
        max_uint16 = 65535
        if value > max_uint16:
            raise ValueError(
                f"Value {value} is too large for uint16_t. Max allowed is {max_uint16}."
            )
        
        # Format string '<H':
        # '<' - Little-endian
        # 'H' - unsigned short (2 bytes)
        format_string = '<H'
    
    else:
        # --- Handle as signed 16-bit integer (int16_t) in two's complement ---
        # Valid range: -32768 (-2^15) to 32767 (2^15 - 1)
        min_int16 = -32768
        max_int16 = 32767

        if not (min_int16 <= value <= max_int16):
            raise ValueError(
                f"Value {value} is outside the int16_t range. Range is {min_int16} to {max_int16}."
            )
        
        # Format string '<h':
        # '<' - Little-endian
        # 'h' - signed short (2 bytes)
        format_string = '<h'

    # The struct.pack function handles the conversion to two's complement 
    # for negative numbers automatically based on the format code 'h'.
    return struct.pack(format_string, value)

import struct

def pack_to_four_bytes(value: int) -> bytes:
    if not isinstance(value, int):
        raise TypeError(f"Input must be an integer, but received {type(value)}")

    if value >= 0:
        # --- Handle as unsigned 32-bit integer (uint32_t) ---
        max_uint32 = 4294967295  # 2^32 - 1
        if value > max_uint32:
            raise ValueError(
                f"Value {value} is too large for uint32_t. Max is {max_uint32}."
            )
        
        # '<I' : Little-endian, unsigned int (4 bytes)
        format_string = '<I'
    
    else:
        # --- Handle as signed 32-bit integer (int32_t) ---
        min_int32 = -2147483648
        max_int32 = 2147483647

        if not (min_int32 <= value <= max_int32):
            raise ValueError(
                f"Value {value} is outside the int32_t range."
            )
        
        # '<i' : Little-endian, signed int (4 bytes)
        format_string = '<i'

    return struct.pack(format_string, value)

def print_C_opcode_len_lookup():
    opcode_map = {
        obj.code: obj
        for obj in globals().values()
        if isinstance(obj, Opcode) and not obj.is_virtual
    }

    op_len_lookup_buf_size = 100
    print(f"#define OP_LEN_LOOKUP_SIZE {op_len_lookup_buf_size}")
    print("uint8_t opcode_len_lookup[OP_LEN_LOOKUP_SIZE] = {")
    for x in range(op_len_lookup_buf_size):
        if x not in opcode_map:
            print(f"255, // [{x}]")
            continue
        this_op = opcode_map[x]
        print(f"{this_op.length}, // [{x}] {this_op.name}")
    print("};")

def print_C_opcode_def():
    opcode_map = {
        obj.code: obj
        for obj in globals().values()
        if isinstance(obj, Opcode) and not obj.is_virtual
    }

    for x in range(256):
        if x not in opcode_map:
            continue
        this_op = opcode_map[x]
        print(f"#define OP_{this_op.name} {this_op.code}")

def generate_c_code():
    disclaimer = """
/*
  AUTO GENERATED BY 
  print_C_opcode_len_lookup()
  print_C_opcode_def()
  IN dsvm_common.py
*/
    """
    print(disclaimer)
    print_C_opcode_len_lookup()
    print()
    print_C_opcode_def()

def get_orig_ds_line_from_orig_ds_lnum_sf1(ctx_dict, lnumsf1):
    try:
        return ctx_dict['orig_listing'][lnumsf1-1].content
    except Exception as e:
        print("get_orig_ds_line_from_orig_ds_lnum_sf1:", e)
    return ""

ds_kw_set = {v for k, v in globals().items() if k.startswith('kw_')}

def is_ds_keyword(name):
    if keyword.iskeyword(name):
        return True
    if name in ds_kw_set:
        return True
    if name in ds_hid_keyname_dict:
        return True
    return False

if __name__ == "__main__":
    generate_c_code()
