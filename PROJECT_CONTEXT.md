# PROJECT_CONTEXT.md — Калькулятор пакетов (Telegram Bot)

## Обзор проекта
Калькулятор расчёта стоимости пакетов с печатью, встроенный в Telegram бота.
Клиенты opening the calculator via a button in the Telegram channel, filling in parameters, and sending a request to the manager.

## Ключевые данные

| Параметр | Значение |
|----------|----------|
| GitHub репо | `https://github.com/andkuv001-ui/calculator-klient.git` |
| Web App URL | `https://andkuv001-ui.github.io/calculator-klient/` |
| Bot username | `@calculator_klient_bot` |
| Bot Token | `8706834807:AAFQzUxA6NAAojznavpmzYSzeVAci1h-zWA` |
| Канал | `@ZipDoy` (ZIP & DOY | Продажа упаковки) |
| User ID (andkuv1) | `385207085` |
| User ID (andkuv001) | `5477173725` |
| Chat ID канала | `-1002424392113` |

## Структура файлов

```
калькулятор клиентский/
├── index.html          # Калькулятор (Telegram Web App) — 239 строк
├── bot.py              # Telegram бот — 181 строка
├── requirements.txt    # python-telegram-bot==21.3, python-dotenv==1.0.0
├── .env                # BOT_TOKEN=..., WEBAPP_URL=..., ADMIN_CHAT_ID=
├── .env.example        # Шаблон
├── .gitignore          # .env, __pycache__, .DS_Store, venv/
└── README.md           # Инструкция
```

## Как запустить

```bash
cd "/Users/andrejkuvsinov/Desktop/калькулятор клиентский"
pip3 install -r requirements.txt
python3 bot.py
```

## Архитектура бота (bot.py)

### Команды
- `/start` — только в личных сообщениях (PRIVATE). Показывает ReplyKeyboard с кнопкой Web App.
- `/post` — в каналах и группах (CHANNEL, GROUPS). Админ публикует калькулятор.

### Три типа клавиатур
1. **ReplyKeyboardMarkup** (личные сообщения) — кнопка внизу экрана, `web_app=WebAppInfo`
2. **InlineKeyboardButton с web_app** (группы) — кнопка прямо под сообщением, `web_app=WebAppInfo`
3. **InlineKeyboardButton с url** (каналы) — кнопка открывает URL в браузере, `url=WEB_APP_URL`

> **Важно:** В каналах Telegram НЕ поддерживаются `web_app` кнопки (`Button_type_invalid`). Используется обычная URL-кнопка.

### Обработка WebApp данных
- `handle_web_app_data` — получает данные из калькулятора
- В личке: отправляет подтверждение клиенту + пересылает в `ADMIN_CHAT_ID` (если настроен)
- В группе/канале: публикует заявку прямо там

### Фильтры
```python
CommandHandler("start", ..., filters=filters.ChatType.PRIVATE)
CommandHandler("post", ..., filters=filters.ChatType.GROUPS | filters.ChatType.CHANNEL)
MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data)
```

## Калькулятор (index.html)

### Данные ( hardcode в JS)
- `BAGS` — цены пакетов по типам (vertical, horizontal, black, transparent) и размерам
- `PRINT` — цены печати по 4 группам и 5 диапазонам тиража
- `SVCS` — доп. услуги: доп. цвет (8.51/шт), золото/серебро (2.56/шт), подготовка макета (170 разово), пантон (бесплатно, инфо)
- `TYPES` — 4 типа пакетов

### Telegram Web App интеграция
```javascript
var tgApp = window.Telegram && window.Telegram.WebApp;
if (tgApp) { tgApp.ready(); tgApp.expand(); }
// sendData() — отправка данных боту (в личке/группе)
// Clipboard fallback — копирование в буфер (в канале/standalone)
```

### Функция copyResult()
Генерирует текст заявки и:
1. Пытается `tgApp.sendData(text)` (Telegram Web App)
2. Fallback на `navigator.clipboard.writeText(text)`

## Известные особенности

1. **Прокси**: Бот работает через прокси `127.0.0.1:10808` (автоматически через httpx/system proxy)
2. **GitHub Pages**: Калькулятор хостится на GitHub Pages — `https://andkuv001-ui.github.io/calculator-klient/`
3. **Бот не работает 24/7**: Запускается на компьютере пользователя. Для постоянной работы нужен VPS.
4. **Каналы vs Группы**: В каналах — URL-кнопка (калькулятор в браузере). В группах — Web App кнопка (калькулятор в Telegram).

## Git история

```
1b57bf9 docs: update README with channel support instructions
e4b1f37 fix: add channel support, use url button for channels, fix Button_type_invalid
1f25c7e feat: add group chat support, /post command, inline keyboard for Web App
95675d8 feat: add Telegram Web App calculator with bot
91d1cbc feat: Telegram Web App calculator with bot (initial)
```

## Что было решено

- **Button_type_invalid**: В каналах нельзя использовать `web_app` кнопки — заменено на `url`
- **Privacy Mode**: Бот имеет `can_read_all_group_messages: true` — privacy mode выключен
- **Канал не группа**: Изначально думали что это группа, оказалось канал — каналы обрабатываются через `channel_post` updates
- **Прокси**: Бот работает через локальный прокси (автоматически)
