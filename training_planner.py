import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")
        
        # Данные
        self.trainings = []
        self.filtered_trainings = []
        self.data_file = "trainings.json"
        
        # Загрузка данных
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_widgets(self):
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавить тренировку", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Поле Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(input_frame, textvariable=self.type_var, width=20)
        self.type_combo['values'] = ('Бег', 'Плавание', 'Велосипед', 'Силовая', 'Йога', 'Другое')
        self.type_combo.grid(row=0, column=3, padx=5, pady=5)
        self.type_combo.set('Бег')
        
        # Поле Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.duration_entry = ttk.Entry(input_frame, width=15)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_btn = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Рамка для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по типу
        ttk.Label(filter_frame, text="Фильтр по типу:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_type_var = tk.StringVar()
        self.filter_type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var, width=20)
        self.filter_type_combo['values'] = ('Все', 'Бег', 'Плавание', 'Велосипед', 'Силовая', 'Йога', 'Другое')
        self.filter_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type_combo.set('Все')
        self.filter_type_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.filter_date_entry = ttk.Entry(filter_frame, width=20)
        self.filter_date_entry.grid(row=0, column=3, padx=5, pady=5)
        self.filter_date_entry.insert(0, "Все")
        
        # Кнопки фильтрации и сброса
        self.filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filters)
        self.filter_btn.grid(row=0, column=4, padx=5, pady=5)
        self.reset_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters)
        self.reset_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Рамка для таблицы
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Таблица с прокруткой
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(table_frame, columns=("date", "type", "duration"), show="headings", yscrollcommand=scrollbar.set)
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        self.tree.column("date", width=150)
        self.tree.column("type", width=200)
        self.tree.column("duration", width=150)
        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Кнопка удаления
        self.delete_btn = ttk.Button(self.root, text="Удалить выбранную тренировку", command=self.delete_training)
        self.delete_btn.pack(pady=5)
    
    def validate_date(self, date_str):
        """Проверка корректности формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_duration(self, duration_str):
        """Проверка корректности длительности"""
        try:
            duration = float(duration_str)
            return duration > 0
        except ValueError:
            return False
    
    def add_training(self):
        """Добавление тренировки"""
        date = self.date_entry.get().strip()
        training_type = self.type_var.get()
        duration = self.duration_entry.get().strip()
        
        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        
        if not training_type:
            messagebox.showerror("Ошибка", "Выберите тип тренировки")
            return
        
        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
            return
        
        # Добавление записи
        training = {
            "date": date,
            "type": training_type,
            "duration": float(duration)
        }
        self.trainings.append(training)
        self.save_data()
        self.refresh_table()
        
        # Очистка полей
        self.duration_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Тренировка добавлена")
    
    def delete_training(self):
        """Удаление выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления")
            return
        
        # Получаем индекс выбранной записи
        item = selected[0]
        values = self.tree.item(item, "values")
        
        # Находим и удаляем запись
        for i, training in enumerate(self.filtered_trainings):
            if (training["date"] == values[0] and 
                training["type"] == values[1] and 
                training["duration"] == float(values[2])):
                # Удаляем из основного списка
                self.trainings.remove(training)
                break
        
        self.save_data()
        self.refresh_table()
        messagebox.showinfo("Успех", "Тренировка удалена")
    
    def apply_filters(self):
        """Применение фильтров"""
        filter_type = self.filter_type_var.get()
        filter_date = self.filter_date_entry.get().strip()
        
        self.filtered_trainings = self.trainings.copy()
        
        # Фильтр по типу
        if filter_type != "Все":
            self.filtered_trainings = [t for t in self.filtered_trainings if t["type"] == filter_type]
        
        # Фильтр по дате
        if filter_date != "Все" and filter_date:
            if self.validate_date(filter_date):
                self.filtered_trainings = [t for t in self.filtered_trainings if t["date"] == filter_date]
            elif filter_date != "Все":
                messagebox.showwarning("Предупреждение", "Неверный формат даты фильтра")
        
        self.update_table()
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_type_var.set("Все")
        self.filter_date_entry.delete(0, tk.END)
        self.filter_date_entry.insert(0, "Все")
        self.refresh_table()
    
    def update_table(self):
        """Обновление таблицы с учетом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполнение таблицы
        for training in self.filtered_trainings:
            self.tree.insert("", "end", values=(
                training["date"],
                training["type"],
                f"{training['duration']:.1f}"
            ))
    
    def refresh_table(self):
        """Обновление данных и таблицы"""
        self.filtered_trainings = self.trainings.copy()
        self.update_table()
    
    def save_data(self):
        """Сохранение данных в JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.trainings = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.trainings = []
        else:
            self.trainings = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
