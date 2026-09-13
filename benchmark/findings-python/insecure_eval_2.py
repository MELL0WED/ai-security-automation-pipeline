def run_user_formula(formula, variables):
    return eval(formula, {"__builtins__": {}}, variables)
