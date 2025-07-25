# 🤖 Telegram → WordPress AutoPoster Bot

Бот для автопубликации сообщений из Telegram в WordPress-сайт через REST API.

📌 Поддержка:
- Фото, заголовков и текста
- Категорий WordPress
- Yoast SEO полей (title + description)
- Очищает emoji из заголовков
- Настраивается через Telegram
- Хранит настройки пользователей и лог постов в SQLite

---

## 🧱 Структура проекта

```
telegram_wp_bot/
│
├── wp_bot/
│   ├── handlers/            # Обработчики событий
│   │   ├── connect.py
│   │   ├── post.py
│   │   └── logs.py
│   ├── keyboards/           # Инлайн-клавиатуры
│   │   └── confirm_remove.py
│   ├── config.py            # Загрузка конфигурации
│   ├── db.py                # SQLite: пользователи и логи
│   ├── wordpress.py         # REST API интеграция
│   └── main.py              # Запуск бота
│
├── telegram_wp_users.db     # База данных
├── requirements.txt         # Зависимости
├── .env                     # Секреты (не пушить)
└── README.md                # Документация
```

---

## ⚙️ Установка

### 🔽 1. Клонировать репозиторий:

```bash
git clone https://github.com/yourusername/telegram_wp_bot.git
cd telegram_wp_bot
```

### 📦 2. Установить зависимости:

```bash
pip install -r requirements.txt
```

### 🛠️ 3. Создать `.env` файл:

```env
BOT_TOKEN=your_telegram_bot_token
DB_PATH=telegram_wp_users.db
```

> 🛡️ `config.py` автоматически подтянет переменные.

### ▶️ 4. Запуск:

```bash
python wp_bot/main.py
```

---

## 💬 Принцип работы

1. Пользователь подключает сайт, вводя URL, логин, пароль.
2. Выбирает Telegram-канал, с которого бот будет принимать сообщения.
3. Задаёт категории WordPress.
4. Отправляет пост в Telegram в формате:

```
Заголовок поста
Описание поста...
(добавить фото)
```

5. Бот:
   - Загружает изображение как Featured Image
   - Очищает заголовок от emoji
   - Публикует пост через REST API
   - Добавляет meta-теги для Yoast SEO
   - Сохраняет лог

---

## 🧩 Поддержка Yoast SEO

Бот автоматически добавляет:

- 🏷️ `yoast_wpseo_title`
- 📝 `yoast_wpseo_metadesc`
- 📂 `yoast_wpseo_primary_category`

---

## 🔐 Безопасность

- Пароли хранятся в SQLite (рекомендуется ограничить доступ к БД)
- Используйте `.env` и `.gitignore`, чтобы не пушить конфиденциальные данные.

---

## 🛠 Поддержка и TODO

- [x] Поддержка фото
- [x] Категории
- [x] Поддержка нескольких пользователей
- [x] Выбор подкатегорий
- [ ] Удаление старых постов
- [ ] Редактирование постов через бота

---

## 🧑‍💻 Автор бота

Разрабатывается и дорабатывается Ravil (tg: https://t.me/nd_admin95).
