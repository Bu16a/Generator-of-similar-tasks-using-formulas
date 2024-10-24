import tkinter as tk
from tkinter import messagebox, filedialog
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
    return res if isinstance(res, list) or isinstance(res, tuple) else [res]


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


def create_equation_input_window():
    def submit_equations():
        eq_input = eq_text.get("1.0", tk.END).strip().splitlines()

        equations = []
        for equation in eq_input:
            if equation:
                if equation.count('=') != 1:
                    messagebox.showerror("Ошибка", "Должно быть одно и только одно '='.")
                    return
                left_side, right_side = equation.split('=')
                left_parsed = parse_equation(left_side.strip())
                right_parsed = parse_equation(right_side.strip())

                try:
                    left_sympy = sympify(left_parsed)
                    right_sympy = sympify(right_parsed)
                    equations.append(Eq(left_sympy, right_sympy))
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при парсинге уравнения: {e}")
                    return

        if not equations:
            messagebox.showerror("Ошибка", "Необходимо ввести хотя бы одно уравнение.")
            return

        variables = find_variables("\n".join(eq_input))

        # После ввода уравнений переходим к следующему шагу
        window.destroy()
        create_variable_input_window(equations, variables)

    # Создаем главное окно
    window = tk.Tk()
    window.title("Ввод уравнений")

    # Поле для ввода уравнений
    tk.Label(window, text="Введите уравнения в формате ... = ... :").pack()
    eq_text = tk.Text(window, height=10, width=50)
    eq_text.pack()

    # Кнопка для подтверждения уравнений
    submit_button = tk.Button(window, text="Подтвердить уравнения", command=submit_equations)
    submit_button.pack()

    window.mainloop()


def create_variable_input_window(equations, variables):
    def submit_variables():
        known_values = {}
        unknown_vars = []

        # Собираем значения известных переменных
        for var in variables:
            value = known_vars_entries[var].get().strip()
            if value:
                try:
                    known_values[var] = float(value)
                except ValueError:
                    messagebox.showerror("Ошибка", f"Некорректное значение для переменной {var}.")
                    return

        # Определяем неизвестные переменные
        for var in variables:
            if unknown_vars_checkbuttons[var].get() == 1:
                unknown_vars.append(var)

        # После сбора данных переходим к следующему шагу
        window.destroy()
        create_solution_window(equations, variables, known_values, unknown_vars)

    # Создаем окно для ввода переменных
    window = tk.Tk()
    window.title("Введите переменные")

    known_vars_entries = {}
    unknown_vars_checkbuttons = {}

    tk.Label(window, text="Введите значения известных переменных и отметьте неизвестные:").pack()

    for var in variables:
        frame = tk.Frame(window)
        frame.pack(fill=tk.X)

        tk.Label(frame, text=f"{var}: ").pack(side=tk.LEFT)

        # Поле для ввода значения известной переменной
        entry = tk.Entry(frame)
        entry.pack(side=tk.LEFT)
        known_vars_entries[var] = entry

        # Чекбокс для отметки неизвестной переменной
        var_var = tk.IntVar()
        unknown_vars_checkbuttons[var] = var_var
        checkbox = tk.Checkbutton(frame, text="Неизвестная", variable=var_var)
        checkbox.pack(side=tk.RIGHT)

    # Кнопка для перехода к следующему шагу
    submit_button = tk.Button(window, text="Далее", command=submit_variables)
    submit_button.pack()

    window.mainloop()


def create_solution_window(equations, variables, known_values, unknown_vars):
    def generate_solutions():
        count = int(count_entry.get())
        all_unknown_vars = [var for var in variables if var not in known_values]
        find_vars = [var for var in unknown_vars if var not in known_values]
        all_unknown_vars = [var for var in all_unknown_vars if var not in find_vars]

        for key in known_values.keys():
            equations.append(Eq(key, known_values[key]))

        solutions = generation_solutions(equations, variables, count, all_unknown_vars)

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
                    elem = [j[ind] for j in solution]
                    row_values.append(elem)
                else:
                    row_values.append('-')
            table.append(row_values)

        # Выводим решения в консоль
        print(tabulate(table, headers=header, tablefmt="grid", numalign="center", floatfmt=".4f"))

        # Показать в окне и предложить сохранить
        solutions_text.set(tabulate(table, headers=header, tablefmt="grid", numalign="center", floatfmt=".4f"))

    def save_solutions():
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'w') as f:
                f.write(solutions_text.get())

    def next_task():
        window.destroy()
        create_equation_input_window()

    # Создаем окно для вывода решений
    window = tk.Tk()
    window.title("Решения уравнений")

    tk.Label(window, text="Введите количество заданий:").pack()
    count_entry = tk.Entry(window)
    count_entry.pack()

    solutions_text = tk.StringVar()
    tk.Label(window, textvariable=solutions_text, justify="left", font=("Courier", 10)).pack()

    # Кнопки для генерации решений, сохранения и следующего задания
    generate_button = tk.Button(window, text="Сгенерировать решения", command=generate_solutions)
    generate_button.pack()

    save_button = tk.Button(window, text="Сохранить решения", command=save_solutions)
    save_button.pack()

    next_button = tk.Button(window, text="Следующее задание", command=next_task)
    next_button.pack()

    window.mainloop()


if __name__ == "__main__":
    create_equation_input_window()
