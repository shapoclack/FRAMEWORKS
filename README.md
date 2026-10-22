# Система учета тем курсовых работ

Веб-приложение на фреймворке **Django** с интерфейсом на **Bootstrap 5**, предназначенное для централизованного учета, распределения и контроля статусов выполнения курсовых работ между студентами и научными руководителями кафедры.

Проект разработан в рамках сквозного курса практических работ:
- **ПР1–ПР3:** Консольное приложение, ООП-модели, JSON-хранилище, реляционное проектирование;
- **ПР5–ПР6:** Архитектура Django (MVT), маршрутизация HTTP, шаблонизатор DTL, статические файлы и Bootstrap 5;
- **ПР7 (Текущий этап):** Слой реляционной СУБД **SQLite**, проектирование схемы, импорт данных из JSON, разработка SQL-запросов и интеграция с Django-представлениями через стандартную библиотеку `sqlite3`.

---

## 1. Текущий этап разработки (Практическая работа № 7)

На этапе ПР7 в проект внедрен самостоятельный реляционный слой базы данных SQLite:
- Спроектирована и создана база данных SQLite: `data/coursework.sqlite` (и копия `data/roomly.sqlite` для совместимости);
- Описана схема таблиц средствами SQL в файле `sql/schema.sql` (таблицы `students`, `supervisors`, `topics`, `status_history`);
- Реализован Python-модуль подключения `db/database.py` с автоматическим включением проверки ограничений внешних ключей (`PRAGMA foreign_keys = ON`);
- Создан скрипт миграции `db/import_json.py`, выполняющий перенос данных из JSON-файлов в таблицы реляционной БД с использованием транзакций (`commit`/`rollback`) и пакетной вставки `executemany()`;
- Разработан и протестирован каталог из **17 SQL-запросов** в файле `sql/queries.sql`, охватывающий все обязательные категории: выборка, фильтрация `WHERE`, объединение таблиц `JOIN`, агрегатные функции `COUNT`/`SUM`/`AVG`/`MIN`/`MAX`, группировка `GROUP BY` и фильтрация групп `HAVING`;
- Выполнена интеграция запросов SQLite в Django-представления (`coursework/views.py`, `core/views.py`) с использованием `conn.row_factory = sqlite3.Row` и параметризованных запросов с плейсхолдерами `?` (без конкатенации строк и f-строк);
- Реализованы ключевые пользовательские сценарии:
  1. **Каталог тем:** `/coursework/topics/` — выборка тем, поиск и фильтрация;
  2. **Темы в работе:** `/coursework/active/` — соединение трёх таблиц (`JOIN`) для вывода закрепленных тем со студентами и преподавателями;
  3. **Поиск свободных тем:** `/coursework/available/` — параметризованный поиск тем без закрепления с фильтром по дедлайну;
  4. **Статистика и аналитика:** `/coursework/statistics/` — агрегатные функции, группировка нагрузки по руководителям и фильтрация групп `HAVING`;
  5. **Списки преподавателей и студентов:** `/coursework/supervisors/`, `/coursework/students/`;
  6. **Детальная карточка темы:** `/coursework/topics/<id>/` — полная информация и аудит статусов.
- Организована сквозная навигация по сайту через именованные маршруты Django (`{% url %}`).

---

## 2. Структура базы данных SQLite (ПР7)

### Таблица `students` (Студенты кафедры)
| Поле | Тип SQLite | Ограничения | Назначение |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY` | Уникальный идентификатор студента |
| `full_name` | `TEXT` | `NOT NULL` | Фамилия, имя, отчество |
| `group_name` | `TEXT` | `NOT NULL` | Академическая группа (например, `ПИ-21-1`) |
| `direction` | `TEXT` | — | Направление подготовки |
| `email` | `TEXT` | `NOT NULL UNIQUE` | Электронная почта студента |
| `created_at` | `TEXT` | `NOT NULL DEFAULT (datetime('now'))` | Дата и время внесения записи |

### Таблица `supervisors` (Научные руководители)
| Поле | Тип SQLite | Ограничения | Назначение |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY` | Уникальный идентификатор преподавателя |
| `full_name` | `TEXT` | `NOT NULL` | Фамилия, имя, отчество |
| `degree` | `TEXT` | — | Ученая степень (к.т.н., д.т.н., к.ф.-м.н.) |
| `position` | `TEXT` | — | Должность (доцент, профессор, ст. преподаватель) |
| `email` | `TEXT` | `NOT NULL UNIQUE` | Рабочая электронная почта |
| `max_topics` | `INTEGER` | `NOT NULL DEFAULT 5 CHECK (max_topics BETWEEN 1 AND 20)` | Лимит руководства темами |
| `created_at` | `TEXT` | `NOT NULL DEFAULT (datetime('now'))` | Дата внесения записи |

### Таблица `topics` (Темы курсовых работ)
| Поле | Тип SQLite | Ограничения | Назначение |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY` | Уникальный идентификатор темы |
| `title` | `TEXT` | `NOT NULL` | Наименование темы курсовой работы |
| `description` | `TEXT` | — | Развернутая аннотация и требования |
| `supervisor_id` | `INTEGER` | `NOT NULL, FOREIGN KEY REFERENCES supervisors(id) ON DELETE RESTRICT` | Связь с научным руководителем |
| `student_id` | `INTEGER` | `FOREIGN KEY REFERENCES students(id) ON DELETE SET NULL` | Связь со студентом (NULL, если свободна) |
| `status` | `TEXT` | `NOT NULL DEFAULT 'свободна' CHECK (status IN ('свободна', 'закреплена', 'на проверке', 'защищена'))` | Жизненный цикл темы |
| `deadline` | `TEXT` | — | Плановый дедлайн сдачи работы (`YYYY-MM-DD`) |
| `created_at` | `TEXT` | `NOT NULL DEFAULT (datetime('now'))` | Дата внесения темы |

### Таблица `status_history` (Аудит изменений статусов)
| Поле | Тип SQLite | Ограничения | Назначение |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Идентификатор записи аудита |
| `topic_id` | `INTEGER` | `NOT NULL, FOREIGN KEY REFERENCES topics(id) ON DELETE CASCADE` | Ссылка на тему |
| `old_status` | `TEXT` | `NOT NULL` | Предыдущий статус |
| `new_status` | `TEXT` | `NOT NULL` | Новый статус |
| `changed_at` | `TEXT` | `NOT NULL DEFAULT (datetime('now'))` | Время фиксации изменения |
| `changed_by` | `TEXT` | — | Инициатор операции (система / пользователь) |

---

## 3. Организация файлов проекта

```text
COURSEWORK/
├── db/                       # Слой прямого доступа к SQLite (ПР7)
│   ├── __init__.py
│   ├── database.py           # Модуль подключения и PRAGMA foreign_keys = ON
│   └── import_json.py        # Скрипт миграции данных из JSON в SQLite
├── sql/                      # Каталог SQL-скриптов
│   ├── schema.sql            # DDL: создание таблиц и связей SQLite
│   └── queries.sql           # 17 документированных запросов всех категорий
├── data/                     # Файлы данных
│   ├── students.json         # Исходные данные студентов
│   ├── supervisors.json      # Исходные данные руководителей
│   ├── topics.json           # Исходные данные тем курсовых
│   └── coursework.sqlite     # Реляционная база данных SQLite (ПР7)
├── coursework_project/       # Конфигурация проекта Django
│   ├── settings.py
│   └── urls.py
├── core/                     # Приложение общих страниц (Главная, О проекте, HTTP)
│   ├── views.py              # Запросы SQLite для главной страницы
│   └── urls.py
├── coursework/               # Приложение предметной области
│   ├── views.py              # Представления на sqlite3.Row и параметрах ?
│   ├── urls.py               # Маршруты: topics, active, available, statistics
│   └── tests.py              # Тесты моделей и представлений (21 тест)
├── templates/                # HTML-шаблоны Bootstrap 5
│   ├── base.html             # Каркас с адаптивным меню и переходами
│   ├── core/
│   │   ├── home.html         # Главный дашборд со сводкой из SQLite
│   │   ├── about.html
│   │   └── http_info.html
│   └── coursework/
│       ├── topic_list.html   # Каталог тем и ссылка на поиск свободных
│       ├── topic_detail.html # Карточка темы и аудит
│       ├── active_topics.html# Темы в работе (JOIN трёх таблиц)
│       ├── available.html    # Поиск свободных тем (параметризованный NOT IN)
│       ├── statistics.html   # Аналитика (GROUP BY, HAVING, агрегаты)
│       ├── student_list.html # Список студентов кафедры
│       └── supervisor_list.html # Список руководителей и нагрузка
├── tests/                    # Набор тестов pytest
│   ├── test_pr7_db.py        # Проверка подключения, схемы и 17 SQL-запросов
│   ├── test_students.py
│   ├── test_supervisors.py
│   └── tests_topics.py
├── main.py                   # Консольный интерфейс (ПР1–ПР2)
├── manage.py
├── pytest.ini
├── .flake8
└── requirements.txt
```

---

## 4. Классификация SQL-запросов (`sql/queries.sql`)

Файл `sql/queries.sql` содержит 17 отлаженных запросов:

1. **Выборка списков объектов (`SELECT`, `ORDER BY`, `LIMIT`, `OFFSET`):**
   - Запрос 1: Получение всех тем с сортировкой по названию (`ORDER BY title ASC`);
   - Запрос 2: Список преподавателей по алфавиту (`ORDER BY full_name ASC`);
   - Запрос 3: Пагинация списка студентов (`LIMIT 5 OFFSET 0`).
2. **Фильтрация данных (`WHERE`):**
   - Запрос 4: Выборка свободных тем (`WHERE status = 'свободна' AND student_id IS NULL`);
   - Запрос 5: Полнотекстовый поиск по подстроке (`WHERE title LIKE ? OR description LIKE ?`);
   - Запрос 6: Студенты без тем через подзапрос (`WHERE id NOT IN (SELECT student_id FROM topics ...)`);
   - Запрос 7: Темы с дедлайном в заданном диапазоне (`WHERE deadline BETWEEN ? AND ?`).
3. **Соединение таблиц (`JOIN`):**
   - Запрос 8: Полная информация о темах с объединением `topics`, `supervisors` и `students`;
   - Запрос 9: Активные темы в процессе выполнения со всеми контактами участников;
   - Запрос 10: Свободные темы конкретного преподавателя (`JOIN ... WHERE supervisor_id = ?`).
4. **Агрегатные функции (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`):**
   - Запрос 11: Подсчет общего числа тем и условные суммы `SUM(CASE WHEN ...)` по каждому статусу;
   - Запрос 12: Агрегатные показатели лимитов нагрузки преподавателей (`AVG`, `MIN`, `MAX`).
5. **Группировка записей (`GROUP BY`):**
   - Запрос 13: Количество тем у каждого руководителя (`LEFT JOIN` + `GROUP BY` для учета преподавателей без тем);
   - Запрос 14: Распределение тем по статусам (`GROUP BY status`);
   - Запрос 15: Распределение студентов по академическим группам (`GROUP BY group_name`).
6. **Фильтрация групп (`HAVING`):**
   - Запрос 16: Преподаватели с повышенной нагрузкой (`GROUP BY sv.id HAVING COUNT(t.id) > 1`);
   - Запрос 17: Учебные группы с количеством студентов более 1 (`GROUP BY group_name HAVING COUNT(*) > 1`).

---

## 5. Маршруты веб-приложения и пользовательские сценарии

| URL-маршрут | Имя маршрута | View-функция | SQL-механизм и назначение |
|---|---|---|---|
| `/` | `core:home` | `core.views.home` | Сводный дашборд: агрегатные `COUNT(*)`, `SUM(CASE)` и последние добавленные темы |
| `/coursework/topics/` | `coursework:topic_list` | `coursework.views.topic_list` | Полный каталог тем, параметризованный поиск `LIKE` и фильтрация по статусу/руководителю |
| `/coursework/active/` | `coursework:active_topics` | `coursework.views.active_topics` | Темы в работе: `JOIN` трёх таблиц (`topics`, `supervisors`, `students`) |
| `/coursework/available/` | `coursework:available` | `coursework.views.available_topics` | Форма поиска свободных тем по дедлайну и ключевым словам с подзапросом `NOT IN` |
| `/coursework/statistics/` | `coursework:statistics` | `coursework.views.statistics` | Страница аналитики: агрегаты, `GROUP BY`, фильтрация групп `HAVING` |
| `/coursework/supervisors/` | `coursework:supervisor_list` | `coursework.views.supervisor_list` | Преподаватели кафедры и расчет нагрузки через `LEFT JOIN` и `GROUP BY` |
| `/coursework/students/` | `coursework:student_list` | `coursework.views.student_list` | Студенты кафедры и сопоставление закрепленных тем через `LEFT JOIN` |
| `/coursework/topics/<id>/` | `coursework:topic_detail` | `coursework.views.topic_detail` | Детальный просмотр темы и аудит изменений из `status_history` |
| `/about/` | `core:about` | `core.views.about` | Описание архитектуры системы и стека технологий |
| `/http-info/` | `core:http_info` | `core.views.http_info` | Интерактивный разбор элементов входящего HTTP-запроса |

---

## 6. Запуск и воспроизведение результата

### 1. Активация виртуального окружения
```bash
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 2. Импорт данных из JSON в SQLite
```bash
python -m db.import_json
```
*Результат:* применение схемы `sql/schema.sql`, перенос 6 студентов, 4 руководителей, 8 тем в файл `data/coursework.sqlite`.

### 3. Запуск сервера разработки Django
```bash
python manage.py runserver
```
Сервер доступен по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 7. Контрольные проверки качества кода (Чек-лист ПР7)

### Проверка конфигурации Django:
```bash
python manage.py check
```
*Результат:* `System check identified no issues (0 silenced)`.

### Запуск полного набора тестов pytest (22 теста):
```bash
pytest -v
```
*Результат:* 22 пройденных теста (`22 passed`), включая проверку соединения, внешних ключей, фабрики `sqlite3.Row`, синтаксиса и выполнения всех 17 SQL-запросов.

### Проверка стиля кода по стандарту PEP 8:
```bash
flake8 . --extend-exclude=venv
```
*Результат:* 0 ошибок и предупреждений.

### Запуск тестов представлений Django:
```bash
python manage.py test
```
*Результат:* 21 пройденный тест (`21 passed`, `OK`).

---

## 8. Метка фиксации в Git (Git Commit)

Изменения этапа ПР7 зафиксированы коммитами с префиксом `PR7:`:
```bash
PR7: add SQLite database, schema, JSON import, SQL queries and Django views
```
