import tkinter as tk
from tkinter import messagebox, filedialog
from tabulate import tabulate
from equation_solver import EquationSolver
from sympy import Eq, sympify, Float
from sympy import re, im


class EquationInputWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Ввод уравнений")
        self.eq_text = tk.Text(self.master, height=10, width=50, wrap="none")

        h_scroll = tk.Scrollbar(self.master, orient="horizontal", command=self.eq_text.xview)
        self.eq_text.config(xscrollcommand=h_scroll.set)
        h_scroll.pack(fill=tk.X)

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
        VariableInputWindow(equations, variables, eq_input)


class TaskWindow:
    def __init__(self, all_unknown_vars, solutions, _uncnowns, _variables):
        self.all_unknown_vars = all_unknown_vars
        self.variables = _variables
        self.solutions = solutions
        self.uncnowns = _uncnowns
        self.master = tk.Tk()
        self.master.title("Генерация заданий")

        var_label = tk.Label(self.master,
                             text="Сгенерированные переменные переменные: " + ", ".join(str(var) for var in self.all_unknown_vars)
                                  + '\nОтветы: ' + ", ".join(str(var) for var in self.uncnowns))
        var_label.pack()

        tk.Label(self.master, text="Введите текст задачи с переменными в формате {переменная}:").pack()
        self.task_input = tk.Text(self.master, height=5, width=50, wrap="none")

        task_h_scroll = tk.Scrollbar(self.master, orient="horizontal", command=self.task_input.xview)
        self.task_input.config(xscrollcommand=task_h_scroll.set)
        task_h_scroll.pack(fill=tk.X)

        self.task_input.pack(pady=10)

        generate_button = tk.Button(self.master, text="Генерация заданий", command=self.generate_tasks)
        generate_button.pack()

        self.output_frame = tk.Frame(self.master)
        self.output_frame.pack(pady=10)

        self.output_text = tk.Text(self.output_frame, height=10, width=50, wrap="none")

        scroll_bar_x = tk.Scrollbar(self.master, orient="horizontal", command=self.output_text.xview)
        self.output_text.config(xscrollcommand=scroll_bar_x.set)
        scroll_bar_x.pack(fill=tk.X)

        self.output_text.pack(side=tk.LEFT)

        save_button = tk.Button(self.master, text="Сохранить задания", command=self.save_tasks)
        save_button.pack(pady=5)

        scroll_bar = tk.Scrollbar(self.output_frame)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.output_text.yview)

    def generate_tasks(self):
        # Получаем шаблон задачи
        task_template = self.task_input.get("1.0", tk.END).strip()
        if not task_template:
            messagebox.showerror("Ошибка", "Введите текст задачи.")
            return

        tasks = []

        # Итерируем по всем решениям
        for solution in self.solutions:
            task = task_template
            for var in self.all_unknown_vars + self.uncnowns:
                if isinstance(solution, dict):
                    value = solution.get(var, None)
                else:
                    ind = self.variables.index(var)
                    value = solution[0][ind]

                if value is not None:
                    if isinstance(value, tuple):
                        value = max(value)
                    if value.is_imaginary:
                        value_str = f"({re(value):.4f} + {im(value):.4f}j)"
                    else:
                        value_str = f"{float(value):.6f}".rstrip('0').rstrip('.')
                    task = task.replace(f'{{{var}}}', value_str)

            tasks.append(task)

        # Формируем текст задач и выводим
        tasks_text = "\n\n".join(tasks)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, tasks_text)

    def save_tasks(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'w') as f:
                f.write(self.output_text.get("1.0", tk.END))


class VariableInputWindow:
    def __init__(self, equations, variables, _eqinput):
        self.equations = equations
        self.eqinput = _eqinput
        self.variables = variables
        self.known_vars_entries = {}
        self.unknown_vars_checkbuttons = {}
        self.ranges_entries = {}
        self.rounding_entries = {}

        self.master = tk.Tk()
        self.master.title("Введите переменные")

        tk.Label(self.master, text="Введите значения известных переменных и отметьте неизвестные:").pack()
        tk.Label(self.master, text='\n'.join(list(map(str, self.eqinput)))).pack()

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

            tk.Label(frame, text="Округление: ").pack(side=tk.LEFT)
            rounding_entry = tk.Entry(frame, width=10)
            rounding_entry.pack(side=tk.LEFT)
            self.rounding_entries[var] = rounding_entry

        submit_button = tk.Button(self.master, text="Далее", command=self.submit_variables)
        submit_button.pack()

    def submit_variables(self):
        known_values = {}
        unknown_vars = []
        ranges = {}
        rounding = {}

        for var in self.variables:
            value = self.known_vars_entries[var].get().strip()
            if value:
                try:
                    known_values[var] = float(value)
                except ValueError:
                    messagebox.showerror("Ошибка", f"Некорректное значение для переменной {var}.")
                    return

            range_value = self.ranges_entries[var].get().strip()
            if range_value:
                try:
                    low, high = map(float, range_value.split(','))
                    ranges[var] = (low, high)
                except ValueError:
                    messagebox.showerror("Ошибка",
                                         f"Некорректный диапазон для переменной {var}. Используйте формат 'min,max'.")
                    return

            rounding_value = self.rounding_entries[var].get().strip()
            if rounding_value:
                try:
                    count = int(rounding_value)
                    if count < 0:
                        raise ValueError("Отрицательное значение")
                    rounding[var] = count
                except ValueError:
                    messagebox.showerror("Ошибка",
                                         f"Некорректный ввод, введите целое число")
                    return

        for var in self.variables:
            if self.unknown_vars_checkbuttons[var].get() == 1:
                unknown_vars.append(var)

        self.master.destroy()
        SolutionWindow(self.equations, self.variables, known_values, unknown_vars, ranges, rounding)


class SolutionWindow:
    def __init__(self, equations, variables, known_values, unknown_vars, ranges, rounding):
        self.equations = equations
        self.variables = variables
        self.known_values = known_values
        self.unknown_vars = unknown_vars
        self.ranges = ranges
        self.rounding = rounding
        self.solutions = None
        self.master = tk.Tk()
        self.master.title("Решения уравнений")

        tk.Label(self.master, text="Введите количество заданий:").pack()
        self.count_entry = tk.Entry(self.master)
        self.count_entry.pack()

        self.table_frame = tk.Frame(self.master)
        self.table_frame.pack()

        # Создаем текстовое окно с прокруткой для вывода решений
        self.solution_frame = tk.Frame(self.master)
        self.solution_frame.pack()

        self.scrollbar_y = tk.Scrollbar(self.solution_frame)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.scrollbar_x = tk.Scrollbar(self.solution_frame, orient=tk.HORIZONTAL)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.solution_text = tk.Text(self.solution_frame, wrap="none", height=20, width=80,
                                     xscrollcommand=self.scrollbar_x.set, yscrollcommand=self.scrollbar_y.set)
        self.solution_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar_x.config(command=self.solution_text.xview)
        self.scrollbar_y.config(command=self.solution_text.yview)

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

        # Генерация решений
        self.solutions = EquationSolver.generation_solutions(
            self.equations, self.variables, count, self.all_unknown_vars, self.ranges, self.rounding
        )

        header = [str(var) for var in self.variables]
        table = []
        for solution in self.solutions:
            row_values = []
            for var in self.variables:
                if var in self.known_values:
                    row_values.append(self.known_values[var])
                elif isinstance(solution, dict) and var in solution:
                    value = solution[var]
                    if value.is_imaginary:
                        value_str = f"({re(value):.4f} + {im(value):.4f}j)"
                        row_values.append(value_str)
                    elif isinstance(value, (list, tuple)):
                        value_str = f"({', '.join([f'{float(v):.4f}' for v in value])})"
                        row_values.append(value_str)
                    elif isinstance(value, Float):
                        row_values.append(f"{float(value):.4f}")
                    else:
                        row_values.append('-')
                elif isinstance(solution, list):
                    ind = self.variables.index(var)
                    value_str = f"({', '.join([f'{float(sol[ind]):.4f}' for sol in solution])})"
                    row_values.append(value_str)
                else:
                    row_values.append('-')

            table.append(row_values)

        # Форматирование результатов в виде таблицы
        result_text = tabulate(table, headers=header, tablefmt="grid", numalign="center", floatfmt=".4f")

        # Очистка и вывод текста решений в текстовое окно
        self.solution_text.delete(1.0, tk.END)  # Очищаем текстовое поле
        self.solution_text.insert(tk.END, result_text)  # Выводим новое решение

    def open_task_window(self):
        TaskWindow(self.all_unknown_vars, self.solutions, self.unknown_vars, self.variables)

    def save_solutions(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'w') as f:
                f.write(self.solution_text.get("1.0", tk.END))

    def next_task(self):
        self.master.destroy()
        EquationInputWindow(tk.Tk())
