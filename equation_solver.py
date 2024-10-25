import random
import re
from sympy import symbols, Eq, solve


class EquationSolver:
    @staticmethod
    def parse_equation(equation):
        equation = re.sub(r'\^', '**', equation)
        equation = re.sub(r'(\d)([a-zA-Z])', r'\1 * \2', equation)
        return equation

    @staticmethod
    def find_variables(equation):
        variables = set(re.findall(r'[a-zA-Z]+', equation))

        math_functions = {'sin', 'cos', 'log', 'tan', 'exp', 'sqrt'}
        variables -= math_functions

        res = symbols(' '.join(variables))
        return res if isinstance(res, (list, tuple)) else [res]

    @staticmethod
    def generation_solutions(equations, find_vars, count, all_unknown_vars, ranges):
        results = []
        for i in range(count):
            eq_copy = equations.copy()
            for var in all_unknown_vars:
                var_range = ranges.get(var, (1, 100))
                random_value = round(random.uniform(*var_range), 2)
                eq_copy.append(Eq(var, random_value))
            solutions = solve(eq_copy, find_vars)
            results.append(solutions)
        return results
