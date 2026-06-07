import threading
import time
import tkinter as tk
from datetime import datetime
from typing import Callable, Optional

from config import DATETIME_FORMAT, MONITOR_CHECK_INTERVAL, NOTIFICATION_DURATION, BEEP_DURATION, BEEP_FREQUENCY
from database import ReminderDatabase
from logger import logger


class NotificationManager:
    """Класс для управления уведомлениями напоминаний"""

    def __init__(self, db: ReminderDatabase, root: Optional[tk.Tk] = None, on_notification: Optional[Callable] = None):
        """Инициализация менеджера уведомлений"""
        self.db = db
        self.root = root
        self.on_notification = on_notification
        self.monitoring = False
        self.monitor_thread = None
        self.shown_reminders = set()
        self.win10toast_available = self._check_win10toast()
        logger.info("NotificationManager инициализирован. win10toast=%s", self.win10toast_available)

    def _ensure_root(self):
        """Создать скрытый корневой Tkinter, если он ещё не создан"""
        if self.root is None:
            try:
                self.root = tk.Tk()
                self.root.withdraw()
                logger.info("Создан скрытый корневой Tkinter для уведомлений")
            except Exception as exc:
                logger.exception("Не удалось создать корневое Tkinter: %s", exc)
                self.root = None

    def _check_win10toast(self) -> bool:
        """Проверка доступности win10toast"""
        try:
            from win10toast import ToastNotifier
            return True
        except ImportError:
            logger.warning("win10toast не установлен. Будут использоваться pop-up уведомления.")
            return False
        except Exception as exc:
            logger.exception("Ошибка при проверке win10toast: %s", exc)
            return False

    def start_monitoring(self):
        """Запустить мониторинг базы данных в фоновом режиме"""
        if self.monitoring:
            return

        self._ensure_root()
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Мониторинг напоминаний запущен")

    def stop_monitoring(self):
        """Остановить мониторинг"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
            logger.info("Мониторинг напоминаний остановлен")

    def _monitor_loop(self):
        """Основной цикл мониторинга"""
        while self.monitoring:
            try:
                overdue_count = self.db.mark_overdue()
                if overdue_count:
                    logger.info("Просрочено автоматически: %s", overdue_count)

                due_reminders = self.db.get_due_reminders()
                for reminder in due_reminders:
                    reminder_id = reminder['id']
                    if reminder_id not in self.shown_reminders:
                        self._show_notification(reminder)
                        self.shown_reminders.add(reminder_id)
                        if self.on_notification:
                            self.on_notification(reminder)
                time.sleep(MONITOR_CHECK_INTERVAL)
            except Exception as exc:
                logger.exception("Ошибка в цикле мониторинга: %s", exc)
                time.sleep(MONITOR_CHECK_INTERVAL)

    def _show_notification(self, reminder: dict):
        """Показать уведомление"""
        try:
            if self.win10toast_available:
                self._show_win10toast(reminder)
            else:
                self._show_popup(reminder)
        except Exception as exc:
            logger.exception("Ошибка при показе уведомления: %s", exc)
            self._show_popup(reminder)

    def _show_win10toast(self, reminder: dict):
        """Показать системное уведомление Windows 11"""
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(
                title=reminder['title'],
                msg=reminder['description'] or 'Новое напоминание',
                duration=30,
                threaded=True
            )
            logger.info("Показано win10toast уведомление для напоминания ID=%s", reminder['id'])
        except Exception as exc:
            logger.exception("Ошибка при показе win10toast: %s", exc)
            self._show_popup(reminder)

    def _show_popup(self, reminder: dict):
        """Показать pop-up окно Tkinter поверх всех окон"""
        self._ensure_root()

        if self.root is None:
            logger.error("Нет доступного Tkinter root. Уведомление будет выведено в консоль.")
            print(f"Напоминание: {reminder['title']} - {reminder['description']}")
            return

        try:
            self.root.after(0, self._create_popup, reminder)
        except Exception as exc:
            logger.exception("Не удалось запланировать pop-up уведомление: %s", exc)
            try:
                self._create_popup(reminder)
            except Exception as exc_inner:
                logger.exception("Не удалось показать pop-up уведомление напрямую: %s", exc_inner)

    def _create_popup(self, reminder: dict):
        """Создать окно уведомления внутри GUI-потока"""
        popup = tk.Toplevel(self.root)
        popup.attributes('-topmost', True)
        popup.geometry("420x260")
        popup.title("⏰ Напоминание")

        title_label = tk.Label(popup, text=reminder['title'], font=("Arial", 14, "bold"), fg="#0d47a1")
        title_label.pack(pady=12, padx=12, fill=tk.BOTH)

        desc_label = tk.Label(popup, text=reminder['description'] or "Описание отсутствует.", font=("Arial", 11), wraplength=400, justify=tk.LEFT)
        desc_label.pack(pady=8, padx=12, fill=tk.BOTH, expand=True)

        time_label = tk.Label(popup, text=f"Время: {reminder['due_time']}", font=("Arial", 10), fg="#424242")
        time_label.pack(pady=4, padx=12)

        close_btn = tk.Button(popup, text="OK", command=popup.destroy, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", padx=18, pady=8)
        close_btn.pack(pady=10)

        popup.after(NOTIFICATION_DURATION, lambda: popup.destroy() if popup.winfo_exists() else None)
        popup.protocol("WM_DELETE_WINDOW", popup.destroy)

        try:
            import winsound
            winsound.Beep(BEEP_FREQUENCY, BEEP_DURATION)
        except Exception:
            logger.debug("winsound недоступен, звук пропущен")

        logger.info("Показано pop-up уведомление для напоминания ID=%s", reminder['id'])

    def show_manual_notification(self, reminder: dict):
        """Показать уведомление вручную"""
        self._show_notification(reminder)

    def test_notification(self):
        """Тестовое уведомление"""
        test_reminder = {
            'title': '🧪 Тестовое уведомление',
            'description': 'Это тестовое уведомление для проверки работы системы.',
            'due_time': datetime.now().strftime(DATETIME_FORMAT),
            'status': 'Ожидает',
            'id': -1
        }
        self._show_notification(test_reminder)
        logger.info("Тестовое уведомление отправлено")
