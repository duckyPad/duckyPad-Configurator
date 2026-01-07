import sys
from dsvm_common import *
import dsvm_preprocessor
import copy
import ast

def make_str_func(first_word, this_line):
    str_content = this_line[len(first_word)+1:]
    return f"{first_word}({repr(str_content)})"

def make_arg_func(first_word, this_line):
    args = this_line[len(first_word)+1:].strip().split(" ")
    final_str = first_word + "("
    for item in args:
        final_str += f"{item}, "
    final_str = final_str.rstrip(", ") + ")"
    return final_str

def line_has_unconsumed_stack_value(line_obj):
    try:
        nodes = ast.parse(line_obj.content).body
        return bool(nodes and isinstance(nodes[0], ast.Expr))
    except Exception as e:
        pass
        # print("line_has_unconsumed_stack_value:", e)
    return False

def run_all(program_listing):
    new_listing = []
    for line_obj in program_listing:
        line_obj.content = line_obj.content.lstrip(' \t')
        first_word = line_obj.content.split()[0]

        if first_word == kw_VAR_DECLARE:
            line_obj.content = line_obj.content[len(kw_VAR_DECLARE):].strip()
        if first_word not in ds_func_to_parse_as_str:
            line_obj.content = replace_operators(line_obj.content)

        this_line = line_obj.content

        if first_word in ds_func_to_parse_as_str:
            new_obj = copy.deepcopy(line_obj)
            new_obj.content = make_str_func(first_word, this_line)
            new_listing.append(new_obj)
        elif first_word in ds_builtin_func_lookup:
            new_obj = copy.deepcopy(line_obj)
            new_obj.content = make_arg_func(first_word, this_line)
            new_listing.append(new_obj)
        elif first_word == kw_IF:
            new_obj = copy.deepcopy(line_obj)
            new_obj.content = f"if {this_line[len(kw_IF):len(this_line)].strip().removesuffix(kw_THEN)}:"
            new_listing.append(new_obj)
        elif this_line.startswith(f"{kw_ELSE_IF} "):
            new_obj = copy.deepcopy(line_obj)
            new_obj.content = f"elif {this_line[len(kw_ELSE_IF):len(this_line)].strip().removesuffix(kw_THEN)}:"
            new_listing.append(new_obj)
        elif first_word == kw_ELSE:
            new_obj = copy.deepcopy(line_obj)
            new_obj.content = "else:"
            new_listing.append(new_obj)
        elif first_word == kw_CONTINUE:
            new_obj = copy.deepcopy(line_obj)
            new_obj.content = "continue"
            new_listing.append(new_obj)
        elif first_word == kw_LOOP_BREAK:
            new_obj = copy.deepcopy(line_obj)
            new_obj.content = "break"
            new_listing.append(new_obj)
        elif first_word == kw_RETURN:
            return_expr = this_line[len(kw_RETURN):].strip()
            new_obj = copy.deepcopy(line_obj)
            new_obj.content = f"return {return_expr}"
            new_listing.append(new_obj)
        elif first_word in ds2py_ignored_cmds:
            continue
        elif first_word == kw_WHILE:
            new_obj = copy.deepcopy(line_obj)
            new_obj.content = f"while {this_line[len(kw_WHILE):].strip()}:"
            new_listing.append(new_obj)
        elif first_word == kw_FUN:
            new_obj = copy.deepcopy(line_obj)
            new_obj.content = f"def {this_line[len(kw_FUN):].strip()}:"
            new_listing.append(new_obj)
        else:
            new_listing.append(line_obj)

    for index, line_obj in enumerate(new_listing):
        line_obj.py_lnum_sf1 = index+1
        if line_has_unconsumed_stack_value(line_obj):
            line_obj.content = f"{DUMMY_VAR_NAME} = " + line_obj.content
    return new_listing

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

    rdict = dsvm_preprocessor.run_all(program_listing)
    
    if rdict['is_success'] is False:
        print("Preprocessing failed!")
        print(f"\t{rdict['comments']}")
        print(f"\tLine {rdict['error_line_number_starting_from_1']}: {rdict['error_line_str']}")
        exit()

    post_pp_listing = rdict["dspp_listing_with_indent_level"]
    # print_ds_line_list(post_pp_listing)
    pyout = run_all(post_pp_listing)

    print_ds_line_list(pyout)