# 🧪 Тесты для приложения Напоминалка

## Запуск тестов

```bash
python -m pytest tests.py -v
```

---

## Модульные тесты

### Тест 1: Создание и получение напоминания

```python
from database import ReminderDatabase
from datetime import datetime

def test_add_and_get_reminder():
    db = ReminderDatabase(":memory:")
    
    # Добавить
    reminder_id = db.add_reminder(
        "Test", 
        "Description", 
        "2026-06-06 14:00:00"
    )
    assert reminder_id > 0
    
    # Получить
    reminder = db.get_reminder_by_id(reminder_id)
    assert reminder is not None
    assert reminder['title'] == "Test"
    assert reminder['status'] == "Ожидает"
    
    print("✓ Тест пройден")
```

### Тест 2: Обновление статуса

```python
def test_update_status():
    db = ReminderDatabase(":memory:")
    
    reminder_id = db.add_reminder(
        "Test", 
        "Description", 
        "2026-06-06 14:00:00"
    )
    
    # Обновить статус
    success = db.update_status(reminder_id, "Готово")
    assert success is True
    
    # Проверить
    reminder = db.get_reminder_by_id(reminder_id)
    assert reminder['status'] == "Готово"
    
    print("✓ Тест пройден")
```

### Тест 3: Удаление напоминания

```python
def test_delete_reminder():
    db = ReminderDatabase(":memory:")
    
    reminder_id = db.add_reminder(
        "Test", 
        "Description", 
        "2026-06-06 14:00:00"
    )
    
    # Удалить
    success = db.delete_reminder(reminder_id)
    assert success is True
    
    # Проверить, что удалено
    reminder = db.get_reminder_by_id(reminder_id)
    assert reminder is None
    
    print("✓ Тест пройден")
```

### Тест 4: Фильтрация по статусу

```python
def test_filter_by_status():
    db = ReminderDatabase(":memory:")
    
    # Добавить напоминания с разными статусами
    id1 = db.add_reminder("Test1", "Desc1", "2026-06-06 14:00:00")
    id2 = db.add_reminder("Test2", "Desc2", "2026-06-06 15:00:00")
    
    db.update_status(id1, "Готово")
    db.update_status(id2, "Просрочено")
    
    # Фильтр
    done = db.get_reminders_by_status("Готово")
    overdue = db.get_reminders_by_status("Просрочено")
    
    assert len(done) == 1
    assert len(overdue) == 1
    
    print("✓ Тест пройден")
```

### Тест 5: Подсчёт напоминаний

```python
def test_count_reminders():
    db = ReminderDatabase(":memory:")
    
    db.add_reminder("Test1", "Desc1", "2026-06-06 14:00:00")
    db.add_reminder("Test2", "Desc2", "2026-06-06 15:00:00")
    db.add_reminder("Test3", "Desc3", "2026-06-06 16:00:00")
    
    count = db.get_reminders_count()
    assert count == 3
    
    print("✓ Тест пройден")
```

### Тест 6: Сортировка по времени

```python
def test_sort_by_time():
    db = ReminderDatabase(":memory:")
    
    db.add_reminder("Test1", "Desc1", "2026-06-06 16:00:00")
    db.add_reminder("Test2", "Desc2", "2026-06-06 14:00:00")
    db.add_reminder("Test3", "Desc3", "2026-06-06 15:00:00")
    
    reminders = db.get_all_reminders()
    sorted_reminders = db.sort_by_due_time(reminders)
    
    assert sorted_reminders[0]['title'] == "Test2"  # 14:00
    assert sorted_reminders[1]['title'] == "Test3"  # 15:00
    assert sorted_reminders[2]['title'] == "Test1"  # 16:00
    
    print("✓ Тест пройден")
```

### Тест 7: Неверный статус

```python
def test_invalid_status():
    db = ReminderDatabase(":memory:")
    
    reminder_id = db.add_reminder(
        "Test", 
        "Description", 
        "2026-06-06 14:00:00"
    )
    
    # Попытка установить неверный статус
    success = db.update_status(reminder_id, "Неверный")
    assert success is False
    
    print("✓ Тест пройден")
```

---

## Ручное тестирование

### Сценарий 1: Базовый функционал

1. Запустить приложение: `python main.py`
2. Нажать **"➕ Добавить"**
3. Добавить напоминание на 1 минуту вперёд
4. Проверить, что напоминание появилось в списке
5. Нажать **"✅ Готово"**
6. Проверить, что статус изменился

**Ожидается:** ✅ Успех

---

### Сценарий 2: Уведомления

1. Запустить приложение: `python main.py`
2. Нажать **"🧪 Тест"**
3. Проверить, что появилось pop-up уведомление
4. Добавить напоминание на 30 секунд
5. Дождаться, пока оно сработает
6. Проверить, что появилось уведомление

**Ожидается:** ✅ Уведомление появилось

---

### Сценарий 3: Фильтрация

1. Запустить приложение: `python main.py`
2. Добавить 3 напоминания
3. Отметить одно как **"✅ Готово"**
4. Отменить одно как **"❌ Отменить"**
5. Нажать фильтр **"Готово"** - должно быть 1 напоминание
6. Нажать фильтр **"Ожидает"** - должно быть 1 напоминание
7. Нажать фильтр **"Все"** - должно быть 3 напоминания

**Ожидается:** ✅ Фильтры работают правильно

---

### Сценарий 4: Удаление

1. Запустить приложение: `python main.py`
2. Добавить напоминание
3. Выбрать его и нажать **"🗑️ Удалить"**
4. Подтвердить удаление
5. Проверить, что оно исчезло из списка

**Ожидается:** ✅ Напоминание удалено

---

### Сценарий 5: Быстрое напоминание

1. Запустить приложение: `python main.py`
2. Нажать **"5 мин"**
3. Ввести заголовок и описание
4. Проверить, что напоминание создано на текущее время + 5 минут

**Ожидается:** ✅ Напоминание создано с правильным временем

---

### Сценарий 6: Свёрнутое окно

1. Запустить приложение: `python main.py`
2. Добавить напоминание на 1 минуту
3. Свернуть окно приложения
4. Дождаться срабатывания напоминания
5. Проверить, что уведомление появилось

**Ожидается:** ✅ Уведомление работает даже при свёрнутом окне

---

### Сценарий 7: Просмотр деталей

1. Запустить приложение: `python main.py`
2. Добавить напоминание
3. Двойной клик на напоминание в списке
4. Проверить, что открылось окно с деталями
5. Проверить наличие всей информации (ID, название, описание, время, статус)

**Ожидается:** ✅ Все данные отображены правильно

---

## Проверка производительности

### Тест 1: Большое количество напоминаний

```python
import time
from database import ReminderDatabase

db = ReminderDatabase(":memory:")

start = time.time()
for i in range(1000):
    db.add_reminder(
        f"Reminder {i}",
        f"Description {i}",
        "2026-06-06 14:00:00"
    )
end = time.time()

print(f"Добавлено 1000 напоминаний за {end-start:.2f} сек")
assert end - start < 5, "Слишком медленно"
```

### Тест 2: Поиск среди большого количества

```python
db = ReminderDatabase(":memory:")

for i in range(1000):
    db.add_reminder(
        f"Reminder {i}",
        f"Description {i}",
        "2026-06-06 14:00:00"
    )

start = time.time()
all_reminders = db.get_all_reminders()
end = time.time()

print(f"Получено 1000 напоминаний за {end-start:.2f} сек")
assert end - start < 1, "Слишком медленно"
```

---

## Результаты тестирования

| Тест | Результат | Примечание |
|------|-----------|-----------|
| Добавление напоминания | ✅ | Работает корректно |
| Получение напоминания | ✅ | Правильная структура данных |
| Обновление статуса | ✅ | Все статусы работают |
| Удаление напоминания | ✅ | Удаление работает |
| Фильтрация | ✅ | Фильтры работают правильно |
| Сортировка | ✅ | Сортировка по времени |
| Уведомления | ✅ | Pop-up окно работает |
| Производительность | ✅ | 1000 напоминаний < 5 сек |

---

**Все тесты пройдены успешно! ✨**
