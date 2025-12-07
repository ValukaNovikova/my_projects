import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import itertools
from threading import Thread
import time

class CombinationFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Поиск комбинаций чисел")
        self.root.geometry("1200x800")
        
        # Переменные
        self.is_searching = False
        self.current_thread = None
        
        self.create_widgets()
        self.bind_events()
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка расширения
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Поле для ввода чисел
        ttk.Label(main_frame, text="Введите числа (каждое число с новой строки или через точку с запятой):").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        self.numbers_text = scrolledtext.ScrolledText(main_frame, height=10, width=85)
        self.numbers_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Кнопка для очистки
        ttk.Button(main_frame, text="Очистить поле", command=self.clear_numbers).grid(row=2, column=1, sticky=tk.E, pady=(0, 10))
        
        # Фрейм для параметров
        params_frame = ttk.Frame(main_frame)
        params_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Поле для целевой суммы
        ttk.Label(params_frame, text="Целевая сумма:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5), padx=(0, 10))
        
        self.target_sum_var = tk.StringVar(value="34,81")
        self.target_entry = ttk.Entry(params_frame, textvariable=self.target_sum_var, width=15)
        self.target_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5), padx=(0, 20))
        
        # Поле для точности
        ttk.Label(params_frame, text="Точность (дельта):").grid(row=0, column=2, sticky=tk.W, pady=(0, 5), padx=(0, 10))
        
        self.tolerance_var = tk.StringVar(value="0,01")
        self.tolerance_entry = ttk.Entry(params_frame, textvariable=self.tolerance_var, width=15)
        self.tolerance_entry.grid(row=0, column=3, sticky=tk.W, pady=(0, 5), padx=(0, 20))
        
        # Ограничение на размер комбинации
        ttk.Label(params_frame, text="Макс. чисел в комбинации:").grid(row=0, column=4, sticky=tk.W, pady=(0, 5), padx=(0, 10))
        
        self.max_comb_var = tk.StringVar(value="0")
        self.max_comb_entry = ttk.Entry(params_frame, textvariable=self.max_comb_var, width=15)
        self.max_comb_entry.grid(row=0, column=5, sticky=tk.W, pady=(0, 5))
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Начать поиск", command=self.start_search)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Остановить", command=self.stop_search, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Поле для результатов
        ttk.Label(main_frame, text="Результаты:").grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        self.results_text = scrolledtext.ScrolledText(main_frame, height=15, width=85)
        self.results_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе. Скопируйте данные из таблицы и вставьте в верхнее поле (Ctrl+V).")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=800)
        status_label.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def bind_events(self):
        """Привязка событий для горячих клавиш"""
        # Привязываем Ctrl+V к текстовым полям
        self.numbers_text.bind('<Control-v>', self.paste_from_clipboard)
        self.numbers_text.bind('<Control-V>', self.paste_from_clipboard)
        
        self.results_text.bind('<Control-v>', self.paste_from_clipboard)
        self.results_text.bind('<Control-V>', self.paste_from_clipboard)
        
        # Также привязываем к основному окну для случаев, когда фокус не в текстовом поле
        self.root.bind('<Control-v>', self.focus_and_paste)
        self.root.bind('<Control-V>', self.focus_and_paste)
        
        # Горячая клавиша для запуска поиска - Enter в поле целевой суммы
        self.target_entry.bind('<Return>', lambda e: self.start_search())
        self.tolerance_entry.bind('<Return>', lambda e: self.start_search())
        self.max_comb_entry.bind('<Return>', lambda e: self.start_search())
        
        # Добавляем контекстное меню для вставки
        self.create_context_menus()
    
    def create_context_menus(self):
        """Создает контекстные меню для текстовых полей"""
        # Меню для поля ввода чисел
        self.numbers_menu = tk.Menu(self.numbers_text, tearoff=0)
        self.numbers_menu.add_command(label="Вставить", command=lambda: self.paste_from_clipboard())
        self.numbers_menu.add_command(label="Копировать", command=lambda: self.numbers_text.event_generate("<<Copy>>"))
        self.numbers_menu.add_command(label="Вырезать", command=lambda: self.numbers_text.event_generate("<<Cut>>"))
        self.numbers_menu.add_separator()
        self.numbers_menu.add_command(label="Выделить все", command=lambda: self.numbers_text.tag_add('sel', '1.0', 'end'))
        
        self.numbers_text.bind("<Button-3>", self.show_numbers_menu)  # Правая кнопка мыши
        
        # Меню для поля результатов
        self.results_menu = tk.Menu(self.results_text, tearoff=0)
        self.results_menu.add_command(label="Копировать", command=lambda: self.results_text.event_generate("<<Copy>>"))
        self.results_menu.add_command(label="Вырезать", command=lambda: self.results_text.event_generate("<<Cut>>"))
        self.results_menu.add_separator()
        self.results_menu.add_command(label="Выделить все", command=lambda: self.results_text.tag_add('sel', '1.0', 'end'))
        self.results_menu.add_command(label="Очистить", command=lambda: self.results_text.delete('1.0', 'end'))
        
        self.results_text.bind("<Button-3>", self.show_results_menu)  # Правая кнопка мыши
    
    def show_numbers_menu(self, event):
        """Показывает контекстное меню для поля ввода чисел"""
        try:
            self.numbers_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.numbers_menu.grab_release()
    
    def show_results_menu(self, event):
        """Показывает контекстное меню для поля результатов"""
        try:
            self.results_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.results_menu.grab_release()
    
    def focus_and_paste(self, event=None):
        """Переводит фокус на поле ввода и вставляет текст"""
        self.numbers_text.focus_set()
        self.paste_from_clipboard(event)
        return "break"
    
    def paste_from_clipboard(self, event=None):
        """Вставляет текст из буфера обмена"""
        try:
            # Получаем текст из буфера обмена
            clipboard_text = self.root.clipboard_get()
            
            # Определяем, в каком виджете вставлять
            if event and event.widget == self.results_text:
                target_widget = self.results_text
            else:
                target_widget = self.numbers_text
            
            # Вставляем текст в текущую позицию курсора
            target_widget.insert(tk.INSERT, clipboard_text)
            
            # Показываем сообщение о успешной вставке
            lines = clipboard_text.strip().split('\n')
            numbers_count = len([line for line in lines if line.strip()])
            self.status_var.set(f"Успешно вставлено {numbers_count} чисел из буфера обмена")
            
            return "break"  # Предотвращаем стандартную обработку
            
        except tk.TclError:
            messagebox.showwarning("Буфер обмена", "Не удалось получить данные из буфера обмена")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при вставке: {str(e)}")
        
        return "break"
    
    def clear_numbers(self):
        """Очищает поле ввода чисел"""
        self.numbers_text.delete('1.0', tk.END)
        self.status_var.set("Поле очищено. Можете вставить новые данные (Ctrl+V).")
    
    def parse_numbers(self, text):
        """Парсит строку с числами, разделенными переводом строки или точкой с запятой"""
        numbers = []
        
        # Сначала пробуем разделить по переводам строк
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Если строка содержит несколько чисел через точку с запятой
            if ';' in line:
                items = line.split(';')
                for item in items:
                    item = item.strip()
                    if item:
                        num = self.parse_single_number(item)
                        if num is not None:
                            numbers.append(num)
            else:
                # Одно число в строке
                num = self.parse_single_number(line)
                if num is not None:
                    numbers.append(num)
        
        return numbers
    
    def parse_single_number(self, text):
        """Парсит одно число, поддерживая разные форматы"""
        text = text.strip()
        if not text:
            return None
            
        # Заменяем запятую на точку
        text = text.replace(',', '.')
        
        # Удаляем все нечисловые символы, кроме точки и минуса
        cleaned = ''
        for char in text:
            if char.isdigit() or char in '.-':
                cleaned += char
        
        try:
            return float(cleaned)
        except ValueError:
            # Пробуем убрать возможные лишние точки
            parts = cleaned.split('.')
            if len(parts) > 2:
                # Если много точек, оставляем только первую как десятичный разделитель
                cleaned = parts[0] + '.' + ''.join(parts[1:])
                try:
                    return float(cleaned)
                except ValueError:
                    return None
            return None
    
    def find_combinations(self, numbers, target_sum, tolerance=0.01, max_comb_size=0):
        """Находит комбинации чисел, дающие сумму в пределах заданной точности"""
        results = []
        
        # Сортируем числа по убыванию для более эффективного поиска
        numbers_sorted = sorted(numbers, reverse=True)
        
        # Определяем максимальный размер комбинации
        max_r = len(numbers_sorted) if max_comb_size == 0 else min(max_comb_size, len(numbers_sorted))
        
        total_combinations = sum(self.combinations_count(len(numbers_sorted), r) for r in range(1, max_r + 1))
        checked_combinations = 0
        
        # Перебираем все возможные размеры комбинаций
        for r in range(1, max_r + 1):
            if not self.is_searching:
                break
                
            comb_count = self.combinations_count(len(numbers_sorted), r)
            self.status_var.set(f"Проверка комбинаций из {r} чисел... ({comb_count} комбинаций)")
            
            for combo in itertools.combinations(numbers_sorted, r):
                if not self.is_searching:
                    break
                    
                checked_combinations += 1
                if checked_combinations % 1000 == 0:  # Обновляем статус каждые 1000 комбинаций
                    progress = (checked_combinations / total_combinations) * 100
                    self.status_var.set(f"Проверка: {checked_combinations}/{total_combinations} ({progress:.1f}%)")
                
                current_sum = sum(combo)
                if abs(current_sum - target_sum) <= tolerance:
                    results.append(combo)
                    # Обновляем интерфейс с найденным результатом
                    self.root.after(0, self.add_result, combo, current_sum)
        
        return results
    
    def combinations_count(self, n, k):
        """Вычисляет количество комбинаций C(n, k)"""
        import math
        return math.comb(n, k)
    
    def add_result(self, combo, sum_value):
        """Добавляет найденный результат в текстовое поле"""
        combo_str = " + ".join(f"{x:.3f}" for x in sorted(combo, reverse=True))
        result_text = f"Сумма: {sum_value:.3f}\nКомбинация: {combo_str}\n{'-'*50}\n"
        self.results_text.insert(tk.END, result_text)
        self.results_text.see(tk.END)
    
    def start_search(self):
        """Запускает поиск в отдельном потоке"""
        if self.is_searching:
            return
        
        # Получаем данные из полей ввода
        numbers_text = self.numbers_text.get("1.0", tk.END).strip()
        target_sum_text = self.target_sum_var.get().strip()
        tolerance_text = self.tolerance_var.get().strip()
        max_comb_text = self.max_comb_var.get().strip()
        
        # Парсим числа
        numbers = self.parse_numbers(numbers_text)
        if not numbers:
            messagebox.showerror("Ошибка", "Не удалось распознать числа. Проверьте формат ввода.")
            return
        
        # Парсим целевую сумму, точность и ограничение
        try:
            target_sum = float(target_sum_text.replace(',', '.'))
            tolerance = float(tolerance_text.replace(',', '.'))
            max_comb_size = int(max_comb_text) if max_comb_text else 0
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат чисел. Проверьте целевую сумму, точность и ограничение.")
            return
        
        # Очищаем результаты
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"Поиск комбинаций для суммы: {target_sum:.3f}\n")
        self.results_text.insert(tk.END, f"Точность: ±{tolerance:.3f}\n")
        self.results_text.insert(tk.END, f"Количество чисел: {len(numbers)}\n")
        if max_comb_size > 0:
            self.results_text.insert(tk.END, f"Макс. чисел в комбинации: {max_comb_size}\n")
        self.results_text.insert(tk.END, f"{'='*50}\n")
        
        # Запускаем поиск
        self.is_searching = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        
        # Запускаем поиск в отдельном потоке
        self.current_thread = Thread(target=self.search_thread, args=(numbers, target_sum, tolerance, max_comb_size))
        self.current_thread.daemon = True
        self.current_thread.start()
    
    def search_thread(self, numbers, target_sum, tolerance, max_comb_size):
        """Поток для выполнения поиска"""
        try:
            start_time = time.time()
            results = self.find_combinations(numbers, target_sum, tolerance, max_comb_size)
            elapsed_time = time.time() - start_time
            
            # Обновляем статус
            if self.is_searching:
                self.root.after(0, self.search_completed, len(results), elapsed_time)
        
        except Exception as e:
            self.root.after(0, self.search_error, str(e))
    
    def search_completed(self, results_count, elapsed_time):
        """Вызывается при завершении поиска"""
        self.is_searching = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        
        self.status_var.set(f"Поиск завершен. Найдено комбинаций: {results_count}. Время: {elapsed_time:.2f} сек.")
        
        if results_count == 0:
            self.results_text.insert(tk.END, "Комбинации не найдены.\n")
    
    def search_error(self, error_message):
        """Вызывается при ошибке поиска"""
        self.is_searching = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        
        messagebox.showerror("Ошибка", f"Произошла ошибка:\n{error_message}")
        self.status_var.set("Ошибка при выполнении поиска")
    
    def stop_search(self):
        """Останавливает поиск"""
        self.is_searching = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.status_var.set("Поиск остановлен пользователем")

def main():
    root = tk.Tk()
    app = CombinationFinder(root)
    root.mainloop()

if __name__ == "__main__":
    main()