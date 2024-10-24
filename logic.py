import tkinter as tk
from tkinter import messagebox, filedialog
import random
import re
from sympy import symbols, Eq, solve, sympify
from tabulate import tabulate


class EquationSolver:
    @staticmethod
    def parse_equation(equation):
        equation = re.sub(r'\^', '**', equation)
        equation = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation)
        equation = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', equation)
        return equation

    @staticmethod
    def find_variables(equation):
        variables = set(re.findall(r'[a-zA-Z]', equation))
        res = symbols(' '.join(variables))
        return res if isinstance(res, list) or isinstance(res, tuple) else [res]

    @staticmethod
    def generation_solutions(equations, find_vars, count, all_unknown_vars, ranges):
        results = []
        for i in range(count):
            eq_copy = equations.copy()
            for var in all_unknown_vars:
                # Получаем диапазон для текущей переменной
                var_range = ranges.get(var, (1, 100))  # По умолчанию диапазон от 1 до 100
                random_value = round(random.uniform(*var_range), 2)
                eq_copy.append(Eq(var, random_value))
            solutions = solve(eq_copy, find_vars)
            results.append(solutions)
        return results


class EquationInputWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Ввод уравнений")
        self.eq_text = tk.Text(self.master, height=10, width=50)

        tk.Label(self.master, text="Введите уравнения в формате ... = ... :").pack()
        self.eq_text.pack()

        submit_button = tk.Button(self.master, text="Подтвердить уравнения", command=self.submit_equations)
        submit_button.pack()

    def submit_equations(self):
        eq_input = self.eq_text.get("1.0", tk.END).strip().splitlines()
        equations = []

        for equation in eq_input:
            if equation:
                if equation.count('=') != 1:
                    messagebox.showerror("Ошибка", "Должно быть одно и только одно '='.")
                    return
                left_side, right_side = equation.split('=')
                left_parsed = EquationSolver.parse_equation(left_side.strip())
                right_parsed = EquationSolver.parse_equation(right_side.strip())

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

        variables = EquationSolver.find_variables("\n".join(eq_input))
        self.master.destroy()
        VariableInputWindow(equations, variables)


class VariableInputWindow:
    def __init__(self, equations, variables):
        self.equations = equations
        self.variables = variables
        self.known_vars_entries = {}
        self.unknown_vars_checkbuttons = {}
        self.ranges_entries = {}

        self.master = tk.Tk()
        self.master.title("Введите переменные")

        tk.Label(self.master, text="Введите значения известных переменных и отметьте неизвестные:").pack()

        for var in variables:
            frame = tk.Frame(self.master)
            frame.pack(fill=tk.X)

            tk.Label(frame, text=f"{var}: ").pack(side=tk.LEFT)

            entry = tk.Entry(frame)
            entry.pack(side=tk.LEFT)
            self.known_vars_entries[var] = entry

            var_var = tk.IntVar()
            self.unknown_vars_checkbuttons[var] = var_var
            checkbox = tk.Checkbutton(frame, text="Неизвестная", variable=var_var)
            checkbox.pack(side=tk.RIGHT)

            tk.Label(frame, text="Диапазон: ").pack(side=tk.LEFT)
            range_entry = tk.Entry(frame, width=10)
            range_entry.pack(side=tk.LEFT)
            self.ranges_entries[var] = range_entry

        submit_button = tk.Button(self.master, text="Далее", command=self.submit_variables)
        submit_button.pack()

    def submit_variables(self):
        known_values = {}
        unknown_vars = []
        ranges = {}

        for var in self.variables:
            value = self.known_vars_entries[var].get().strip()
            if value:
                try:
                    known_values[var] = float(value)
                except ValueError:
                    messagebox.showerror("Ошибка", f"Некорректное значение для переменной {var}.")
                    return

            # Получаем диапазон для неизвестных переменных
            range_value = self.ranges_entries[var].get().strip()
            if range_value:
                try:
                    low, high = map(float, range_value.split(','))
                    ranges[var] = (low, high)
                except ValueError:
                    messagebox.showerror("Ошибка",
                                         f"Некорректный диапазон для переменной {var}. Используйте формат 'min,max'.")
                    return

        for var in self.variables:
            if self.unknown_vars_checkbuttons[var].get() == 1:
                unknown_vars.append(var)

        self.master.destroy()
        SolutionWindow(self.equations, self.variables, known_values, unknown_vars, ranges)


class SolutionWindow:
    def __init__(self, equations, variables, known_values, unknown_vars, ranges):
        self.equations = equations
        self.variables = variables
        self.known_values = known_values
        self.unknown_vars = unknown_vars
        self.ranges = ranges

        self.master = tk.Tk()
        self.master.title("Решения уравнений")

        self.solutions_text = tk.StringVar()

        tk.Label(self.master, text="Введите количество заданий:").pack()
        self.count_entry = tk.Entry(self.master)
        self.count_entry.pack()

        self.table_frame = tk.Frame(self.master)
        self.table_frame.pack()

        tk.Label(self.master, textvariable=self.solutions_text, justify="left", font=("Courier", 10)).pack()

        generate_button = tk.Button(self.master, text="Сгенерировать решения", command=self.generate_solutions)
        generate_button.pack()

        self.task_window_button = tk.Button(self.master, text="Генерация заданий", command=self.open_task_window)
        self.task_window_button.pack()

        save_button = tk.Button(self.master, text="Сохранить решения", command=self.save_solutions)
        save_button.pack()

        next_button = tk.Button(self.master, text="Следующее задание", command=self.next_task)
        next_button.pack()

        self.all_unknown_vars = []

    def generate_solutions(self):
        count = int(self.count_entry.get())
        all_unknown_vars = [var for var in self.variables if var not in self.known_values]
        find_vars = [var for var in self.unknown_vars if var not in self.known_values]
        self.all_unknown_vars = [var for var in all_unknown_vars if var not in find_vars]

        for key in self.known_values.keys():
            self.equations.append(Eq(key, self.known_values[key]))

        # Передаем диапазоны в функцию генерации решений
        self.solutions = EquationSolver.generation_solutions(self.equations, self.variables,
                                                             count, self.all_unknown_vars, self.ranges)

        header = [str(var) for var in self.variables]
        table = []
        for solution in self.solutions:
            row_values = []
            for var in self.variables:
                if var in self.known_values:
                    row_values.append(self.known_values[var])
                elif isinstance(solution, dict) and var in solution:
                    value = solution[var]
                    if isinstance(value, (list, tuple)):
                        # Распаковываем элементы списка
                        row_values.extend([float(str(v).rstrip('0').rstrip('.')) for v in value])
                    else:
                        row_values.append(float(str(value).rstrip('0').rstrip('.')))
                elif isinstance(solution, list):
                    ind = self.variables.index(var)
                    # Получаем значения из списка, распаковывая их
                    elem = [float(str(j[ind]).rstrip('0').rstrip('.')) for j in solution]
                    row_values.extend(elem)  # Распаковка в строку таблицы
                else:
                    row_values.append('-')
            table.append(row_values)

        result_text = tabulate(table, headers=header, tablefmt="grid", numalign="center", floatfmt=".4f")
        print(result_text)
        self.solutions_text.set(result_text)

    def open_task_window(self):
        TaskWindow(self.all_unknown_vars, self.solutions, self.unknown_vars)

    def save_solutions(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'w') as f:
                f.write(self.solutions_text.get())

    def next_task(self):
        self.master.destroy()
        EquationInputWindow(tk.Tk())


class TaskWindow:
    def __init__(self, all_unknown_vars, solutions, _uncnowns):
        self.all_unknown_vars = all_unknown_vars
        self.solutions = solutions
        self.uncnowns = _uncnowns
        self.master = tk.Tk()
        self.master.title("Генерация заданий")

        # Заголовок с доступными переменными
        var_label = tk.Label(self.master,
                             text="Доступные переменные: " + ", ".join(str(var) for var in self.all_unknown_vars)
                                  + '\nОтветы: ' + ", ".join(str(var) for var in self.uncnowns))
        var_label.pack()

        # Многострочное поле для ввода задачи
        tk.Label(self.master, text="Введите текст задачи с переменными в формате {переменная}:").pack()
        self.task_input = tk.Text(self.master, height=5, width=50)
        self.task_input.pack(pady=10)

        generate_button = tk.Button(self.master, text="Генерация заданий", command=self.generate_tasks)
        generate_button.pack()

        self.output_frame = tk.Frame(self.master)
        self.output_frame.pack(pady=10)

        self.output_text = tk.Text(self.output_frame, height=10, width=50)
        self.output_text.pack(side=tk.LEFT)

        save_button = tk.Button(self.master, text="Сохранить задания", command=self.save_tasks)
        save_button.pack(pady=5)

        scroll_bar = tk.Scrollbar(self.output_frame)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.output_text.yview)

    def generate_tasks(self):
        task_template = self.task_input.get("1.0", tk.END).strip()
        if not task_template:
            messagebox.showerror("Ошибка", "Введите текст задачи.")
            return

        tasks = []
        for solution in self.solutions:
            task = task_template
            for var in self.all_unknown_vars:
                value = solution.get(var, None)
                if value is not None:
                    task = task.replace(f'{{{var}}}', str(value).rstrip('0').rstrip('.'))
            for var in self.uncnowns:
                value = solution.get(var, None)
                if value is not None:
                    task = task.replace(f'{{{var}}}', str(value).rstrip('0').rstrip('.'))
            tasks.append(task)

        tasks_text = "\n".join(tasks)
        self.output_text.delete("1.0", tk.END)  # Очищаем текстовое поле перед выводом
        self.output_text.insert(tk.END, tasks_text)  # Вставляем сгенерированные задания

    def save_tasks(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'w') as f:
                f.write(self.output_text.get("1.0", tk.END))


if __name__ == "__main__":
    root = tk.Tk()
    app = EquationInputWindow(root)
    root.mainloop()
