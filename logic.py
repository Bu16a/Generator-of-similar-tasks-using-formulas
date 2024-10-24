import random
import re
from sympy import symbols, Eq, solve, sympify
from tabulate import tabulate


def parse_equation(equation):
    equation = re.sub(r'\^', '**', equation)
    equation = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation)
    equation = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', equation)
    return equation


def find_variables(equation):
    variables = set(re.findall(r'[a-zA-Z]', equation))
    res = symbols(' '.join(variables))
    if isinstance(res, list) or isinstance(res, tuple):
        return res
    return [res]


def process_input():
    while True:
        eq_input = input("Введите уравнение в формате ... = ... : ")

        if eq_input.count('=') != 1:
            print("Ошибка: должно быть одно и только одно '='.")
            continue

        left_side, right_side = eq_input.split('=')

        left_parsed = parse_equation(left_side.strip())
        right_parsed = parse_equation(right_side.strip())

        try:
            left_sympy = sympify(left_parsed)
            right_sympy = sympify(right_parsed)
            return Eq(left_sympy, right_sympy), eq_input
        except Exception as e:
            print(f"Ошибка при парсинге уравнения: {e}")
            print("Попробуйте ввести уравнение ещё раз.")


def get_known_variables(variables):
    known_values = {}
    for var in variables:
        while True:
            try:
                value = input(f"Введите значение для переменной {var} (или нажмите Enter, чтобы пропустить): ")
                if value.strip():
                    known_values[var] = float(value)
                break
            except Exception as e:
                print("Попробуйте ввести переменную ещё раз")
    return known_values


def process_which(vars):
    result = []
    for var in vars:
        value = input(f"Введите да если эта переменная неизвестна {var} (или нажмите Enter, чтобы пропустить): ")
        if value.lower() == 'да':
            result.append(var)
    return result


def generation_solutions(equals, _find_vars, count, _all_unknown_vars):
    results = []

    for i in range(count):
        eq_copy = equals.copy()
        for var in _all_unknown_vars:
            random_value = round(random.uniform(1, 100), 2)
            eq_copy.append(Eq(var, random_value))

        solutions = solve(eq_copy, _find_vars)
        results.append(solutions)
    return results


n = int(input("Введите количество уравнений: "))
eq = []
eq_input = ''

for i in range(n):
    eq_i, eq_input_i = process_input()
    eq.append(eq_i)
    eq_input += eq_input_i

variables = find_variables(eq_input)
known_values = get_known_variables(variables)

for key in known_values.keys():
    eq.append(Eq(key, known_values[key]))

all_unknown_vars = [var for var in variables if var not in known_values]
find_vars = process_which(all_unknown_vars)

all_unknown_vars = [var for var in all_unknown_vars if var not in find_vars]

count = int(input("Введите количество заданий: "))

solutions = generation_solutions(eq, variables, count, all_unknown_vars)

header = [str(var) for var in variables]

table = []
for solution in solutions:
    row_values = []
    for var in variables:
        if var in known_values:
            row_values.append(known_values[var])
        elif isinstance(solution, dict) and var in solution:
            value = solution[var]
            if isinstance(value, (list, tuple)):
                row_values.append(', '.join(map(str, value)))
            else:
                row_values.append(value)
        elif isinstance(solution, list):
            ind = variables.index(var)
            elem = []
            for j in solution:
                elem.append(j[ind])
            row_values.append(elem)
        else:
            row_values.append('-')

    table.append(row_values)

print(tabulate(table, headers=header, tablefmt="grid", numalign="center", floatfmt=".4f"))
