# 🔌 API Documentation - Напоминалка

## Содержание
1. [ReminderDatabase](#reminddatabase)
2. [NotificationManager](#notificationmanager)
3. [ReminderGUI](#remindergui)
4. [Data Models](#data-models)

---

## ReminderDatabase

Класс для работы с базой данных SQLite3.

### Инициализация

```python
from database import ReminderDatabase

db = ReminderDatabase(db_path="reminders.db")
```

**Параметры:**
- `db_path` (str): Путь к файлу базы данных. По умолчанию "reminders.db"

---

### Методы

#### `add_reminder(title, description, due_time) -> int`

Добавить новое напоминание.

**Параметры:**
- `title` (str): Заголовок напоминания (не пустой)
- `description` (str): Описание напоминания (может быть пустым)
- `due_time` (str): Дата и время в формате "YYYY-MM-DD HH:MM:SS"

**Возвращает:**
- `int`: ID добавленного напоминания или -1 при ошибке

**Пример:**
```python
reminder_id = db.add_reminder(
    "Встреча",
    "С клиентом Иван",
    "2026-06-06 14:30:00"
)
print(f"Добавлено напоминание с ID: {reminder_id}")
```

---

#### `get_all_reminders() -> List[Dict]`

Получить все напоминания, отсортированные по времени.

**Возвращает:**
- `List[Dict]`: Список напоминаний

**Структура возвращаемого словаря:**
```python
{
    'id': int,
    'title': str,
    'description': str,
    'due_time': str,  # "YYYY-MM-DD HH:MM:SS"
    'status': str,    # "Ожидает", "Готово", "Просрочено", "Отменено"
    'created_at': str # "YYYY-MM-DD HH:MM:SS"
}
```

**Пример:**
```python
reminders = db.get_all_reminders()
for r in reminders:
    print(f"{r['title']} - {r['status']}")
```

---

#### `get_due_reminders() -> List[Dict]`

Получить напоминания, которые срабатывают сейчас (время пришло, статус "Ожидает").

**Возвращает:**
- `List[Dict]`: Список срабатывающих напоминаний

**Пример:**
```python
due = db.get_due_reminders()
for reminder in due:
    print(f"Пора показать: {reminder['title']}")
```

---

#### `get_reminders_by_status(status) -> List[Dict]`

Получить напоминания по статусу.

**Параметры:**
- `status` (str): Статус из списка: "Ожидает", "Готово", "Просрочено", "Отменено"

**Возвращает:**
- `List[Dict]`: Список напоминаний с указанным статусом

**Пример:**
```python
waiting = db.get_reminders_by_status("Ожидает")
done = db.get_reminders_by_status("Готово")
```

---

#### `get_reminder_by_id(reminder_id) -> Optional[Dict]`

Получить конкретное напоминание по ID.

**Параметры:**
- `reminder_id` (int): ID напоминания

**Возвращает:**
- `Dict`: Напоминание или `None` если не найдено

**Пример:**
```python
reminder = db.get_reminder_by_id(1)
if reminder:
    print(f"Найдено: {reminder['title']}")
```

---

#### `update_status(reminder_id, new_status) -> bool`

Изменить статус напоминания.

**Параметры:**
- `reminder_id` (int): ID напоминания
- `new_status` (str): Новый статус

**Возвращает:**
- `bool`: True если успешно, False если ошибка

**Допустимые статусы:**
- `"Ожидает"` - ожидание срабатывания
- `"Готово"` - выполнено
- `"Просрочено"` - время прошло, не отмечено как готово
- `"Отменено"` - отменено пользователем

**Пример:**
```python
db.update_status(1, "Готово")
db.update_status(2, "Отменено")
```

---

#### `delete_reminder(reminder_id) -> bool`

Удалить напоминание.

**Параметры:**
- `reminder_id` (int): ID напоминания

**Возвращает:**
- `bool`: True если успешно, False если ошибка

**Пример:**
```python
if db.delete_reminder(1):
    print("Напоминание удалено")
```

---

#### `mark_overdue() -> int`

Автоматически отметить просроченные напоминания (время вышло больше чем на 1 минуту).

**Возвращает:**
- `int`: Количество отмеченных напоминаний

**Пример:**
```python
count = db.mark_overdue()
print(f"Отмечено просроченных: {count}")
```

---

#### `sort_by_due_time(reminders) -> List[Dict]`

Отсортировать список напоминаний по времени срабатывания.

**Параметры:**
- `reminders` (List[Dict]): Список напоминаний

**Возвращает:**
- `List[Dict]`: Отсортированный список

**Пример:**
```python
unsorted = db.get_reminders_by_status("Готово")
sorted_list = db.sort_by_due_time(unsorted)
```

---

#### `get_reminders_count() -> int`

Получить общее количество напоминаний.

**Возвращает:**
- `int`: Количество напоминаний в базе

**Пример:**
```python
total = db.get_reminders_count()
print(f"Всего напоминаний: {total}")
```

---

#### `close()`

Закрыть соединение с базой данных.

**Пример:**
```python
db.close()
```

---

## NotificationManager

Класс для управления уведомлениями.

### Инициализация

```python
from database import ReminderDatabase
from notifications import NotificationManager

db = ReminderDatabase()
notifier = NotificationManager(db, on_notification=None)
```

**Параметры:**
- `db` (ReminderDatabase): Экземпляр базы данных
- `on_notification` (Callable, optional): Функция-обработчик при срабатывании уведомления

---

### Методы

#### `start_monitoring()`

Запустить фоновый мониторинг напоминаний.

Проверяет каждую секунду, есть ли напоминания для показа.

**Пример:**
```python
notifier.start_monitoring()
print("Мониторинг запущен")
```

---

#### `stop_monitoring()`

Остановить фоновый мониторинг.

**Пример:**
```python
notifier.stop_monitoring()
print("Мониторинг остановлен")
```

---

#### `test_notification()`

Показать тестовое уведомление.

**Пример:**
```python
notifier.test_notification()
```

---

#### `show_manual_notification(reminder)`

Показать уведомление вручную.

**Параметры:**
- `reminder` (Dict): Словарь напоминания

**Пример:**
```python
reminder = db.get_reminder_by_id(1)
if reminder:
    notifier.show_manual_notification(reminder)
```

---

## ReminderGUI

Класс для графического интерфейса.

### Инициализация

```python
import tkinter as tk
from gui import ReminderGUI

root = tk.Tk()
gui = ReminderGUI(root, db, notifier)
```

**Параметры:**
- `root` (tk.Tk): Главное окно Tkinter
- `db` (ReminderDatabase): Экземпляр базы данных
- `notifier` (NotificationManager): Менеджер уведомлений

---

### Методы

#### `add_reminder()`

Открыть диалог добавления нового напоминания.

---

#### `refresh_reminders()`

Обновить список напоминаний на экране.

---

#### `mark_as_done()`

Отметить выбранное напоминание как выполненное.

---

#### `cancel_reminder()`

Отменить выбранное напоминание.

---

#### `delete_reminder()`

Удалить выбранное напоминание.

---

#### `apply_filter(filter_name)`

Применить фильтр к напоминаниям.

**Параметры:**
- `filter_name` (str): Название фильтра ("Все", "Ожидает", "Готово", "Просрочено", "Отменено")

---

#### `run()`

Запустить главное окно приложения.

---

## Data Models

### Напоминание (Reminder)

```python
{
    'id': int,                          # Уникальный идентификатор
    'title': str,                       # Заголовок (обязательно)
    'description': str,                 # Описание (может быть пустым)
    'due_time': str,                    # Формат: "YYYY-MM-DD HH:MM:SS"
    'status': str,                      # Один из: "Ожидает", "Готово", "Просрочено", "Отменено"
    'created_at': str                   # Формат: "YYYY-MM-DD HH:MM:SS"
}
```

### Статусы

| Статус | Значение | Описание |
|--------|----------|---------|
| Ожидает | "Ожидает" | Напоминание ещё не срабатывало |
| Готово | "Готово" | Задача выполнена |
| Просрочено | "Просрочено" | Время прошло, задача не выполнена |
| Отменено | "Отменено" | Задача отменена пользователем |

---

## Обработка ошибок

### Исключение при добавлении напоминания

```python
reminder_id = db.add_reminder("Встреча", "С клиентом", "2026-06-06 14:30:00")
if reminder_id == -1:
    print("Ошибка при добавлении напоминания")
```

### Исключение при обновлении статуса

```python
success = db.update_status(1, "Неверный статус")
if not success:
    print("Ошибка: неверный статус")
```

---

## Примеры использования API

### Пример 1: Полный цикл

```python
from database import ReminderDatabase
from notifications import NotificationManager
from datetime import datetime, timedelta

# Инициализация
db = ReminderDatabase()
notifier = NotificationManager(db)
notifier.start_monitoring()

# Добавить напоминание
reminder_id = db.add_reminder(
    "Купить продукты",
    "Молоко, хлеб, яйца",
    (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
)

# Получить все напоминания
all_reminders = db.get_all_reminders()
print(f"Всего: {len(all_reminders)}")

# Отметить как готово
db.update_status(reminder_id, "Готово")

# Удалить
db.delete_reminder(reminder_id)

# Остановить
notifier.stop_monitoring()
db.close()
```

### Пример 2: Пользовательский обработчик

```python
def my_notification_handler(reminder):
    print(f"Сработало: {reminder['title']}")
    # Может быть: отправка email, логирование, и т.д.

db = ReminderDatabase()
notifier = NotificationManager(db, on_notification=my_notification_handler)
notifier.start_monitoring()
```

---

**Документация актуальна для версии 1.0**
