import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from config import (
    DATETIME_FORMAT,
    DEFAULT_FONT,
    TITLE_FONT,
    SMALL_FONT,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_INFO,
    COLOR_WARNING,
    COLOR_SECONDARY,
    STATUS_ICONS,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)
from database import ReminderDatabase
from notifications import NotificationManager
from logger import logger


class ReminderGUI:
    """Класс для графического интерфейса приложения"""

    def __init__(self, root: tk.Tk, db: ReminderDatabase, notifier: NotificationManager):
        """Инициализация GUI"""
        self.root = root
        self.db = db
        self.notifier = notifier
        self.current_filter = "Все"
        self.setup_ui()

    def setup_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.root.title("📋 Reminder App Wind11")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(True, True)
        self.root.configure(bg="#f7f9fc")

        top_frame = tk.Frame(self.root, bg="#edf2fb", height=64)
        top_frame.pack(fill=tk.X, padx=0, pady=0)

        add_btn = tk.Button(
            top_frame,
            text="➕ Добавить",
            command=self.add_reminder,
            font=DEFAULT_FONT,
            bg=COLOR_SUCCESS,
            fg="white",
            padx=16,
            pady=10,
        )
        add_btn.pack(side=tk.LEFT, padx=6, pady=8)

        del_btn = tk.Button(
            top_frame,
            text="🗑️ Удалить",
            command=self.delete_reminder,
            font=DEFAULT_FONT,
            bg=COLOR_ERROR,
            fg="white",
            padx=16,
            pady=10,
        )
        del_btn.pack(side=tk.LEFT, padx=6, pady=8)

        done_btn = tk.Button(
            top_frame,
            text="✅ Готово",
            command=self.mark_as_done,
            font=DEFAULT_FONT,
            bg=COLOR_INFO,
            fg="white",
            padx=16,
            pady=10,
        )
        done_btn.pack(side=tk.LEFT, padx=6, pady=8)

        cancel_btn = tk.Button(
            top_frame,
            text="❌ Отменить",
            command=self.cancel_reminder,
            font=DEFAULT_FONT,
            bg=COLOR_WARNING,
            fg="white",
            padx=16,
            pady=10,
        )
        cancel_btn.pack(side=tk.LEFT, padx=6, pady=8)

        refresh_btn = tk.Button(
            top_frame,
            text="🔄 Обновить",
            command=self.refresh_reminders,
            font=DEFAULT_FONT,
            bg=COLOR_SECONDARY,
            fg="white",
            padx=16,
            pady=10,
        )
        refresh_btn.pack(side=tk.LEFT, padx=6, pady=8)

        test_btn = tk.Button(
            top_frame,
            text="🧪 Тест",
            command=self.notifier.test_notification,
            font=DEFAULT_FONT,
            bg="#455a64",
            fg="white",
            padx=16,
            pady=10,
        )
        test_btn.pack(side=tk.LEFT, padx=6, pady=8)

        quick_frame = tk.Frame(self.root, bg="#ffffff", height=44)
        quick_frame.pack(fill=tk.X, padx=10, pady=8)

        quick_label = tk.Label(quick_frame, text="Быстрое напоминание через:", font=SMALL_FONT, bg="#ffffff")
        quick_label.pack(side=tk.LEFT, padx=4)

        for label_text, minutes in [("1 мин", 1), ("5 мин", 5), ("15 мин", 15), ("1 час", 60)]:
            btn = tk.Button(
                quick_frame,
                text=label_text,
                command=lambda m=minutes: self.set_quick_time(m),
                font=SMALL_FONT,
                bg="#e8f3ff",
                padx=12,
                pady=7,
            )
            btn.pack(side=tk.LEFT, padx=4)

        filter_frame = tk.Frame(self.root, bg="#ffffff", height=44)
        filter_frame.pack(fill=tk.X, padx=10, pady=4)

        filter_label = tk.Label(filter_frame, text="Фильтр:", font=SMALL_FONT, bg="#ffffff")
        filter_label.pack(side=tk.LEFT, padx=4)

        for filter_name in ["Все", "Ожидает", "Готово", "Просрочено", "Отменено"]:
            btn = tk.Button(
                filter_frame,
                text=filter_name,
                command=lambda f=filter_name: self.apply_filter(f),
                font=SMALL_FONT,
                bg="#f5f5f5",
                padx=12,
                pady=7,
            )
            btn.pack(side=tk.LEFT, padx=4)

        list_frame = tk.Frame(self.root, bg="#ffffff")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.reminder_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=DEFAULT_FONT,
            bg="#ffffff",
            fg="#1f2937",
            selectbackground="#bbdefb",
            selectforeground="#0d47a1",
            activestyle='none',
            height=20,
        )
        self.reminder_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.reminder_listbox.bind('<Double-Button-1>', self.on_double_click)
        scrollbar.config(command=self.reminder_listbox.yview)

        status_frame = tk.Frame(self.root, bg="#f1f5f9", height=36)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = tk.Label(
            status_frame,
            text="Загрузка напоминаний...",
            font=SMALL_FONT,
            bg="#f1f5f9",
            fg="#1f2937",
            anchor=tk.W,
        )
        self.status_label.pack(fill=tk.X, padx=12, pady=8)

        self.refresh_reminders()

    def _get_current_reminders(self) -> List[Dict]:
        """Получение списка напоминаний в соответствии с текущим фильтром"""
        if self.current_filter == "Все":
            return self.db.get_all_reminders()
        return self.db.get_reminders_by_status(self.current_filter)

    def _show_error(self, title: str, message: str):
        logger.error("%s: %s", title, message)
        messagebox.showerror(title, message)

    def update_status_bar(self):
        """Обновить статус-бар с количеством напоминаний"""
        total = self.db.get_reminders_count()
        waiting = len(self.db.get_reminders_by_status("Ожидает"))
        done = len(self.db.get_reminders_by_status("Готово"))
        overdue = len(self.db.get_reminders_by_status("Просрочено"))
        cancelled = len(self.db.get_reminders_by_status("Отменено"))

        status_text = f"Всего: {total} | Ожидает: {waiting} | Готово: {done} | Просрочено: {overdue} | Отменено: {cancelled}"
        self.status_label.config(text=status_text)

    def set_quick_time(self, minutes: int):
        """Быстрое напоминание на определённое время"""
        title = simpledialog.askstring("Быстрое напоминание", "Заголовок:")
        if title is None or not title.strip():
            return

        description = simpledialog.askstring("Быстрое напоминание", "Описание:")
        if description is None:
            description = ""

        due_time = datetime.now() + timedelta(minutes=minutes)
        due_time_str = due_time.strftime(DATETIME_FORMAT)

        reminder_id = self.db.add_reminder(title, description, due_time_str)
        if reminder_id == -1:
            self._show_error("Ошибка", "Не удалось добавить напоминание. Проверьте данные и попробуйте снова.")
            return

        messagebox.showinfo("Успех", f"Напоминание установлено на {due_time_str}")
        self.refresh_reminders()

    def add_reminder(self):
        """Добавить новое напоминание"""
        add_window = tk.Toplevel(self.root)
        add_window.title("➕ Добавить напоминание")
        add_window.geometry("430x380")
        add_window.transient(self.root)
        add_window.grab_set()

        ttk.Label(add_window, text="Заголовок:", font=SMALL_FONT).pack(pady=6, padx=12, anchor=tk.W)
        title_entry = ttk.Entry(add_window, width=42)
        title_entry.pack(pady=4, padx=12, fill=tk.X)

        ttk.Label(add_window, text="Описание:", font=SMALL_FONT).pack(pady=6, padx=12, anchor=tk.W)
        desc_text = tk.Text(add_window, height=6, width=42, wrap=tk.WORD)
        desc_text.pack(pady=4, padx=12, fill=tk.BOTH, expand=True)

        ttk.Label(add_window, text="Дата и время (YYYY-MM-DD HH:MM:SS):", font=SMALL_FONT).pack(pady=6, padx=12, anchor=tk.W)
        time_entry = ttk.Entry(add_window, width=42)
        default_time = (datetime.now() + timedelta(hours=1)).strftime(DATETIME_FORMAT)
        time_entry.insert(0, default_time)
        time_entry.pack(pady=4, padx=12, fill=tk.X)

        def save_reminder():
            title = title_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            due_time = time_entry.get().strip()

            if not title:
                messagebox.showerror("Ошибка", "Заголовок не может быть пустым.")
                return
            if not due_time:
                messagebox.showerror("Ошибка", "Дата и время не могут быть пустыми.")
                return

            try:
                datetime.strptime(due_time, DATETIME_FORMAT)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат времени. Используйте YYYY-MM-DD HH:MM:SS.")
                return

            reminder_id = self.db.add_reminder(title, description, due_time)
            if reminder_id == -1:
                self._show_error("Ошибка", "Не удалось сохранить напоминание. Проверьте данные и попробуйте снова.")
                return

            messagebox.showinfo("Успех", "Напоминание успешно добавлено.")
            add_window.destroy()
            self.refresh_reminders()

        save_btn = tk.Button(
            add_window,
            text="💾 Сохранить",
            command=save_reminder,
            font=DEFAULT_FONT,
            bg=COLOR_SUCCESS,
            fg="white",
            padx=20,
            pady=10,
        )
        save_btn.pack(pady=12)

    def refresh_reminders(self):
        """Обновить список напоминаний"""
        try:
            self.reminder_listbox.delete(0, tk.END)
            reminders = self._get_current_reminders()
            reminders = self.db.sort_by_due_time(reminders)
            for reminder in reminders:
                icon = STATUS_ICONS.get(reminder['status'], "❓")
                display_text = f"{icon} [{reminder['id']}] {reminder['title']} — {reminder['due_time']}"
                self.reminder_listbox.insert(tk.END, display_text)
            self.update_status_bar()
        except Exception as exc:
            self._show_error("Ошибка", "Не удалось обновить список напоминаний.")
            logger.exception("Ошибка при обновлении списка напоминаний: %s", exc)

    def _get_selected_reminder(self) -> Optional[Dict]:
        selection = self.reminder_listbox.curselection()
        if not selection:
            return None

        reminders = self._get_current_reminders()
        reminders = self.db.sort_by_due_time(reminders)
        index = selection[0]
        if index >= len(reminders):
            return None
        return reminders[index]

    def mark_as_done(self):
        """Отметить напоминание как выполненное"""
        reminder = self._get_selected_reminder()
        if not reminder:
            messagebox.showwarning("Ошибка", "Выберите напоминание для отметки.")
            return
        if not self.db.update_status(reminder['id'], "Готово"):
            self._show_error("Ошибка", "Не удалось отметить напоминание как готовое.")
            return
        self.refresh_reminders()

    def cancel_reminder(self):
        """Отменить напоминание"""
        reminder = self._get_selected_reminder()
        if not reminder:
            messagebox.showwarning("Ошибка", "Выберите напоминание для отмены.")
            return
        if not self.db.update_status(reminder['id'], "Отменено"):
            self._show_error("Ошибка", "Не удалось отменить напоминание.")
            return
        self.refresh_reminders()

    def delete_reminder(self):
        """Удалить напоминание"""
        reminder = self._get_selected_reminder()
        if not reminder:
            messagebox.showwarning("Ошибка", "Выберите напоминание для удаления.")
            return

        if messagebox.askyesno("Подтверждение", f"Удалить '{reminder['title']}'?"):
            if not self.db.delete_reminder(reminder['id']):
                self._show_error("Ошибка", "Не удалось удалить напоминание.")
                return
            self.refresh_reminders()

    def on_double_click(self, event):
        """Обработка двойного клика для просмотра деталей"""
        reminder = self._get_selected_reminder()
        if not reminder:
            return

        details_window = tk.Toplevel(self.root)
        details_window.title("📖 Детали напоминания")
        details_window.geometry("480x320")
        details_window.transient(self.root)
        details_window.grab_set()

        tk.Label(details_window, text=f"ID: {reminder['id']}", font=TITLE_FONT).pack(pady=6, anchor=tk.W, padx=10)
        tk.Label(details_window, text=f"Заголовок: {reminder['title']}", font=DEFAULT_FONT).pack(pady=4, anchor=tk.W, padx=10)
        tk.Label(details_window, text=f"Описание:\n{reminder['description']}", font=SMALL_FONT, wraplength=440, justify=tk.LEFT).pack(pady=4, anchor=tk.W, padx=10)
        tk.Label(details_window, text=f"Время: {reminder['due_time']}", font=SMALL_FONT).pack(pady=4, anchor=tk.W, padx=10)
        tk.Label(details_window, text=f"Статус: {reminder['status']}", font=SMALL_FONT, fg="#1565c0").pack(pady=4, anchor=tk.W, padx=10)
        tk.Label(details_window, text=f"Создано: {reminder['created_at']}", font=SMALL_FONT).pack(pady=4, anchor=tk.W, padx=10)

    def apply_filter(self, filter_name: str):
        """Применить фильтр по статусу"""
        self.current_filter = filter_name
        self.refresh_reminders()

    def on_closing(self):
        """Обработка закрытия приложения"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            try:
                self.notifier.stop_monitoring()
            except Exception as exc:
                logger.exception("Ошибка при остановке мониторинга: %s", exc)
            self.root.destroy()

    def run(self):
        """Запустить приложение"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
