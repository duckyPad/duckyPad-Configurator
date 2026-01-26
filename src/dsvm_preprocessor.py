import sys
from dsvm_common import *
import copy
import re

def needs_rstrip(first_word):
    if first_word == kw_STRING:
        return False
    if first_word == kw_STRINGLN:
        return False
    if first_word == kw_OLED_PRINT:
        return False
    return True

def replace_DEFINE_once(pgm_line, def_dict):
    if pgm_line.startswith(kw_STRING+" ") or pgm_line.startswith(kw_STRINGLN+" "):
        def_dict.pop("TRUE", None)
        def_dict.pop("FALSE", None)
    else:
        def_dict['TRUE'] = 1
        def_dict['FALSE'] = 0
    def_dict_list_longest_first = sorted(list(def_dict.keys()), key=len, reverse=True)
    for key in def_dict_list_longest_first:
        value = str(def_dict[key])
        pattern = r'\b' + re.escape(key) + r'\b'
        pgm_line, sub_count = re.subn(pattern, lambda _: value, pgm_line)
        if sub_count > 0:
            break
    return pgm_line

def replace_DEFINE(source, def_dict):
    last_source = ""
    iterations = 0
    max_iterations = max(512, len(def_dict)*2)
    while last_source != source:
        if iterations > max_iterations:
            raise ValueError("Recursive DEFINE")
        last_source = source
        source = replace_DEFINE_once(source, def_dict)
        iterations += 1
    return source

def skip_whitespace(pgm_line):
    whitespace_chars = [' ', '\t']
    search_index = len(kw_DEFINE)
    try:
        while 1:
            this_char = pgm_line[search_index]
            if this_char in whitespace_chars:
                search_index += 1
            else:
                return search_index
    except Exception:
        return -1
    return -1

def is_valid_var_name(varname):
    if len(varname) == 0:
        return False, 'Empty name'
    if varname[0].isnumeric():
        return False, f"Name can't begin with a number: {varname}"
    if is_ds_keyword(varname):
        return False, f"Invalid Variable Name: {varname}"
    for letter in varname:
        if letter not in valid_var_chars:
            return False, f'Name contains invalid characters: {varname}'
    return True, ''

def new_define(pgm_line, dd):
    pgm_line = pgm_line.rsplit(kw_C_COMMENT, 1)[0].rstrip()
    define_source_start = skip_whitespace(pgm_line)
    if define_source_start == -1:
        return PARSE_ERROR, "DEFINE content not found"
    segments = pgm_line[define_source_start:].split(' ', 1)
    if len(segments) != 2:
        return PARSE_ERROR, "empty DEFINE"
    define_source = segments[0]
    define_destination = segments[1]
    is_valid, comment = is_valid_var_name(define_source)
    if is_valid is False:
        return PARSE_ERROR, comment
    if define_source in dd and define_destination != dd[define_source]:
        return PARSE_ERROR, f"{define_source} is already defined"
    dd[define_source] = define_destination
    return PARSE_OK, ''

def check_loop(pgm_line):
    try:
        line_split = [x for x in pgm_line.split(kw_LOOP) if len(x) > 0]
        if ':' not in line_split[0]:
            return PARSE_ERROR, 'missing ":"', None
        number_split = [x for x in line_split[0].split(":") if len(x) > 0]
        if len(number_split) != 1:
            return PARSE_ERROR, "wrong number of arguments", None
        return PARSE_OK, "", int(number_split[0])
    except Exception as e:
        return PARSE_ERROR, str(e), None

def new_rem_block_check(lnum, rbss, rbdict):
    if len(rbss) != 0:
        return PARSE_ERROR, "unmatched END_REM"
    rbss.append(lnum)
    rbdict[lnum] = None
    return PARSE_OK, ''

def new_stringln_block_check(lnum, slbss, slbdict):
    if len(slbss) != 0:
        return PARSE_ERROR, "unmatched END_STRINGLN"
    slbss.append(lnum)
    slbdict[lnum] = None
    # print("new_stringln_block_check:", slbss, slbdict)
    return PARSE_OK, ''

def new_string_block_check(lnum, sbss, sbdict):
    if len(sbss) != 0:
        return PARSE_ERROR, "unmatched END_STRING"
    sbss.append(lnum)
    sbdict[lnum] = None
    return PARSE_OK, ''

def new_func_check(pgm_line, lnum, fss, fdict):
    if len(fss) != 0:
        return PARSE_ERROR, "unmatched END_FUN"
    if pgm_line.endswith(")") is False:
        return PARSE_ERROR, "missing )"
    try:
        fun_name = pgm_line.split()[1].split('(')[0]
    except Exception:
        return PARSE_ERROR, "invalid func name"
    if_valid_vn, vn_comment = is_valid_var_name(fun_name)
    if if_valid_vn is False:
        return PARSE_ERROR, vn_comment
    if fun_name in fdict:
        return PARSE_ERROR, "function already exists"
    try:
        all_args = pgm_line.split("(", 1)[-1].rsplit(")", 1)[0]
        # arg_list = [f"{FUNC_NAME_MANGLE_PREFIX}{fun_name}_{x.strip()}" for x in all_args.split(",")]
        arg_list = [x.strip() for x in all_args.split(",") if len(x.strip())]
    except Exception:
        return PARSE_ERROR, "Arg parse error"
    for arg in arg_list:
        is_valid, vn_comment = is_valid_var_name(arg)
        if is_valid is False:
            return PARSE_ERROR, vn_comment
    if len(arg_list) != len(set(arg_list)):
        return PARSE_ERROR, "Duplicate arg name"
    fss.append(fun_name)
    fdict[fun_name] = {"fun_start":lnum, 'fun_end':None, 'args':arg_list}
    return PARSE_OK, ''

def rem_block_end_check(lnum, rbss, rbdict):
    if len(rbss) == 0:
        return PARSE_ERROR, "orphan END_REM"
    if len(rbss) != 1:
        return PARSE_ERROR, "unmatched REM_BLOCK"
    rbdict[rbss.pop()] = lnum
    # print(pgm_line, lnum, rbss, rbdict)
    return PARSE_OK, ''

def stringln_block_end_check(lnum, slbss, slbdict):
    if len(slbss) == 0:
        return PARSE_ERROR, "orphan END_STRINGLN"
    if len(slbss) != 1:
        return PARSE_ERROR, "unmatched STRINGLN_BLOCK"
    slbdict[slbss.pop()] = lnum
    # print("stringln_block_end_check", lnum, slbss, slbdict)
    return PARSE_OK, ''

def string_block_end_check(lnum, sbss, sbdict):
    if len(sbss) == 0:
        return PARSE_ERROR, "orphan END_STRING"
    if len(sbss) != 1:
        return PARSE_ERROR, "unmatched STRING_BLOCK"
    sbdict[sbss.pop()] = lnum
    # print("stringln_block_end_check", lnum, sbss, sbdict)
    return PARSE_OK, ''

def func_end_check(lnum, fss, fdict):
    if len(fss) == 0:
        return PARSE_ERROR, "orphan END_FUN"
    fun_name = fss.pop()
    fdict[fun_name]['fun_end'] = lnum
    return PARSE_OK, ''

def if_check(pgm_line, lnum, iss):
    if_expr = pgm_line.replace(kw_IF, '', 1)
    if_expr = if_expr[:len(if_expr)]
    iss.append({lnum:{"else_if":[], "else":None, "end_if":None}})
    return PARSE_OK, ''

def end_if_check(pgm_line, lnum, iss, if_skip_table, if_take_table):
    if pgm_line != kw_END_IF:
        return PARSE_ERROR, "missing END_IF at end"
    if len(iss) == 0:
        return PARSE_ERROR, "orphan END_IF"
    ifdict = iss.pop()
    if_root = list(ifdict.keys())[0]
    ifdict[if_root]['end_if'] = lnum
    ifdict[if_root]['else_if'] = sorted(ifdict[if_root]['else_if'])
    # print(ifdict)

    if_take_table[if_root] = ifdict[if_root]['end_if']
    # has no else_if and no else
    if len(ifdict[if_root]['else_if']) == 0 and ifdict[if_root]['else'] is None:
        # print("no else_if and no else")
        if_skip_table[if_root] = ifdict[if_root]['end_if']
    # only has else
    elif len(ifdict[if_root]['else_if']) == 0 and ifdict[if_root]['else'] is not None:
        # print("only has else")
        if_skip_table[if_root] = ifdict[if_root]['else']
    # only has else_if
    elif len(ifdict[if_root]['else_if']) > 0 and ifdict[if_root]['else'] is None:
        # print("only has else_if")
        cond_chain = [if_root] + ifdict[if_root]['else_if'] + [ifdict[if_root]['end_if']]
        # print(cond_chain)
        for index, item in enumerate(cond_chain[:-1]):
            if_skip_table[item] = cond_chain[index+1]
            if_take_table[item] = ifdict[if_root]['end_if']

    elif len(ifdict[if_root]['else_if']) > 0 and ifdict[if_root]['else'] is not None:
        # print("has both else and else_if")
        cond_chain = [if_root] + ifdict[if_root]['else_if'] + [ifdict[if_root]['else']] + [ifdict[if_root]['end_if']]
        # print(cond_chain)
        for index, item in enumerate(cond_chain[:-1]):
            if_skip_table[item] = cond_chain[index+1]
            if_take_table[item] = ifdict[if_root]['end_if']
    # print("if_skip_table", if_skip_table)
    # print("if_take_table", if_take_table)
    return PARSE_OK, ''

def elseif_check(pgm_line, lnum, iss):
    if len(iss) == 0:
        return PARSE_ERROR, "orphan ELSE IF"
    ifdict = iss[-1]
    for key in ifdict:
        if ifdict[key]['else'] is not None:
            return PARSE_ERROR, "ELSE IF must be before ELSE"
        ifdict[key]['else_if'].append(lnum)
    # print(ifdict)
    elseif_expr = pgm_line.replace(kw_ELSE_IF, '', 1)
    elseif_expr = elseif_expr[:len(elseif_expr)]
    return PARSE_OK, ''

def else_check(pgm_line, lnum, iss):
    if pgm_line != kw_ELSE and kw_C_COMMENT not in pgm_line:
        return PARSE_ERROR, "extra stuff at end"
    if len(iss) == 0:
        return PARSE_ERROR, "orphan ELSE"
    ifdict = iss[-1]
    for key in ifdict:
        if ifdict[key]['else'] != None:
            return PARSE_ERROR, "unmatched ELSE"
        ifdict[key]['else'] = lnum
    # print(ifdict)
    return PARSE_OK, ''

def new_while_check(lnum, wss, wdict):
    wss.append(lnum)
    wdict[lnum] = None
    return PARSE_OK, ''

def end_while_check(pgm_line, lnum, wss, wdict):
    if pgm_line != kw_END_WHILE and kw_C_COMMENT not in pgm_line:
        return PARSE_ERROR, "extra stuff at end"
    if len(wss) == 0:
        return PARSE_ERROR, "orphan END_WHILE"
    while_start_line = wss.pop()
    wdict[while_start_line] = lnum
    return PARSE_OK, '' 

def break_check(pgm_line, wss):
    split = [x for x in pgm_line.split(' ') if len(x) > 0]
    if len(split) != 1 and kw_C_COMMENT not in pgm_line:
        return PARSE_ERROR, "extra stuff at end"
    if len(wss) == 0:
        return PARSE_ERROR, "BREAK outside WHILE"
    return PARSE_OK, '' 

def continue_check(pgm_line, wss):
    split = [x for x in pgm_line.split(' ') if len(x) > 0]
    if len(split) != 1 and kw_C_COMMENT not in pgm_line:
        return PARSE_ERROR, "extra stuff at end"
    if len(wss) == 0:
        return PARSE_ERROR, "CONTINUE outside WHILE"
    return PARSE_OK, '' 

def is_within_rem_block(lnum, rbdict):
    for key in rbdict:
        if rbdict[key] is None:
            return lnum >= key
        if key <= lnum <= rbdict[key]:
            return True
    return False

def is_within_strlen_block(lnum, slbdict):
    for key in slbdict:
        if slbdict[key] is None:
            return True
        if key < lnum < slbdict[key]:
            return True
    return False

def is_within_str_block(lnum, sbdict):
    for key in sbdict:
        if sbdict[key] is None:
            return True
        if key < lnum < sbdict[key]:
            return True
    return False

def ensure_arg_count(pgm_line, expected_args):
    tokens = [x for x in pgm_line.split() if len(x) > 0]
    arg_count = len(tokens) - 1
    if arg_count != expected_args:
        return PARSE_ERROR, f"Expected {expected_args} args, got {arg_count}"
    return PARSE_OK, ''

def ensure_zero_arg(pgm_line):
    return ensure_arg_count(pgm_line, 0)

def split_string(input_string, max_length=STRING_MAX_SIZE):
    if len(input_string) <= max_length:
        return [input_string]
    return [input_string[i:i+max_length] for i in range(0, len(input_string), max_length)]

def split_str_cmd(kw_type, line_obj):
    str_content = line_obj.content.split(kw_type + " ", 1)[-1]
    if len(str_content) <= STRING_MAX_SIZE:
        return [line_obj]
    kw_list = []
    for item in split_string(str_content):
        new_obj = ds_line(content=f"{kw_STRING} {item}", orig_lnum_sf1=line_obj.orig_lnum_sf1)
        kw_list.append(new_obj)
    if kw_type == kw_STRINGLN:
        new_obj = ds_line(content=f"{kw_ENTER}", orig_lnum_sf1=line_obj.orig_lnum_sf1)
        kw_list.append(new_obj)
    return kw_list

MAX_COMBO = 10

def parse_combo(line_obj):
    combo_keys = [x for x in line_obj.content.split(' ') if len(x) > 0]
    if len(combo_keys) > MAX_COMBO:
        return PARSE_ERROR, f'No more than {MAX_COMBO} combos', None
    for item in [x.lower() for x in combo_keys if x not in ds_hid_keyname_dict.keys()]:
        if item not in valid_combo_chars:
            return PARSE_ERROR, 'Invalid combo character', None
    new_lines = []
    for item in combo_keys:
        new_obj = copy.deepcopy(line_obj)
        new_obj.content = f"KEYDOWN {item}"
        new_lines.append(new_obj)
    for item in reversed(combo_keys):
        new_obj = copy.deepcopy(line_obj)
        new_obj.content = f"KEYUP {item}"
        new_lines.append(new_obj)
    return PARSE_OK, 'Success', new_lines

def check_var_declare(pgm_line, var_dict, fss):
    try:
        pgm_line = replace_operators(pgm_line)
        var_sides = pgm_line.split(kw_VAR_DECLARE, 1)[-1].split('=')
        this_var_name = var_sides[0].strip()
        rightside = var_sides[1].strip()
    except Exception as e:
        return PARSE_ERROR, "Invalid VAR declaration"
    if len(rightside) == 0:
        return PARSE_ERROR, "Empty VAR declaration"
    if_valid_vn, vn_comment = is_valid_var_name(this_var_name)
    if if_valid_vn is False:
        return PARSE_ERROR, vn_comment
    if this_var_name in reserved_variables_dict:
        return PARSE_ERROR, "Re-declaration of reserved variable"
    parent_func_name = None
    if len(fss) > 0:
        parent_func_name = fss[-1]
        
    if parent_func_name not in var_dict:
        var_dict[parent_func_name] = set()

    if this_var_name in var_dict[parent_func_name]:
        return PARSE_ERROR, "Duplicate var name"
    var_dict[parent_func_name].add(this_var_name)

    return PARSE_OK, ''

# this makes sure the code is suitable for converting into python
def single_pass(program_listing, define_dict):
    loop_numbers = set()
    func_table = {}
    if_take_table = {}
    if_skip_table = {}
    # line_number_starting_from_1 : end_while line number
    while_table = {}
    func_search_stack = []
    if_search_stack = []
    while_search_stack = []
    rem_block_search_stack = []
    rem_block_table = {}
    strlen_block_search_stack = []
    strlen_block_table = {}
    str_block_search_stack = []
    str_block_table = {}
    user_declared_var_dict = {}

    return_dict = {
    'is_success':False,
    'comments':"",
    'error_line_number_starting_from_1':None,
    'error_line_str':"",
    'loop_state_save_needed':False,
    'loop_size':None,
    }

    for line_obj in program_listing:
        line_number_starting_from_1 = line_obj.orig_lnum_sf1
        this_line = line_obj.content.lstrip(' \t')
        if len(this_line) == 0:
            continue
        first_word = this_line.split()[0]
        if needs_rstrip(first_word):
            this_line = this_line.rstrip(" \t")
        
        this_indent_level = len(if_search_stack) + len(func_search_stack) + len(while_search_stack)

        presult = PARSE_ERROR
        pcomment = f"single_pass: Unknown error"

        if first_word != kw_DEFINE:
            this_line = replace_DEFINE(this_line, define_dict)
            first_word = this_line.split()[0]

        if first_word == kw_END_REM:
            presult, pcomment = rem_block_end_check(line_number_starting_from_1, rem_block_search_stack, rem_block_table)
        elif is_within_rem_block(line_number_starting_from_1, rem_block_table):
            presult = PARSE_OK
            pcomment = ''
        elif first_word == kw_END_STRINGLN:
            presult, pcomment = stringln_block_end_check(line_number_starting_from_1, strlen_block_search_stack, strlen_block_table)
        elif is_within_strlen_block(line_number_starting_from_1, strlen_block_table):
            presult = PARSE_OK
            pcomment = ''
        elif first_word == kw_END_STRING:
            presult, pcomment = string_block_end_check(line_number_starting_from_1, str_block_search_stack, str_block_table)
        elif is_within_str_block(line_number_starting_from_1, str_block_table):
            presult = PARSE_OK
            pcomment = ''
        elif first_word == kw_DEFINE:
            presult, pcomment = new_define(this_line, define_dict)
        elif first_word == kw_VAR_DECLARE:
            presult, pcomment = check_var_declare(this_line, user_declared_var_dict, func_search_stack)
        elif first_word == kw_FUN:
            presult, pcomment = new_func_check(this_line, line_number_starting_from_1, func_search_stack, func_table)
        elif first_word == kw_END_FUN:
            this_indent_level -= 1
            presult, pcomment = func_end_check(line_number_starting_from_1, func_search_stack, func_table)
        elif first_word == kw_IF:
            presult, pcomment = if_check(this_line, line_number_starting_from_1, if_search_stack)
        elif this_line.startswith(kw_ELSE_IF):
            this_indent_level -= 1
            presult, pcomment = elseif_check(this_line, line_number_starting_from_1, if_search_stack)
        elif first_word == kw_ELSE:
            this_indent_level -= 1
            presult, pcomment = else_check(this_line, line_number_starting_from_1, if_search_stack)
        elif first_word == kw_END_IF:
            this_indent_level -= 1
            presult, pcomment = end_if_check(this_line, line_number_starting_from_1, if_search_stack, if_skip_table, if_take_table)
        elif first_word == kw_WHILE:
            presult, pcomment = new_while_check(line_number_starting_from_1, while_search_stack, while_table)
        elif first_word == kw_END_WHILE:
            this_indent_level -= 1
            presult, pcomment = end_while_check(this_line, line_number_starting_from_1, while_search_stack, while_table)
        elif first_word == kw_LOOP_BREAK:
            presult, pcomment = break_check(this_line, while_search_stack)
        elif first_word == kw_CONTINUE:
            presult, pcomment = continue_check(this_line, while_search_stack)
        elif first_word == kw_REM_BLOCK:
            presult, pcomment = new_rem_block_check(line_number_starting_from_1, rem_block_search_stack, rem_block_table)
        elif first_word == kw_STRINGLN_BLOCK:
            presult, pcomment = new_stringln_block_check(line_number_starting_from_1, strlen_block_search_stack, strlen_block_table)
        elif first_word == kw_STRING_BLOCK:
            presult, pcomment = new_string_block_check(line_number_starting_from_1, str_block_search_stack, str_block_table)
        elif first_word == kw_RETURN:
            if len(func_search_stack) == 0:
                presult = PARSE_ERROR
                pcomment = f"RETURN outside function"
            else:
                presult = PARSE_OK
                pcomment = ''
        elif first_word == kw_SWCC:
            presult, pcomment = PARSE_OK, ''
        elif first_word == kw_SWCF:
            presult, pcomment = PARSE_OK, ''
        elif first_word == kw_SWCR:
            presult, pcomment = PARSE_OK, ''
        elif first_word == kw_OLED_UPDATE:
            presult, pcomment = ensure_zero_arg(this_line)
        elif first_word == kw_OLED_CLEAR:
            presult, pcomment = ensure_zero_arg(this_line)
        elif first_word == kw_OLED_RESTORE:
            presult, pcomment = ensure_zero_arg(this_line)
        elif first_word == kw_BCLR:
            presult, pcomment = ensure_zero_arg(this_line)
        elif first_word == kw_NEXT_PROFILE:
            presult, pcomment = ensure_zero_arg(this_line)
        elif first_word == kw_PREV_PROFILE:
            presult, pcomment = ensure_zero_arg(this_line)
        elif first_word == kw_DP_SLEEP:
            presult, pcomment = ensure_zero_arg(this_line)
        elif first_word == kw_KEYDOWN or first_word == kw_KEYUP:
            presult, pcomment = ensure_arg_count(this_line, 1)
        elif this_line.startswith(kw_SWCOLOR):
            presult, pcomment = PARSE_OK, ''
        elif this_line.startswith(kw_LOOP):
            presult, pcomment, value = check_loop(this_line)
            if value is not None:
                return_dict['loop_state_save_needed'] = True
                loop_numbers.add(value)
        else:
             presult, pcomment = PARSE_OK, ''

        if this_indent_level < 0:
            presult, pcomment = PARSE_ERROR, "Invalid indent level"
        
        line_obj.indent_level = this_indent_level
        
        if presult == PARSE_ERROR:
            # error_message = f"PARSE ERROR at Line {line_number_starting_from_1}: {this_line}\n{pcomment}"
            # print(error_message)
            return_dict['is_success'] = False
            return_dict['comments'] = pcomment
            return_dict['error_line_number_starting_from_1'] = line_number_starting_from_1
            return_dict['error_line_str'] = this_line
            return return_dict
        
    # ----------
    
    if len(if_search_stack) != 0:
        return_dict['is_success'] = False
        # return_dict['comments'] = f"END_IF missing for IF at line {list(if_search_stack[0].keys())[0]}"
        return_dict['comments'] = "Missing END_IF"
        return_dict['error_line_number_starting_from_1'] = list(if_search_stack[0].keys())[0]
        return return_dict

    if len(func_search_stack) != 0:
        return_dict['is_success'] = False
        # return_dict['comments'] = f"END_FUN missing for FUNCTION {func_search_stack[0]}() at line {func_table[func_search_stack[0]]['fun_start']}"
        return_dict['comments'] = "Missing END_FUN"
        return_dict['error_line_number_starting_from_1'] = func_table[func_search_stack[0]]['fun_start']
        return return_dict

    if len(while_search_stack) != 0:
        return_dict['is_success'] = False
        # return_dict['comments'] = f"END_WHILE missing for WHILE at line {while_search_stack[-1]}"
        return_dict['comments'] = "Missing END_WHILE"
        return_dict['error_line_number_starting_from_1'] = while_search_stack[-1]
        return return_dict

    for key in rem_block_table:
        if rem_block_table[key] is None:
            return_dict['is_success'] = False
            return_dict['comments'] = "Missing END_REM"
            return_dict['error_line_number_starting_from_1'] = key
            return_dict['error_line_str'] = ""
            return return_dict

    for key in strlen_block_table:
        if strlen_block_table[key] is None:
            return_dict['is_success'] = False
            return_dict['comments'] = "Missing END_STRINGLN"
            return_dict['error_line_number_starting_from_1'] = key
            return_dict['error_line_str'] = ""
            return return_dict

    for key in str_block_table:
        if str_block_table[key] is None:
            return_dict['is_success'] = False
            return_dict['comments'] = "Missing END_STRING"
            return_dict['error_line_number_starting_from_1'] = key
            return_dict['error_line_str'] = ""
            return return_dict
    # ----------

    return_dict['is_success'] = True
    return_dict['comments'] = ""
    return_dict['error_line_number_starting_from_1'] = None
    return_dict['error_line_str'] = ""
    return_dict['rem_block_table'] = rem_block_table
    return_dict['strlen_block_table'] = strlen_block_table
    return_dict['str_block_table'] = str_block_table
    return_dict['dspp_listing_with_indent_level'] = program_listing
    return_dict['user_declared_var_dict'] = user_declared_var_dict

    if len(loop_numbers) > 0:
        return_dict['loop_size'] = max(loop_numbers)
    
    return return_dict

def get_default_def_dict():
    default_dict = {
        kw_RANDOM_LOWERCASE_LETTER : f"{kw_RANDCHR}(0x101)",
        kw_RANDOM_UPPERCASE_LETTER : f"{kw_RANDCHR}(0x102)",
        kw_RANDOM_LETTER : f"{kw_RANDCHR}(0x103)",
        kw_RANDOM_NUMBER : f"{kw_RANDCHR}(0x104)",
        kw_RANDOM_SPECIAL : f"{kw_RANDCHR}(0x108)",
        kw_RANDOM_CHAR : f"{kw_RANDCHR}(0x10f)",
        kw_DEFAULTDELAY : "_DEFAULTDELAY=",
        kw_DEFAULTCHARDELAY : "_DEFAULTCHARDELAY=",
        kw_CHARJITTER : "_CHARJITTER=",
        kw_MOUSE_WHEEL : f"{kw_MOUSE_SCROLL} 0",
        f"{kw_FUNCTION} " : f"{kw_FUN} ",
        kw_END_FUNCTION : kw_END_FUN,
        kw_TRUE : "1",
        kw_FALSE : "0",
        kw_OLED_PRINT : kw_OLED_LPRINT,
        rv_IS_NUMLOCK_ON : f"(({rv_KBLED_BITFIELD}&0x1)!=0)",
        rv_IS_CAPSLOCK_ON : f"(({rv_KBLED_BITFIELD}&0x2)!=0)",
        rv_IS_SCROLLLOCK_ON : f"(({rv_KBLED_BITFIELD}&0x4)!=0)",
        kw_PASS : "pass",
        kw_STR_PRINT_FORMAT : DUMMY_VAR_NAME,
        kw_STR_PRINT_PADDING : DUMMY_VAR_NAME,
    }
    return default_dict

class import_result(IntEnum):
    NOT_IMPORT_COMMAND = 0
    ALREADY_IMPORTED = 1
    NEW_IMPORT = 2

already_imported_header_set = set()
def get_import_lineobjs(first_word, import_name_to_line_obj_dict):
    if import_name_to_line_obj_dict is None:
        return import_result.NOT_IMPORT_COMMAND, []
    new_lineobj_list = []
    if first_word in import_name_to_line_obj_dict:
        if first_word in already_imported_header_set:
            return import_result.ALREADY_IMPORTED, []
        new_lineobj_list += import_name_to_line_obj_dict[first_word]
        already_imported_header_set.add(first_word)
    return import_result.NEW_IMPORT, new_lineobj_list

def run_all(program_listing, import_name_to_line_obj_dict=None):
    all_def_dict = get_default_def_dict()
    already_imported_header_set.clear()
    # ----------- expand STRING_BLOCKm, STRINGLN_BLOCK, and REM_BLOCK. split STRING and STRINGLN ----------
    rdict = single_pass(program_listing, all_def_dict)
    if rdict['is_success'] is False:
        return rdict
    new_program_listing = []
    for line_obj in program_listing:
        line_number_starting_from_1 = line_obj.orig_lnum_sf1

        if is_within_strlen_block(line_number_starting_from_1, rdict['strlen_block_table']):
            line_obj.content = f"{kw_STRINGLN} {line_obj.content}"
        elif is_within_str_block(line_number_starting_from_1, rdict['str_block_table']):
            line_obj.content = f"{kw_STRING} {line_obj.content}"
        elif is_within_rem_block(line_number_starting_from_1, rdict['rem_block_table']):
            line_obj.content = f"{kw_C_COMMENT} {line_obj.content}"
        else:
            line_obj.content = line_obj.content.lstrip(' \t')

        if len(line_obj.content) == 0:
            continue

        first_word = line_obj.content.split(" ")[0]
        
        imp_result, imported_lineobj_list = get_import_lineobjs(first_word, import_name_to_line_obj_dict)
        if imp_result == import_result.ALREADY_IMPORTED:
            continue
        if imp_result == import_result.NEW_IMPORT and len(imported_lineobj_list) > 0:
            new_program_listing += imported_lineobj_list
            continue

        if first_word in [kw_STRINGLN_BLOCK, kw_END_STRINGLN, kw_STRING_BLOCK, kw_END_STRING]:
            continue

        if first_word in [kw_STRINGLN, kw_STRING]:
            for item in split_str_cmd(first_word, line_obj):
                new_program_listing.append(item)
        else:
            new_program_listing.append(line_obj)

    program_listing = new_program_listing
    # ---------------------
    new_program_listing = []
    for line_obj in program_listing:
        # remove leading space and tabs
        line_obj.content = line_obj.content.lstrip(" \t")
        first_word = line_obj.content.split(" ")[0]
        # remove single-line comments 
        if first_word == kw_REM or first_word.startswith(kw_C_COMMENT):
            continue
        # remove INJECT_MOD
        if first_word == kw_INJECT_MOD:
            line_obj.content = line_obj.content.replace(kw_INJECT_MOD, "", 1)
        if first_word not in ds_func_to_parse_as_str:
            cpos = line_obj.content.find(kw_C_COMMENT)
            if cpos != -1:
                line_obj.content = line_obj.content[:cpos].rstrip(" \t")
            line_obj.content = replace_operators(line_obj.content)
        if first_word == kw_PREV_PROFILE:
            line_obj.content = f"{kw_SKIP_PROFILE} -1"
        if first_word == kw_NEXT_PROFILE:
            line_obj.content = f"{kw_SKIP_PROFILE} 1"
        if line_obj.content.strip() == kw_GOTO_PROFILE:
            rdict['is_success'] = False
            rdict['comments'] = "Missing profile name"
            rdict['error_line_number_starting_from_1'] = line_obj.orig_lnum_sf1
            rdict['error_line_str'] = line_obj.content
            return rdict
        line_obj.content = line_obj.content.lstrip(" \t")
        new_program_listing.append(line_obj)

    program_listing = new_program_listing

    rdict = single_pass(program_listing, all_def_dict)
    if rdict['is_success'] is False:
        return rdict

    print("---------First Pass OK!---------")
    # ----- Second Pass -------------

    second_pass_program_listing = []
    needs_end_if = False

    epilogue = 0
    if rdict['loop_state_save_needed']:
        epilogue |= 0x1

    if epilogue != 0:
        second_pass_program_listing.append(ds_line(content=f"_EPILOGUE_ACTIONS = {epilogue}"))
    if rdict['loop_size'] is not None:
        second_pass_program_listing.append(ds_line(content=f"_LOOP_SIZE = {rdict['loop_size']+1}"))
    
    for line_obj in program_listing:
        line_number_starting_from_1 = line_obj.orig_lnum_sf1
        this_line = line_obj.content.lstrip(' \t')
        rdict['error_line_number_starting_from_1'] = line_number_starting_from_1
        rdict['error_line_str'] = this_line
        if len(this_line) == 0:
            continue
        first_word = this_line.split(" ")[0]
        if needs_rstrip(first_word):
            line_obj.content = this_line.rstrip(" \t")
        if first_word != kw_DEFINE:
                line_obj.content = replace_DEFINE(this_line, all_def_dict)
        else:
            continue
        this_line = line_obj.content.lstrip(' \t')

        if first_word == kw_REPEAT:
            if len(second_pass_program_listing) == 0:
                rdict['is_success'] = False
                rdict['comments'] = "Nothing before REPEAT"
                return rdict
            try:
                repeat_count = int(this_line[len(kw_REPEAT):].strip())
                if repeat_count > REPEAT_MAX_SIZE:
                    raise ValueError
            except Exception as e:
                rdict['is_success'] = False
                rdict['comments'] = "Invalid REPEAT count"
                return rdict
            last_line = second_pass_program_listing[-1]
            for x in range(repeat_count):
                second_pass_program_listing.append(last_line)
        elif this_line.startswith(kw_LOOP):
            presult, pcomment, value = check_loop(this_line)
            if needs_end_if:
                second_pass_program_listing.append(ds_line(kw_END_IF, line_number_starting_from_1))
            loop_str = f'{kw_IF} _KEYPRESS_COUNT % _LOOP_SIZE == {value}'
            second_pass_program_listing.append(ds_line(loop_str, line_number_starting_from_1))
            needs_end_if = True
        else:
            second_pass_program_listing.append(line_obj)
        
    if needs_end_if:
        second_pass_program_listing.append(ds_line(kw_END_IF, line_number_starting_from_1))

    # -----------------

    new_program_listing = []
    for line_obj in second_pass_program_listing:
        first_word = line_obj.content.split(" ")[0]
        # Expand key combos
        if first_word in ds_hid_keyname_dict.keys():
            parse_result, comments, new_lines = parse_combo(line_obj)
            if parse_result == PARSE_ERROR:
                rdict['is_success'] = False
                rdict['comments'] = comments
                rdict['error_line_number_starting_from_1'] = line_obj.orig_lnum_sf1
                rdict['error_line_str'] = line_obj.content
                return rdict
            new_program_listing += new_lines
            continue
        line_obj.content = line_obj.content.lstrip(" \t")
        new_program_listing.append(line_obj)

    second_pass_program_listing = new_program_listing
    # -----------------
    rdict = single_pass(second_pass_program_listing, all_def_dict)
    rdict['define_dict'] = all_def_dict
    return rdict

def preprocess_import_str_dict(import_str_dict):
    preprocessed_import_lineobj_dict = {}
    for key in import_str_dict:
        lineobj_list = make_list_of_ds_line_obj_from_str_listing(import_str_dict[key], key)
        rdict = run_all(lineobj_list)
        # after run_all(), DEFINEs would have been replaced. This add them back to be included in other scripts.
        user_define_dict = {k:v for k, v in rdict['define_dict'].items() if k not in get_default_def_dict()}
        for defkey in user_define_dict:
            user_def_lineobj = ds_line(f"DEFINE {defkey} {user_define_dict[defkey]}", orig_lnum_sf1=1)
            lineobj_list.insert(0, user_def_lineobj)
            rdict["dspp_listing_with_indent_level"].insert(0, user_def_lineobj)
        if rdict['is_success'] is False:
            preprocessed_import_lineobj_dict[key] = lineobj_list
        else:
            preprocessed_import_lineobj_dict[key] = rdict["dspp_listing_with_indent_level"]
    return preprocessed_import_lineobj_dict

if __name__ == "__main__":
    # Require at least input and output arguments
    if len(sys.argv) < 2:
        print(f"Usage: {__file__} <ds3_script> [output]")
        exit()

    text_file = open(sys.argv[1])
    text_listing = text_file.readlines()
    text_file.close()

    program_listing = []
    for index, line in enumerate(text_listing):
        line = line.rstrip("\r\n")
        program_listing.append(ds_line(line, index + 1))

    rdict = run_all(program_listing)
    
    if rdict['is_success'] is False:
        print("Preprocessing failed!")
        print(f"\t{rdict['comments']}")
        print(f"\tLine {rdict['error_line_number_starting_from_1']}: {rdict['error_line_str']}")
        exit()

    post_pp_listing = rdict["dspp_listing_with_indent_level"]
    
    for item in post_pp_listing:
        final_str = "    "*item.indent_level + item.content
        print(final_str)