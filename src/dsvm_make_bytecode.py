import sys
from dsvm_common import *
import dsvm_preprocessor
import dsvm_ds2py
import ast
import symtable
import dsvm_myast
import copy
from collections import defaultdict
import traceback
import re

"""
duckyscript VM changelog
version 0:
OG duckyPad with duckyscript 3

version 1:
duckyPad Pro with duckyScript 3
Done:
Added VMVER to aid version checking
mouse move and mouse scroll arguments on stack
more changes at the end of bytecode_vm.md

Version 2:
2025-11-23
New flat memory map
complete overhaul
new opcode values
single stack
32 bit stack width and arithmetics
a lot more look at notes

"""
DS_VM_VERSION = 2
print_asm = False

arith_lookup = {
    "Eq" : OP_EQ,
    "NotEq" : OP_NOTEQ,
    "Lt" : OP_LT,
    "LtE" : OP_LTE,
    "Gt" : OP_GT,
    "GtE" : OP_GTE,

    "Add" : OP_ADD,
    "Sub" : OP_SUB,
    "Mult" : OP_MULT,
    "Div" : OP_DIV,
    "Mod" : OP_MOD,
    "Pow" : OP_POW,

    "LShift" : OP_LSHIFT,
    "RShift" : OP_RSHIFT,
    "BitOr" : OP_BITOR,
    "BitAnd" : OP_BITAND,
    "BitXor" : OP_BITXOR,

    "And" : OP_LOGIAND,
    "Or" : OP_LOGIOR,

    "Invert" : OP_BITINV,
    "Not" : OP_LOGINOT,
    "USub" : OP_USUB,
}

global_context_dict = {}

def make_instruction_pushc(value, comment: str = ""):
    val = int(value) & 0xFFFFFFFF
    if val > 0xFFFF:
        return dsvm_instruction(opcode=OP_PUSHC32, payload=val, comment=comment)
    if val > 0xFF:
        return dsvm_instruction(opcode=OP_PUSHC16, payload=val, comment=comment)
    return dsvm_instruction(opcode=OP_PUSHC8, payload=val, comment=comment)

def print_assembly_list(asmlist):
    if print_asm is False:
        return
    for item in asmlist:
        print(item)

def print_full_assembly_from_context_dict(ctx_dict):
    if print_asm is False:
        return
    bin_size_bytes = 0
    for item in ctx_dict["root_assembly_list"]:
        print(item)
        bin_size_bytes += item.opcode.length
    for key in ctx_dict['func_assembly_dict']:
        print(f'----FUNC: {key}----')
        for item in ctx_dict['func_assembly_dict'][key]:
            print(item)
            bin_size_bytes += item.opcode.length
        print(f'----END {key}----')
    print(f"Total: {bin_size_bytes} Bytes")

AST_ARITH_NODES = (
    ast.operator,
    ast.cmpop,
    ast.boolop,
    ast.unaryop,
)

def get_orig_ds_line_from_py_lnum(rdict, this_pylnum_sf1):
    if this_pylnum_sf1 is None:
        return ""
    og_index_sf0 = None
    for line_obj in rdict['ds2py_listing']:
        if line_obj.py_lnum_sf1 == this_pylnum_sf1:
            og_index_sf0 = line_obj.orig_lnum_sf1 - 1
            break
    if og_index_sf0 is None:
        return ""
    return rdict['orig_listing'][og_index_sf0].content

def search_in_symtable(name: str, table: symtable.SymbolTable):
    try:
        return table.lookup(name)
    except KeyError:
        return None

def is_known_global(name, ctx_dict):
    try:
        return name in ctx_dict["user_declared_var_dict"][None]
    except Exception as e:
        print("is_known_global:", e)
    return False

def classify_name(name: str, current_function: str | None, ctx_dict) -> int:
    if is_ds_keyword(name):
        raise ValueError(f'Invalid Variable Name: "{name}"')
    
    if name in reserved_variables_dict:
        return SymType.RESERVED_VAR
    
    root_table = ctx_dict["symtable_root"]

    if current_function is not None:
        this_table = dsvm_myast.find_function_table(root_table, current_function)
        user_declared_func_locals = ctx_dict['user_declared_var_dict'].get(current_function)
        if this_table is None:
            raise ValueError(f"No symtable for {name} in {current_function!r}()")

        sym = search_in_symtable(name, this_table)
        if sym is not None:
            if sym.is_parameter() and user_declared_func_locals is not None and name in user_declared_func_locals:
                raise ValueError(f"Variable clash: {name} cannot be both arg and local")
            if sym.is_parameter():
                return SymType.FUNC_ARG
            if user_declared_func_locals is not None and name in user_declared_func_locals:
                return SymType.FUNC_LOCAL_VAR
                
    if is_known_global(name, ctx_dict):
        return SymType.GLOBAL_VAR
    raise ValueError(f'Unknown symbol "{name}" in function "{current_function}()"')

def visit_name_node(node, ctx_dict, inst_list):
    og_ds_line = ctx_dict["og_ds_line"]
    current_function = ctx_dict["func_def_name"]

    node_name = node.id
    sym_type = classify_name(node.id, current_function, ctx_dict)
    # print("symtype:", node.id, current_function, sym_type.name)

    parent_func = current_function
    if sym_type in [SymType.GLOBAL_VAR, SymType.RESERVED_VAR]:
        parent_func = None
    this_var_info = var_info(node_name, sym_type, parent_func)
    ctx_dict['var_info_set'].add(this_var_info)

    if isinstance(node.ctx, ast.Store):
        opcode = OP_POPR if (sym_type in [SymType.FUNC_ARG, SymType.FUNC_LOCAL_VAR]) else OP_POPI
        inst_list.append(dsvm_instruction(opcode=opcode, payload=node_name, comment=og_ds_line, parent_func=current_function, var_type=sym_type))
        return

    if isinstance(node.ctx, ast.Load):
        opcode = OP_PUSHR if (sym_type in [SymType.FUNC_ARG, SymType.FUNC_LOCAL_VAR]) else OP_PUSHI
        inst_list.append(dsvm_instruction(opcode=opcode, payload=node_name, comment=og_ds_line, parent_func=current_function, var_type=sym_type))

def get_key_combined_value(keyname):
    if keyname in ds_hid_keyname_dict:
        key_code = ds_hid_keyname_dict[keyname][0]
        key_type = ds_hid_keyname_dict[keyname][1]
    elif len(keyname) == 1:
        key_code = ord(keyname[0])
        key_type = KEY_TYPE_CHAR
    else:
        raise ValueError(f"Invalid Key: {keyname}")
    return ((key_type % 0xff) << 8) | (key_code % 0xff)

def visit_node(node, ctx_dict):
    current_function = ctx_dict.get("func_def_name")
    caller_func_name = ctx_dict["caller_func_name"]
    # Pick the right instruction list (root vs function)
    if current_function is None:
        instruction_list = ctx_dict["root_assembly_list"]
    else:
        instruction_list = ctx_dict["func_assembly_dict"].setdefault(current_function, [])

    og_ds_line = get_orig_ds_line_from_py_lnum(ctx_dict, getattr(node, "lineno", None))
    ctx_dict["og_ds_line"] = og_ds_line

    def emit(opcode, payload=None, label=None, parent_func=None):
        instruction_list.append(
            dsvm_instruction(opcode=opcode, payload=payload, label=label, comment=og_ds_line, parent_func=parent_func)
        )

    if isinstance(node, ast.Name):
        visit_name_node(node, ctx_dict, instruction_list)

    elif isinstance(node, ast.Constant):
        if isinstance(node.value, str) and caller_func_name in ds_str_func_lookup:
            emit(OP_PUSHSTR, payload=node.value, parent_func=current_function)
        elif isinstance(node.value, str) and caller_func_name in ds_keypress_func_lookup:
            emit(OP_PUSHC16, payload=get_key_combined_value(node.value))
        elif isinstance(node.value, int):
            instruction_list.append(make_instruction_pushc(node.value, og_ds_line))
        else:
            raise ValueError(f"Unsupported Constant: {node.value}")

    elif isinstance(node, AST_ARITH_NODES):
        op_name = node.__class__.__name__
        if op_name not in arith_lookup:
            raise ValueError(f"Unsupported Operation: {op_name}")
        emit(arith_lookup[op_name])

    elif isinstance(node, ast.If):
        emit(OP_BRZ, payload=ctx_dict["if_destination_label"])

    elif isinstance(node, ast.While):
        emit(OP_BRZ, payload=ctx_dict["while_end_label"])

    elif isinstance(node, ast.Continue):
        emit(OP_JMP, payload=ctx_dict["while_start_label"])

    elif isinstance(node, ast.Break):
        emit(OP_JMP, payload=ctx_dict["while_end_label"])

    elif isinstance(node, ast.Call):
        func_name = node.func.id
        if func_name in ds_reserved_funcs:
            fun_info = ds_reserved_funcs[func_name]
            emit(fun_info.opcode)
            if fun_info.has_return_value is False:
                emit(OP_PUSH0)
        else:
            ctx_dict['func_visit_set'].add(func_name)
            emit(OP_CALL, payload=f"func_{func_name}")

    elif isinstance(node, ast.Return):
        arg_count = dsvm_myast.how_many_args(current_function, ctx_dict)
        if arg_count is None:
            raise ValueError("Invalid arg count")
        emit(OP_RET, payload=arg_count)

    elif isinstance(node, dsvm_myast.add_nop):
        emit(OP_NOP, label=node.label)

    elif isinstance(node, dsvm_myast.add_jmp):
        emit(OP_JMP, payload=node.label)

    elif isinstance(node, dsvm_myast.add_push0):
        emit(OP_PUSH0)

    elif isinstance(node, dsvm_myast.add_default_return):
        if instruction_list[-1].opcode != OP_RET:
            emit(OP_PUSH0)
            emit(OP_RET, payload=node.arg_count)

    elif isinstance(node, dsvm_myast.add_alloc):
        emit(OP_ALLOC, payload=node.func_name)

    else:
        raise ValueError(f"Unsupported leaf node: {node}")

def print_symtable(tbl, indent=0):
    pad = " " * indent
    print(f"{pad}Table ({tbl.get_type()}): {tbl.get_name()}")
    for symbol in tbl.get_symbols():
        print(f"{pad}  - {symbol.get_name()} "
              f"(param={symbol.is_parameter()}, "
              f"local={symbol.is_local()}, "
              f"global={symbol.is_global()}, "
              f"free={symbol.is_free()}, "
              )

    for child in tbl.get_children():
        print_symtable(child, indent + 2)

# ---------------------------

def resolve_global_and_reserved_var_address(var_name, udgv_lookup):
    if var_name in reserved_variables_dict:
        return reserved_variables_dict[var_name]
    if var_name in udgv_lookup:
        return udgv_lookup[var_name]
    raise ValueError(f"Unknown variable: {var_name}")

def group_vars(global_context_dict):
    grouped_data = defaultdict(lambda: {"args": [], "locals": []})
    for variable in global_context_dict['var_info_set']:
        if variable.func is None:
            continue
        if variable.type == SymType.FUNC_LOCAL_VAR:
            grouped_data[variable.func]["locals"].append(variable.name)

    for func_name in global_context_dict['func_args_dict']:
        grouped_data[func_name]['args'] = global_context_dict['func_args_dict'][func_name]

    for key in grouped_data:
         grouped_data[key]['locals'].sort()
    return dict(grouped_data)

def needs_resolving(inst):
    if inst.opcode.length == 1:
        return False
    if isinstance(inst.payload, str):
        return True
    if isinstance(inst.payload, int):
        return False
    raise ValueError(f"Unable to resolve: {inst}")

def var_name_to_address_lookup_only_for_strprint(var_name, str_inst, arg_and_local_var_lookup, udgv_lookup):
    parent_func = str_inst.parent_func
    # priority: reserved vars, args, locals, globals
    if var_name in reserved_variables_dict:
        return reserved_variables_dict[var_name], SymType.RESERVED_VAR
    if parent_func is not None and parent_func in arg_and_local_var_lookup:
        fun_var_list = arg_and_local_var_lookup[parent_func]
        if var_name in fun_var_list['args']:
            return (fun_var_list['args'].index(var_name) + 1) * 4, SymType.FUNC_ARG
        if var_name in fun_var_list['locals']:
            return (fun_var_list['locals'].index(var_name) + 1) * -4, SymType.FUNC_LOCAL_VAR
    if var_name in udgv_lookup:
        return udgv_lookup[var_name], SymType.GLOBAL_VAR
    return None, None

def get_partial_varname_addr(msg, str_inst, arg_and_local_var_lookup, udgv_lookup):
    if not msg:
        return None, None, None
    for x in range(len(msg), -1, -1):
        partial_name = msg[:x]
        addr, var_type = var_name_to_address_lookup_only_for_strprint(
            partial_name, str_inst, arg_and_local_var_lookup, udgv_lookup)
        if addr is not None:
            return partial_name, addr, var_type
    return None, None, None

def get_func_args(symtable_root):
    func_args = {}
    def _traverse(table):
        if table.get_type() == 'function':
            func_name = table.get_name()
            args = list(table.get_parameters()) 
            func_args[func_name] = args
        for child in table.get_children():
            _traverse(child)
    _traverse(symtable_root)
    return func_args

def extract_printf_specifier(text):
    # ^             : Start of the string
    # %             : Literal percent sign
    # [-+ #0]* : Optional flags (left-align, sign, space, hash, zero-padding)
    # (\d+)?        : Optional width (one or more digits)
    # (\.\d+)?      : Optional precision (a dot followed by digits)
    # [duxX]        : The type specifier (d, u, x, X)
    pattern = r"^%[-+ #0]*(\d+)?(\.\d+)?[duxX]"
    match = re.match(pattern, text)
    if match:
        return match.group(0)
    return ""

endianness = 'little'
var_boundary_fp_rel = 0x1e
var_boundary_udgv = 0x1f

def replace_var_in_str(instruction, arg_and_local_var_lookup, udgv_lookup):
    result = bytearray()
    msg = instruction.payload
    i = 0
    msg_len = len(msg)

    while i < msg_len:
        ch = msg[i]

        if ch == "$":
            var_name, var_addr, var_type = get_partial_varname_addr(
                msg[i + 1:], instruction, arg_and_local_var_lookup, udgv_lookup
            )

            # If couldn't resolve the variable, treat '$' as a literal.
            if var_addr is None:
                result.extend(ch.encode())
                i += 1
                continue

            if var_type in (SymType.FUNC_ARG, SymType.FUNC_LOCAL_VAR):
                boundary = var_boundary_fp_rel
                payload_bytes = var_addr.to_bytes(2, endianness, signed=True)
            else:
                boundary = var_boundary_udgv
                payload_bytes = var_addr.to_bytes(2, endianness, signed=False)

            # Skip over '$' + variable name
            i += 1 + len(var_name)
            printf_format_specifier = extract_printf_specifier(msg[i:])
            # Emit boundary, payload, boundary
            result.extend(boundary.to_bytes(1, endianness))
            result.extend(payload_bytes)
            result.extend(printf_format_specifier.encode("ascii", errors="ignore"))
            result.extend(boundary.to_bytes(1, endianness))
            # skip over format specifier (if any)
            i += len(printf_format_specifier)
        else:
            result.extend(ch.encode())
            i += 1
    result.append(0)
    return result

def compile_to_bin(rdict):
    if print_asm:
        print("\n\n--------- Assembly Listing, (Mildly) Optimised, Unresolved: ---------")
        print_full_assembly_from_context_dict(rdict)

    """
    this is generated from walking the nodes, not the symtable and AST.
    that means if a function has args but none are referenced, those args wont show up
    """
    user_strings_dict = {}
    func_arg_and_local_var_lookup = rdict['func_arg_and_local_var_lookup']
    user_declared_global_var_addr_lookup = {}
    for index, item in enumerate(sorted([x.name for x in rdict['var_info_set'] if x.type is SymType.GLOBAL_VAR])):
        user_declared_global_var_addr_lookup[item] = index * USER_VAR_BYTE_WIDTH + USER_VAR_START_ADDRESS

    if len(user_declared_global_var_addr_lookup) > MAX_UDV_COUNT:
        raise ValueError("Too many user-declared variables")

    print("\n--------- Global Variables ---------")
    print(user_declared_global_var_addr_lookup)
    print("\n--------- Func Args and Local Variables ---------")
    for key in func_arg_and_local_var_lookup:
        print(f"{key}: {func_arg_and_local_var_lookup[key]}")

    final_assembly_list = []
    """
    Combine root level and function instructions
    resolve their address in ROM.
    Strings will come later
    """
    curr_inst_addr = 0
    for this_inst in rdict['root_assembly_list']:
        this_inst.addr = curr_inst_addr
        curr_inst_addr += this_inst.opcode.length
        final_assembly_list.append(this_inst)

    for func_name in rdict['func_assembly_dict']:
        for this_inst in rdict['func_assembly_dict'][func_name]:
            this_inst.addr = curr_inst_addr
            curr_inst_addr += this_inst.opcode.length
            final_assembly_list.append(this_inst)

    # Build label -> addr dict
    label_to_addr_dict = {}
    for this_inst in final_assembly_list:
        if this_inst.label is None:
            continue
        if len(this_inst.label) == 0:
            continue
        label_to_addr_dict[this_inst.label] = this_inst.addr

    for this_inst in final_assembly_list:
        if needs_resolving(this_inst) is False:
            continue

        if this_inst.opcode == OP_PUSHSTR:
            bytestr = replace_var_in_str(this_inst, func_arg_and_local_var_lookup, user_declared_global_var_addr_lookup)
            bytestr = bytes(bytestr)
            this_inst.payload = bytestr
            user_strings_dict[bytestr] = None
        elif this_inst.payload in label_to_addr_dict:
            this_inst.payload = label_to_addr_dict[this_inst.payload]
        elif this_inst.opcode == OP_ALLOC:
            local_vars_count = 0
            try:
                local_vars_count = len(func_arg_and_local_var_lookup[this_inst.payload]['locals'])
            except Exception as e:
                pass
            this_inst.payload = local_vars_count
        elif this_inst.opcode in [OP_PUSHI, OP_POPI]: # global variables
            this_inst.payload = resolve_global_and_reserved_var_address(this_inst.payload, user_declared_global_var_addr_lookup)
        elif this_inst.opcode in [OP_PUSHR, OP_POPR]: # local var or func args
            var_name = this_inst.payload
            parent_func = this_inst.parent_func
            var_type = this_inst.var_type
            if parent_func is None\
                or len(parent_func) == 0\
                or var_type not in [SymType.FUNC_LOCAL_VAR, SymType.FUNC_ARG]:
                raise ValueError(f"Insufficient info for {var_name} in {parent_func}()")
            fun_info_dict = func_arg_and_local_var_lookup[parent_func]
            if var_type == SymType.FUNC_ARG:
                arg_list = fun_info_dict['args']
                if var_name not in arg_list:
                    raise ValueError(f"Not an arg: {var_name} in {parent_func}()")
                this_inst.payload = (arg_list.index(var_name) + 1) * 4
            if var_type == SymType.FUNC_LOCAL_VAR:
                local_list = fun_info_dict['locals']
                if var_name not in local_list:
                    raise ValueError(f"Not an local: {var_name} in {parent_func}()")
                this_inst.payload = (local_list.index(var_name) + 1) * -4
        else:
            raise ValueError(f"Unknown instruction: {this_inst}")

    user_str_addr = final_assembly_list[-1].addr + final_assembly_list[-1].opcode.length
    # Figrue out starting address of each string

    for key in user_strings_dict:
        user_strings_dict[key] = user_str_addr
        user_str_addr += len(key)

    for this_inst in final_assembly_list:
        if this_inst.opcode == OP_PUSHSTR:
            this_inst.opcode = OP_PUSHC16
            this_inst.payload = user_strings_dict[this_inst.payload]

    if print_asm:
        print("\n\n--------- Assembly Listing, Resolved: ---------")
        print_assembly_list(final_assembly_list)
        for key in user_strings_dict:
            print(f"{user_strings_dict[key]}   DATA: {key}")

    # ------------------ generate binary ------------------

    output_bin_array = bytearray()
    for this_inst in final_assembly_list:
        output_bin_array += this_inst.opcode.code.to_bytes(1, byteorder=endianness)
        this_payload = this_inst.payload
        if this_payload is None:
            continue
        if this_inst.opcode == OP_PUSHC8:
            output_bin_array += pack_to_one_byte(this_payload)
        elif this_inst.opcode == OP_PUSHC32:
            output_bin_array += pack_to_four_bytes(this_payload)
        else:
            output_bin_array += pack_to_two_bytes(this_payload)
    for key in user_strings_dict:
        output_bin_array += key
    if len(output_bin_array) > MAX_BIN_SIZE:
        raise ValueError("Binary size too large")
    return output_bin_array

pushc_instructions = {OP_PUSHC8, OP_PUSHC16, OP_PUSHC32}

def optimize_pass(instruction_list, arg_and_var_dict):
    optimized_list = []
    i = 0
    while i < len(instruction_list):
        current_instr = instruction_list[i]
        
        # Lookahead for peephole optimizations
        if i + 1 < len(instruction_list):
            next_instr = instruction_list[i + 1]
            
            # PUSH0 + DROP -> Remove both
            if current_instr.opcode == OP_PUSH0 and next_instr.opcode == OP_DROP:
                i += 2
                continue

            # POPI/POPR [X] + PUSHI/PUSHR [X] -> DUP + POPI/POPR [X]
            # This handles both Global (POPI) and Local (POPR) variables
            is_same_mem_save_load = (current_instr.opcode == OP_POPI and next_instr.opcode == OP_PUSHI) or (current_instr.opcode == OP_POPR and next_instr.opcode == OP_PUSHR)
            if is_same_mem_save_load and current_instr.payload == next_instr.payload:
                optimized_list.append(dsvm_instruction(opcode=OP_DUP))
                optimized_list.append(current_instr)
                i += 2
                continue

        # PUSHC16 0 -> PUSH0
        if current_instr.opcode in pushc_instructions and current_instr.payload == 0:
            optimized_list.append(dsvm_instruction(opcode=OP_PUSH0, label=current_instr.label, comment=current_instr.comment))
            i += 1
            continue
        if current_instr.opcode in pushc_instructions and current_instr.payload == 1:
            optimized_list.append(dsvm_instruction(opcode=OP_PUSH1, label=current_instr.label, comment=current_instr.comment))
            i += 1
            continue
        if current_instr.opcode == OP_ALLOC and current_instr.payload in arg_and_var_dict and len(arg_and_var_dict[current_instr.payload]['locals']) == 0:
            i += 1
            continue

        optimized_list.append(current_instr)
        i += 1
    
    return optimized_list

def optimize_full_assembly_from_context_dict(ctx_dict):
    arg_and_var_dict = ctx_dict['func_arg_and_local_var_lookup']
    ctx_dict["root_assembly_list"] = optimize_pass(ctx_dict["root_assembly_list"], arg_and_var_dict)
    for key in ctx_dict['func_assembly_dict']:
        ctx_dict['func_assembly_dict'][key] = optimize_pass(ctx_dict['func_assembly_dict'][key], arg_and_var_dict)

def replace_dummy_with_drop(instruction_list):
    for this_instruction in instruction_list:
        if this_instruction.opcode == OP_POPI and this_instruction.payload == DUMMY_VAR_NAME:
            this_instruction.opcode = OP_DROP
            this_instruction.payload = None

def drop_unused_functions(ctx_dict):
    ctx_dict['func_assembly_dict'] = {k: v for k, v in ctx_dict['func_assembly_dict'].items() if k in ctx_dict['func_visit_set']}

def replace_dummy_with_drop_from_context_dict(ctx_dict):
    replace_dummy_with_drop(ctx_dict["root_assembly_list"])
    for key in ctx_dict['func_assembly_dict']:
        replace_dummy_with_drop(ctx_dict['func_assembly_dict'][key])

def make_dsb_with_exception(program_listing, should_print=False):
    global global_context_dict
    global print_asm
    print_asm = should_print

    orig_listing = copy.deepcopy(program_listing)
    rdict = dsvm_preprocessor.run_all(program_listing)

    if rdict['is_success'] is False:
        comp_result = compile_result(
            is_success=False,
            error_comment=rdict.get("comments", ''),
            error_line_str = rdict.get('error_line_str', ''),
            error_line_number_starting_from_1=rdict.get('error_line_number_starting_from_1', 0)
        )
        return comp_result

    global_context_dict = rdict
    rdict["orig_listing"] = orig_listing
    post_pp_listing = rdict["dspp_listing_with_indent_level"]
    pyout = dsvm_ds2py.run_all(post_pp_listing)
    rdict["ds2py_listing"] = pyout
    if should_print:
        save_lines_to_file(post_pp_listing, "ppds.txt")
        save_lines_to_file(pyout, "pyds.py")
    source = dsline_to_source(pyout)
    try:
        my_tree = ast.parse(source, mode="exec")
    except SyntaxError as e:
        comp_result = compile_result(
            is_success = False,
            error_comment = e.msg,
            error_line_number_starting_from_1=get_orig_ds_lnumsf1_from_py_lnumsf1(rdict, e.lineno, onerr=0),
            error_line_str = e.text
        )
        return comp_result
    symtable_root = symtable.symtable(source, filename="ds2py", compile_type="exec")
    rdict["root_assembly_list"] = []
    rdict["root_assembly_list"].append(dsvm_instruction(OP_VMVER, payload=DS_VM_VERSION))
    rdict["symtable_root"] = symtable_root
    rdict['func_assembly_dict'] = {}
    rdict['func_args_dict'] = get_func_args(symtable_root)
    rdict['var_info_set'] = set()
    rdict['func_visit_set'] = set()

    for statement in my_tree.body:
        rdict["func_def_name"] = None
        rdict["caller_func_name"] = None
        dsvm_myast.postorder_walk(statement, visit_node, rdict)

    print("\n\n--------- Assembly Listing, Unoptimised, Unresolved: ---------")
    print_full_assembly_from_context_dict(rdict)
    rdict['func_arg_and_local_var_lookup'] = group_vars(rdict)
    drop_unused_functions(rdict)
    replace_dummy_with_drop_from_context_dict(rdict)
    optimize_full_assembly_from_context_dict(rdict)
    rdict["root_assembly_list"].append(dsvm_instruction(OP_HALT))

    bin_array = compile_to_bin(rdict)
    comp_result = compile_result(
        is_success=True,
        bin_array=bytes(bin_array)
    )
    return comp_result

def make_dsb_no_exception(program_listing, should_print=False):
    global print_asm
    print_asm = should_print
    try:
        return make_dsb_with_exception(program_listing, should_print)
    except Exception as e:
        print("MDNE:", traceback.format_exc())
        comp_result = compile_result(
            is_success=False,
            error_comment = str(e),
            error_line_number_starting_from_1 = global_context_dict.get('latest_orig_ds_lnum_sf1', 0),
            error_line_str = get_orig_ds_line_from_orig_ds_lnum_sf1(global_context_dict, global_context_dict.get('latest_orig_ds_lnum_sf1', ''))
        )
        return comp_result

def print_bin_output(binarr):
    if print_asm is False:
        return
    print("----- Binary output ------")
    for bbb in binarr:
        print(f"{bbb:02x}", end=" ")
    print()
    print()

# --------------------------

if __name__ == "__main__":
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

    comp_result = make_dsb_no_exception(program_listing, should_print=True)
    if comp_result.is_success is False:
        error_msg = (f"Error on Line {comp_result.error_line_number_starting_from_1}: {comp_result.error_comment}\n\t{comp_result.error_line_str}")
        print(error_msg)
        exit()

    print_bin_output(comp_result.bin_array)
    if len(sys.argv) >= 3:
        file_path = sys.argv[2]
        with open(file_path, 'wb') as file_out:
            bytes_written = file_out.write(comp_result.bin_array)
            print(f"Wrote {bytes_written} bytes to '{file_path}'")
    else:
        print("No output path provided; skipping file save.")