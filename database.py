import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

from config import DATETIME_FORMAT, VALID_STATUSES, OVERDUE_THRESHOLD
from logger import logger


class ReminderDatabase:
    """Класс для работы с базой данных напоминаний"""

    def __init__(self, db_path: str = "reminders.db"):
        """Инициализация базы данных"""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self._connect()
        self.init_database()

    def _connect(self):
        """Подключение к базе данных"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.connection.cursor()
            logger.info("Подключение к базе данных выполнено: %s", self.db_path)
        except sqlite3.Error as exc:
            logger.exception("Ошибка подключения к SQLite3: %s", exc)
            raise

    def init_database(self):
        """Инициализация базы данных, создание таблицы если её нет"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_time DATETIME NOT NULL,
                    status TEXT DEFAULT 'Ожидает',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.connection.commit()
            logger.info("Таблица reminders создана или уже существует")
        except sqlite3.Error as exc:
            logger.exception("Ошибка инициализации таблицы reminders: %s", exc)
            raise

    def _ensure_connection(self):
        """Проверка подключения перед выполнением запроса"""
        if self.connection is None or self.cursor is None:
            self._connect()

    def _validate_due_time(self, due_time: str) -> bool:
        """Проверка формата даты и времени"""
        try:
            datetime.strptime(due_time, DATETIME_FORMAT)
            return True
        except ValueError:
            return False

    def add_reminder(self, title: str, description: str, due_time: str) -> int:
        """Добавить новое напоминание"""
        title = title.strip()
        description = (description or "").strip()

        if not title:
            logger.warning("Попытка добавить напоминание без заголовка")
            return -1

        if not self._validate_due_time(due_time):
            logger.warning("Неверный формат времени для напоминания: %s", due_time)
            return -1

        self._ensure_connection()
        try:
            self.cursor.execute('''
                INSERT INTO reminders (title, description, due_time, status)
                VALUES (?, ?, ?, ?)
            ''', (title, description, due_time, 'Ожидает'))
            self.connection.commit()
            reminder_id = self.cursor.lastrowid
            logger.info("Добавлено новое напоминание: %s (ID=%s)", title, reminder_id)
            return reminder_id
        except sqlite3.Error as exc:
            logger.exception("Ошибка при добавлении напоминания: %s", exc)
            return -1

    def get_all_reminders(self) -> List[Dict]:
        """Получение всех напоминаний"""
        self._ensure_connection()
        try:
            self.cursor.execute('SELECT * FROM reminders ORDER BY due_time ASC')
            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except sqlite3.Error as exc:
            logger.exception("Ошибка при получении напоминаний: %s", exc)
            return []

    def get_due_reminders(self) -> List[Dict]:
        """Получить напоминания, которые пора показать"""
        self._ensure_connection()
        try:
            now = datetime.now().strftime(DATETIME_FORMAT)
            self.cursor.execute('''
                SELECT * FROM reminders
                WHERE status = 'Ожидает' AND due_time <= ?
                ORDER BY due_time ASC
            ''', (now,))
            rows = self.cursor.fetchall()
            reminders = [self._row_to_dict(row) for row in rows]
            logger.debug("Найдено %s срабатывающих напоминаний", len(reminders))
            return reminders
        except sqlite3.Error as exc:
            logger.exception("Ошибка при получении срабатывающих напоминаний: %s", exc)
            return []

    def sort_by_due_time(self, reminders: List[Dict]) -> List[Dict]:
        """Сортировка напоминаний по времени срабатывания"""
        return sorted(reminders, key=lambda x: x['due_time'])

    def update_status(self, reminder_id: int, new_status: str) -> bool:
        """Изменить статус напоминания"""
        if new_status not in VALID_STATUSES:
            logger.warning("Неверный статус для обновления: %s", new_status)
            return False

        self._ensure_connection()
        try:
            self.cursor.execute('''
                UPDATE reminders
                SET status = ?
                WHERE id = ?
            ''', (new_status, reminder_id))
            self.connection.commit()
            if self.cursor.rowcount == 0:
                logger.warning("Статус не был обновлен; напоминание ID=%s не найдено", reminder_id)
                return False
            logger.info("Статус напоминания ID=%s обновлен на %s", reminder_id, new_status)
            return True
        except sqlite3.Error as exc:
            logger.exception("Ошибка при обновлении статуса: %s", exc)
            return False

    def delete_reminder(self, reminder_id: int) -> bool:
        """Удалить напоминание"""
        self._ensure_connection()
        try:
            self.cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
            self.connection.commit()
            if self.cursor.rowcount == 0:
                logger.warning("Невозможно удалить: напоминание ID=%s не найдено", reminder_id)
                return False
            logger.info("Напоминание ID=%s удалено", reminder_id)
            return True
        except sqlite3.Error as exc:
            logger.exception("Ошибка при удалении напоминания: %s", exc)
            return False

    def mark_overdue(self) -> int:
        """Автоматически отметить просроченные напоминания"""
        self._ensure_connection()
        try:
            query = f"SELECT id FROM reminders WHERE status = 'Ожидает' AND datetime(due_time) < datetime('now', '-{OVERDUE_THRESHOLD} minute')"
            self.cursor.execute(query)
            overdue_ids = [row[0] for row in self.cursor.fetchall()]

            for reminder_id in overdue_ids:
                self.update_status(reminder_id, 'Просрочено')

            if overdue_ids:
                logger.info("Отмечено как просроченные %s напоминаний", len(overdue_ids))
            return len(overdue_ids)
        except sqlite3.Error as exc:
            logger.exception("Ошибка при отметке просроченных напоминаний: %s", exc)
            return 0

    def get_reminder_by_id(self, reminder_id: int) -> Optional[Dict]:
        """Получить конкретное напоминание по ID"""
        self._ensure_connection()
        try:
            self.cursor.execute('SELECT * FROM reminders WHERE id = ?', (reminder_id,))
            row = self.cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            logger.warning("Напоминание ID=%s не найдено", reminder_id)
            return None
        except sqlite3.Error as exc:
            logger.exception("Ошибка при получении напоминания: %s", exc)
            return None

    def get_reminders_count(self) -> int:
        """Получить общее количество напоминаний"""
        self._ensure_connection()
        try:
            self.cursor.execute('SELECT COUNT(*) FROM reminders')
            return self.cursor.fetchone()[0]
        except sqlite3.Error as exc:
            logger.exception("Ошибка при подсчёте напоминаний: %s", exc)
            return 0

    def get_reminders_by_status(self, status: str) -> List[Dict]:
        """Получить напоминания по статусу"""
        if status not in VALID_STATUSES:
            logger.warning("Неверный статус фильтрации: %s", status)
            return []

        self._ensure_connection()
        try:
            self.cursor.execute('''
                SELECT * FROM reminders
                WHERE status = ?
                ORDER BY due_time ASC
            ''', (status,))
            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except sqlite3.Error as exc:
            logger.exception("Ошибка при получении напоминаний по статусу: %s", exc)
            return []

    def _row_to_dict(self, row: tuple) -> Dict:
        """Преобразовать строку БД в словарь"""
        return {
            'id': row[0],
            'title': row[1],
            'description': row[2] or "",
            'due_time': row[3],
            'status': row[4],
            'created_at': row[5]
        }

    def close(self):
        """Закрыть соединение с БД"""
        try:
            if self.connection:
                self.connection.close()
                logger.info("Соединение с базой данных закрыто")
        except sqlite3.Error as exc:
            logger.exception("Ошибка при закрытии базы данных: %s", exc)

    def __del__(self):
        """Деструктор для закрытия соединения"""
        self.close()
