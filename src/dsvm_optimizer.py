import ast
import operator
from dsvm_common import *

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

def replace_dummy_with_drop_from_context_dict(ctx_dict):
    replace_dummy_with_drop(ctx_dict["root_assembly_list"])
    for key in ctx_dict['func_assembly_dict']:
        replace_dummy_with_drop(ctx_dict['func_assembly_dict'][key])

"""
Performs dead function elimination and constant folding
Only on operators unaffected by `_UNSIGNED_MODE`
"""


def c_style_div(a, b):
    return int(a / b)

def c_style_mod(a, b):
    return int(math.fmod(a, b))

def optimize_ast(tree, remove_unused_func=True):
    # --- Step 1: Reachability Analysis (Conditional) ---
    live_funcs = set()
    
    if remove_unused_func:
        # Map function names to their FunctionDef nodes
        defined_funcs = {
            node.name: node 
            for node in tree.body 
            if isinstance(node, ast.FunctionDef)
        }

        # Queue for BFS/DFS traversal. Start with the "Main" body.
        worklist = [node for node in tree.body if not isinstance(node, ast.FunctionDef)]
        
        def get_calls_from_nodes(nodes):
            calls = []
            for node in nodes:
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            calls.append(child.func.id)
            return calls

        # Process the worklist to find all reachable functions
        while worklist:
            current_node = worklist.pop()
            called_names = get_calls_from_nodes([current_node])
            
            for name in called_names:
                if name in defined_funcs and name not in live_funcs:
                    live_funcs.add(name)
                    worklist.append(defined_funcs[name])

    # --- Step 2: AST Transformation ---

    class DuckyOptimizer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            # 1. Dead Code Elimination
            if remove_unused_func and node.name not in live_funcs:
                return None
            return self.generic_visit(node)

        def visit_BinOp(self, node):
            # Optimize children first
            self.generic_visit(node)

            # 2. Constant Folding for Binary Operators
            if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
                if isinstance(node.left.value, int) and isinstance(node.right.value, int):
                    try:
                        val = self._apply_bin_op(node.op, node.left.value, node.right.value)
                        # Check if optimization was possible (val is not None)
                        if val is not None:
                            # Cast to int to ensure type consistency (e.g. for division)
                            return ast.Constant(value=int(val))
                    except (ZeroDivisionError, OverflowError):
                        # Leave the node as is if it causes a runtime error (let the runtime handle it)
                        pass
            return node

        def visit_Compare(self, node):
            # Optimize children first
            self.generic_visit(node)
            
            # 3. Constant Folding for Comparisons
            if len(node.ops) == 1 and len(node.comparators) == 1:
                left = node.left
                right = node.comparators[0]
                op = node.ops[0]
                
                if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
                     if isinstance(left.value, int) and isinstance(right.value, int):
                        try:
                            val = self._apply_cmp_op(op, left.value, right.value)
                            if val is not None:
                                # Convert boolean result to integer (1 or 0)
                                return ast.Constant(value=int(val)) 
                        except Exception:
                            pass
            return node

        def visit_BoolOp(self, node):
            self.generic_visit(node)
            # Constant Folding for Logical Operators (LOGIAND, LOGIOR)
            if all(isinstance(v, ast.Constant) for v in node.values):
                raw_values = [v.value for v in node.values]
                final_val = 0
                if isinstance(node.op, ast.And):
                    final_val = 1 if all(raw_values) else 0
                elif isinstance(node.op, ast.Or):
                    final_val = 1 if any(raw_values) else 0
                return ast.Constant(value=final_val)
            return node
        
        # --- Operator Mapping Helpers ---

        def _apply_bin_op(self, op, left, right):
            ops = {
                # Arithmetic
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Pow: operator.pow,
                ast.Div: c_style_div,     
                ast.FloorDiv: c_style_div,
                ast.Mod: c_style_mod,         
                
                # Bitwise / Shifts
                ast.LShift: operator.lshift,   # LSL
                ast.RShift: operator.rshift,   # ASR (Python >> is arithmetic on signed ints)
                ast.BitOr: operator.or_,       # BITOR
                ast.BitXor: operator.xor,      # BITXOR
                ast.BitAnd: operator.and_,     # BITAND
            }
            op_type = type(op)
            if op_type in ops:
                return ops[op_type](left, right)
            return None

        def _apply_cmp_op(self, op, left, right):
            ops = {
                ast.Eq: operator.eq,   
                ast.NotEq: operator.ne,
                ast.Lt: operator.lt,   
                ast.LtE: operator.le,  
                ast.Gt: operator.gt,   
                ast.GtE: operator.ge,  
            }
            op_type = type(op)
            if op_type in ops:
                return ops[op_type](left, right)
            return None

    optimizer = DuckyOptimizer()
    new_tree = optimizer.visit(tree)
    ast.fix_missing_locations(new_tree)
    
    return new_tree