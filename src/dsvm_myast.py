import sys
import ast
import symtable
import copy
from dsvm_common import *

def find_function_table(root: symtable.SymbolTable, func_name: str):
    for child in root.get_children():
        if child.get_type() == 'function' and child.get_name() == func_name:
            return child
        found = find_function_table(child, func_name)
        if found is not None:
            return found
    return None

def how_many_args(func_name, ctx_dict):
    args_list = ctx_dict['func_args_dict'].get(func_name)
    if args_list is None:
        return None
    return len(args_list)

def print_node_info(node):
    lineno = getattr(node, "lineno", None)
    print(f"---Line {lineno}: {type(node)}---")
    for item in node._fields:
        if getattr(node, item, None) is not None:
            print(f"{item}: {getattr(node, item, None)}")
    print()

AST_LEAF_NODES = (
    ast.Name,
)

@dataclass(frozen=True, slots=True)
class add_alloc:
    func_name : str = ""

@dataclass(frozen=True, slots=True)
class add_nop:
    label: str = ""

@dataclass(frozen=True, slots=True)
class add_jmp:
    label: str = ""

@dataclass(frozen=True, slots=True)
class add_push0:
    label: str = ""

@dataclass(frozen=True, slots=True)
class add_default_return:
    arg_count: int = 0

def is_leaf(node):
    if isinstance(node, AST_LEAF_NODES):
        return True
    return not any(ast.iter_child_nodes(node))

def postorder_walk(node, action, ctx_dict):
    this_pylnum_sf1 = getattr(node, "lineno", None)
    this_orig_ds_lnum_sf1 = get_orig_ds_lnumsf1_from_py_lnumsf1(ctx_dict, this_pylnum_sf1)
    if this_orig_ds_lnum_sf1 is not None:
        ctx_dict['latest_orig_ds_lnum_sf1'] = this_orig_ds_lnum_sf1
    if isinstance(node, ast.Expr):
        postorder_walk(node.value, action, ctx_dict)
    elif isinstance(node, ast.BinOp):
        # Push args right-to-left
        postorder_walk(node.right, action, ctx_dict)
        postorder_walk(node.left, action, ctx_dict)
        postorder_walk(node.op, action, ctx_dict)
    elif isinstance(node, ast.BoolOp):
        for item in reversed(node.values):
            postorder_walk(item, action, ctx_dict)
        for x in range(len(node.values) - 1):
            postorder_walk(node.op, action, ctx_dict)
    elif isinstance(node, ast.UnaryOp):
        postorder_walk(node.operand, action, ctx_dict)
        postorder_walk(node.op, action, ctx_dict)
    elif isinstance(node, ast.Compare):
        if len(node.comparators) > 1 or len(node.ops) > 1:
            raise ValueError("Multiple Comparators")
        print_node_info(node)
        postorder_walk(node.comparators[0], action, ctx_dict)
        postorder_walk(node.left, action, ctx_dict)
        postorder_walk(node.ops[0], action, ctx_dict)
    elif isinstance(node, ast.Assign):
        postorder_walk(node.value, action, ctx_dict)
        if len(node.targets) != 1:
            raise ValueError("Multiple Assignments")
        postorder_walk(node.targets[0], action, ctx_dict)
    elif isinstance(node, ast.FunctionDef):
        func_name = node.name
        this_func_label = f"func_{func_name}"
        this_arg_count = how_many_args(func_name, ctx_dict)
        if this_arg_count is None:
            raise ValueError(f"Invalid args")
        if this_arg_count > DSVM_FUNC_ARG_MAX_SIZE:
            raise ValueError(f"Too many args")
        ctx_dict['func_def_name'] = func_name
        action(add_nop(this_func_label), ctx_dict)
        action(add_alloc(func_name), ctx_dict)
        for item in node.body:
            postorder_walk(item, action, ctx_dict)
        action(add_default_return(this_arg_count), ctx_dict)
    elif isinstance(node, ast.Return):
        if node.value is None:
            action(add_push0(), ctx_dict)
        else:
            postorder_walk(node.value, action, ctx_dict)
        action(node, ctx_dict)
    elif isinstance(node, ast.AugAssign):
        print_node_info(node) # target op value
        target_load = copy.deepcopy(node.target)
        target_load.ctx = ast.Load()
        postorder_walk(node.value, action, ctx_dict)
        postorder_walk(target_load, action, ctx_dict)
        postorder_walk(node.op, action, ctx_dict)
        postorder_walk(node.target, action, ctx_dict)
    elif isinstance(node, ast.If):
        if_skip_label = f"{node.__class__.__name__}_skip@{this_orig_ds_lnum_sf1}"
        if_end_label = f"{node.__class__.__name__}_end@{this_orig_ds_lnum_sf1}"
        if len(node.orelse) == 0:
            if_skip_label = if_end_label
        ctx_dict['if_destination_label'] = if_skip_label
        postorder_walk(node.test, action, ctx_dict)
        action(node, ctx_dict)
        for item in node.body:
            postorder_walk(item, action, ctx_dict)
        if len(node.orelse):
            action(add_jmp(if_end_label), ctx_dict)
            action(add_nop(if_skip_label), ctx_dict)
            for item in node.orelse:
                postorder_walk(item, action, ctx_dict)
        action(add_nop(if_end_label), ctx_dict)
    elif isinstance(node, ast.While):
        while_start_label = f"{node.__class__.__name__}_start@{this_orig_ds_lnum_sf1}"
        while_end_label = f"{node.__class__.__name__}_end@{this_orig_ds_lnum_sf1}"
        action(add_nop(while_start_label), ctx_dict)
        postorder_walk(node.test, action, ctx_dict)
        ctx_dict['while_start_label'] = while_start_label
        ctx_dict['while_end_label'] = while_end_label
        action(node, ctx_dict)
        for item in node.body:
            postorder_walk(item, action, ctx_dict)
        action(add_jmp(while_start_label), ctx_dict)
        action(add_nop(while_end_label), ctx_dict)
    elif isinstance(node, ast.Call):
        func_name = node.func.id
        caller_arg_count = len(node.args)
        if len(node.keywords) != 0:
            raise ValueError("Invalid arguments")
        if func_name in ds_reserved_funcs:
            callee_arg_count = ds_reserved_funcs[func_name].arg_len
        else:
            callee_arg_count = how_many_args(func_name, ctx_dict)
        if callee_arg_count is None:
            raise ValueError(f"Function {func_name}() not found")
        if caller_arg_count != callee_arg_count:
            raise ValueError("Wrong number of arguments")
        ctx_dict["caller_func_name"] = func_name
        # Push args right-to-left
        for item in reversed(node.args):
            postorder_walk(item, action, ctx_dict)
        action(node, ctx_dict)
    elif is_leaf(node):
        action(node, ctx_dict)
    else:
        raise ValueError(f"Unknown AST Node: {node}")
