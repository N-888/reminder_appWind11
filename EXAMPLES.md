# 📚 Примеры использования модулей Напоминалки

## Использование Database модуля

### Пример 1: Создание напоминания
```python
from database import ReminderDatabase

db = ReminderDatabase("reminders.db")

# Добавить новое напоминание
reminder_id = db.add_reminder(
    title="Встреча",
    description="Встреча с командой в 15:00",
    due_time="2026-06-06 15:00:00"
)

print(f"Напоминание добавлено с ID: {reminder_id}")
```

### Пример 2: Получение всех напоминаний
```python
from database import ReminderDatabase

db = ReminderDatabase("reminders.db")

# Получить все напоминания
all_reminders = db.get_all_reminders()

for reminder in all_reminders:
    print(f"[{reminder['id']}] {reminder['title']} - {reminder['status']}")
```

### Пример 3: Получение срабатывающих напоминаний
```python
from database import ReminderDatabase

db = ReminderDatabase("reminders.db")

# Получить напоминания, которые пора показать
due_reminders = db.get_due_reminders()

for reminder in due_reminders:
    print(f"Пора показать: {reminder['title']}")
```

### Пример 4: Изменение статуса
```python
from database import ReminderDatabase

db = ReminderDatabase("reminders.db")

# Отметить как выполненное
db.update_status(reminder_id=1, new_status="Готово")

# Отметить как просроченное
db.update_status(reminder_id=2, new_status="Просрочено")

# Отменить
db.update_status(reminder_id=3, new_status="Отменено")
```

### Пример 5: Удаление напоминания
```python
from database import ReminderDatabase

db = ReminderDatabase("reminders.db")

# Удалить напоминание по ID
db.delete_reminder(reminder_id=1)
print("Напоминание удалено")
```

### Пример 6: Фильтрация по статусу
```python
from database import ReminderDatabase

db = ReminderDatabase("reminders.db")

# Получить только активные напоминания
waiting = db.get_reminders_by_status("Ожидает")
done = db.get_reminders_by_status("Готово")
overdue = db.get_reminders_by_status("Просрочено")

print(f"Ожидающих: {len(waiting)}")
print(f"Готовых: {len(done)}")
print(f"Просроченных: {len(overdue)}")
```

### Пример 7: Подсчёт напоминаний
```python
from database import ReminderDatabase

db = ReminderDatabase("reminders.db")

# Получить общее количество
count = db.get_reminders_count()
print(f"Всего напоминаний: {count}")
```

---

## Использование NotificationManager модуля

### Пример 1: Запуск мониторинга
```python
from database import ReminderDatabase
from notifications import NotificationManager

db = ReminderDatabase("reminders.db")
notifier = NotificationManager(db)

# Запустить фоновый мониторинг
notifier.start_monitoring()

# Программа продолжает работать...
# Уведомления будут показаны автоматически

# Остановить мониторинг
# notifier.stop_monitoring()
```

### Пример 2: Обработка уведомлений
```python
from database import ReminderDatabase
from notifications import NotificationManager

def on_notification(reminder):
    """Пользовательская функция обработки уведомления"""
    print(f"Сработало напоминание: {reminder['title']}")
    # Здесь можно добавить дополнительную логику

db = ReminderDatabase("reminders.db")
notifier = NotificationManager(db, on_notification=on_notification)
notifier.start_monitoring()
```

### Пример 3: Тестовое уведомление
```python
from database import ReminderDatabase
from notifications import NotificationManager

db = ReminderDatabase("reminders.db")
notifier = NotificationManager(db)

# Показать тестовое уведомление
notifier.test_notification()
```

### Пример 4: Ручное отправление уведомления
```python
from database import ReminderDatabase
from notifications import NotificationManager

db = ReminderDatabase("reminders.db")
notifier = NotificationManager(db)

reminder = {
    'title': 'Важное напоминание',
    'description': 'Это важное напоминание',
    'due_time': '2026-06-06 14:30:00',
    'status': 'Ожидает',
    'id': 1
}

# Показать уведомление вручную
notifier.show_manual_notification(reminder)
```

---

## Использование GUI модуля

### Пример: Запуск интерфейса
```python
import tkinter as tk
from database import ReminderDatabase
from notifications import NotificationManager
from gui import ReminderGUI

# Инициализация компонентов
root = tk.Tk()
db = ReminderDatabase("reminders.db")
notifier = NotificationManager(db)
notifier.start_monitoring()

# Создание и запуск GUI
gui = ReminderGUI(root, db, notifier)
gui.run()
```

---

## Полный пример: Автоматическое создание тестовых напоминаний

```python
from database import ReminderDatabase
from notifications import NotificationManager
from datetime import datetime, timedelta
import time

# Инициализация
db = ReminderDatabase("reminders.db")
notifier = NotificationManager(db)
notifier.start_monitoring()

# Создание тестовых напоминаний
test_reminders = [
    ("Встреча с клиентом", "Офис, кабинет 301", datetime.now() + timedelta(minutes=5)),
    ("Отправить отчёт", "Главному менеджеру", datetime.now() + timedelta(minutes=10)),
    ("Обеденный перерыв", "Пообедать в столовой", datetime.now() + timedelta(hours=1)),
]

print("Создание тестовых напоминаний...")
for title, description, due_time in test_reminders:
    reminder_id = db.add_reminder(
        title=title,
        description=description,
        due_time=due_time.strftime("%Y-%m-%d %H:%M:%S")
    )
    print(f"✓ Создано: {title} (ID: {reminder_id})")

# Просмотр всех напоминаний
print("\nВсе напоминания:")
reminders = db.get_all_reminders()
for r in reminders:
    print(f"  [{r['id']}] {r['title']} - {r['due_time']} ({r['status']})")

# Держать программу работающей
print("\nМониторинг работает. Нажмите Ctrl+C для выхода...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    notifier.stop_monitoring()
    print("\nПрограмма завершена.")
```

---

## Расширение функционала

### Пример 1: Добавить звуковое уведомление
```python
import winsound
from datetime import datetime
from database import ReminderDatabase
from notifications import NotificationManager

def enhanced_notification(reminder):
    # Системное уведомление
    notifier.show_manual_notification(reminder)
    
    # Звуковой сигнал
    winsound.Beep(1000, 500)  # 1000 Hz, 500 ms
    winsound.Beep(1000, 500)
    
    # Логирование
    with open("notifications.log", "a") as log:
        log.write(f"{datetime.now()} - {reminder['title']}\n")

db = ReminderDatabase("reminders.db")
notifier = NotificationManager(db, on_notification=enhanced_notification)
notifier.start_monitoring()
```

### Пример 2: Повторяющееся напоминание
```python
from database import ReminderDatabase
from datetime import datetime, timedelta

db = ReminderDatabase("reminders.db")

def create_recurring_reminder(title, description, interval_days=1, count=5):
    """Создать повторяющееся напоминание"""
    start_time = datetime.now() + timedelta(days=1)
    
    for i in range(count):
        due_time = start_time + timedelta(days=i*interval_days)
        db.add_reminder(
            title=f"{title} (День {i+1})",
            description=description,
            due_time=due_time.strftime("%Y-%m-%d 09:00:00")
        )

# Создать напоминание на 5 дней
create_recurring_reminder(
    title="Ежедневная встреча",
    description="Встреча с командой",
    interval_days=1,
    count=5
)
```

---

## Отладка

### Просмотр содержимого базы данных
```python
from database import ReminderDatabase

db = ReminderDatabase("reminders.db")

print("=== Все напоминания ===")
for r in db.get_all_reminders():
    print(f"ID: {r['id']}")
    print(f"  Название: {r['title']}")
    print(f"  Описание: {r['description']}")
    print(f"  Время: {r['due_time']}")
    print(f"  Статус: {r['status']}")
    print(f"  Создано: {r['created_at']}")
    print()
```

### Проверка статистики
```python
from database import ReminderDatabase

db = ReminderDatabase("reminders.db")

waiting = len(db.get_reminders_by_status("Ожидает"))
done = len(db.get_reminders_by_status("Готово"))
overdue = len(db.get_reminders_by_status("Просрочено"))
cancelled = len(db.get_reminders_by_status("Отменено"))

print(f"""
Статистика:
  Ожидают: {waiting}
  Выполнены: {done}
  Просрочены: {overdue}
  Отменены: {cancelled}
  ВСЕГО: {waiting + done + overdue + cancelled}
""")
```

---

**Больше примеров найдёте в исходном коде модулей! 📚**
