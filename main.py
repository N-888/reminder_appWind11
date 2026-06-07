import tkinter as tk
from tkinter import messagebox
import os

from config import DATABASE_PATH
from database import ReminderDatabase
from logger import logger
from notifications import NotificationManager
from gui import ReminderGUI


def main():
    """Точка входа в приложение"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    root = None
    db = None
    notifier = None
    try:
        logger.info("🚀 Запуск Reminder App Wind11...")

        root = tk.Tk()
        db = ReminderDatabase(DATABASE_PATH)
        notifier = NotificationManager(db, root=root)
        notifier.start_monitoring()

        gui = ReminderGUI(root, db, notifier)
        logger.info("✅ Графический интерфейс загружен")

        gui.run()
    except Exception as exc:
        logger.exception("Не удалось запустить приложение: %s", exc)
        if root is not None:
            try:
                messagebox.showerror("Ошибка", f"Не удалось запустить приложение:\n{exc}")
            except Exception:
                pass
    finally:
        if notifier is not None:
            try:
                notifier.stop_monitoring()
            except Exception:
                pass
        if db is not None:
            db.close()
        logger.info("Приложение завершено")


if __name__ == "__main__":
    main()
