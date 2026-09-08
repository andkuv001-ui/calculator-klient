import os
import logging
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://andkuv001-ui.github.io/calculator-klient/")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[KeyboardButton(
        text="📦 Рассчитать пакеты",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Добро пожаловать!\n\n"
        "Нажмите кнопку ниже, чтобы открыть калькулятор и рассчитать стоимость пакетов.",
        reply_markup=reply_markup
    )


async def calc_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[KeyboardButton(
        text="📦 Рассчитать пакеты",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Откройте калькулятор:",
        reply_markup=reply_markup
    )


async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = update.effective_message.web_app_data.data
    user = update.effective_user
    logger.info("Заявка от %s (ID: %s): %s", user.first_name, user.id, data)

    await update.message.reply_text(
        "✅ Ваша заявка принята!\n\n"
        f"📋 Данные:\n{data}\n\n"
        "Наш менеджер свяжется с вами в ближайшее время."
    )


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан. Создайте файл .env с токеном от BotFather.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("calc", calc_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    logger.info("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()
