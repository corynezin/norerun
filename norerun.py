import ast
import sys
import time
import collections


filename = sys.argv[1]
debug = False


def log_code(code):
    print(code)
    with open("log.py", "a") as f:
        f.write(code)
        f.write("\n")


def dictify(node):
    if isinstance(node, ast.AST):
        res = vars(node).copy()
        for k in "lineno", "col_offset", "end_lineno", "end_col_offset", "ctx":
            res.pop(k, None)
        for k, v in res.items():
            res[k] = dictify(v)
        res["__type__"] = type(node).__name__
        return res
    elif isinstance(node, list):
        return [dictify(n) for n in node]
    elif isinstance(node, dict):
        return {k: dictify(v) for k, v in node.items()}
    else:
        return node


def get_calls(ast_dict):
    if isinstance(ast_dict, list):
        for node in ast_dict:
            for call in get_calls(node):
                yield call
    elif isinstance(ast_dict, dict):
        if "__type__" in ast_dict and ast_dict["__type__"] == "Call":
            if "id" in ast_dict["func"]:
                yield ast_dict["func"]["id"]
        for nodename, nodevalue in ast_dict.items():
            for call in get_calls(nodevalue):
                yield call


if __name__ == "__main__":
    old_functions = {}  # old function definitions
    old_assignments = {}  # old assignments statments
    source_to_targets = collections.defaultdict(
        set
    )  # source variables to targets
    target_to_func = {}  # target variable to func that produces it
    dep_to_func = None  # function to dependent functions
    dirty_vars = None  # variables which need to be updated
    dirty_funcs = None  # functions which need to be updated

    while True:
        dirty_vars = set()
        dirty_funcs = set()
        dep_to_func = collections.defaultdict(list)

        with open(filename) as f:
            try:
                module = ast.parse(f.read())
            except SyntaxError as exc:
                command = input(f"Error: {exc} press enter to continue")
                continue

        new_functions = {}
        new_assignments = collections.OrderedDict()

        for statement in module.body:
            if isinstance(statement, ast.FunctionDef):
                new_functions[statement.name] = statement
                calls = list(get_calls(dictify(statement)))
                for call in calls:
                    dep_to_func[call].append(statement.name)
            elif isinstance(statement, ast.Assign) and isinstance(
                statement.value, ast.Call
            ):
                for target in statement.targets:
                    new_assignments[target.id] = statement
                    for arg in statement.value.args:
                        if isinstance(arg, ast.Name):
                            source_to_targets[arg.id].add(target.id)
                target_to_func[target.id] = statement.value.func.id
            else:
                print(f"WARNING: statement not supported for tracking: {ast.unparse(statement)}")
                code = ast.unparse(statement)
                try:
                    log_code(code)
                    exec(code)
                except Exception as exc:
                    print(f"error: {exc}")
                    continue

        dict_new_functions = dictify(new_functions)
        dict_old_functions = dictify(old_functions)
        # Redefine functions and mark targets as dirty
        for key in dict_new_functions:
            if dict_old_functions.get(key) != dict_new_functions.get(key):
                dirty_funcs.add(key)
                for func in dep_to_func[key]:
                    dirty_funcs.add(func)
                function_ast = new_functions[key]
                code = ast.unparse(function_ast)
                try:
                    log_code(code)
                    exec(code)
                except Exception as exc:
                    print(f"error: {exc}")
                    continue

        # Mark targets for assignments that have changed
        for target in target_to_func:
            if target_to_func[target] in dirty_funcs:
                dirty_vars.add(target)
        for target in new_assignments:
            if dictify(old_assignments.get(target)) != dictify(
                new_assignments.get(target)
            ):
                dirty_vars.add(target)
        for dirty_var in set(dirty_vars):

            def set_dirty(target):
                for var in source_to_targets.get(target, []):
                    dirty_vars.add(var)
                    set_dirty(var)

            set_dirty(dirty_var)
        for var in new_assignments:
            if var in dirty_vars:
                dirty_vars.remove(var)
                function_ast = new_assignments[var]
                code = ast.unparse(function_ast)
                try:
                    log_code(code)
                    exec(code)
                except Exception as exc:
                    print(f"error: {exc}")
                    continue
        if debug:
            print(f"dirty_vars: {dirty_vars}")
            print(f"dirty_funcs: {dirty_funcs}")

        old_functions = new_functions
        old_assignments = new_assignments
        command = None
        while True:
            try:
                command = input(">>> ")
                if command == "debug":
                    breakpoint()
                if not command or command == "continue":
                    break
                print(eval(command))
            except Exception as exc:
                print(f"error: {exc}")
                break
