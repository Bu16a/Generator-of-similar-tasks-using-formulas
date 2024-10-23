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
    return symbols(' '.join(variables))


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
    random_values_list = []

    for i in range(count):
        # Копируем начальные уравнения
        eq_copy = equals.copy()

        # Для каждой неизвестной переменной генерируем случайное значение и добавляем уравнение
        random_values = {}
        for var in _all_unknown_vars:
            random_value = round(random.uniform(1, 100), 2)
            random_values[var] = random_value  # Запоминаем случайные значения
            eq_copy.append(Eq(var, random_value))  # Добавляем уравнение вида var = random_value

        # Подставляем случайные значения в исходные уравнения
        eq_with_values = [eq.subs(random_values) for eq in eq_copy]

        # Решаем уравнение с текущим набором данных
        solutions = solve(eq_with_values, _find_vars)
        results.append(solutions)
        random_values_list.append(random_values)

    return results, random_values_list


# Основной код программы
n = int(input("Введите количество уравнений: "))
eq = []
eq_input = ''

for i in range(n):
    eq_i, eq_input_i = process_input()
    eq.append(eq_i)
    eq_input += eq_input_i

variables = find_variables(eq_input)
known_values = get_known_variables(variables)

# Добавляем уравнения для известных переменных (если они введены)
for key in known_values.keys():
    eq.append(Eq(key, known_values[key]))

# Определяем неизвестные переменные
all_unknown_vars = [var for var in variables if var not in known_values]
find_vars = process_which(all_unknown_vars)

# Исключаем переменные, которые нужно найти, из списка тех, для которых нужно генерировать случайные значения
all_unknown_vars = [var for var in all_unknown_vars if var not in find_vars]

# Указываем количество заданий
count = int(input("Введите количество заданий: "))

# Генерируем решения и случайные значения
solutions, random_values_list = generation_solutions(eq, find_vars, count, all_unknown_vars)

# Подготавливаем данные для вывода в таблице
header = [str(var) for var in (all_unknown_vars + find_vars)]  # Заголовок таблицы

table = []
for i in range(count):
    random_values = random_values_list[i]
    solution = solutions[i]

    # Обрабатываем как случай, если решение - это словарь, так и если это список
    row_values = []
    if isinstance(solution, dict):
        # Если решение в виде словаря
        row_values = [random_values.get(var, solution.get(var, '-')) for var in (all_unknown_vars + find_vars)]
    elif isinstance(solution, list):
        # Если решение в виде списка
        row_values = [random_values.get(var, solution[i] if i < len(solution) else '-') for i, var in enumerate(all_unknown_vars + find_vars)]
    else:
        # Если решение - это единичное значение
        row_values = [random_values.get(var, solution) for var in (all_unknown_vars + find_vars)]

    table.append(row_values)

# Выводим таблицу с помощью tabulate
print(tabulate(table, headers=header, tablefmt="grid", numalign="center", floatfmt=".4f"))
