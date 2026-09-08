import os
import logging
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = "https://andkuv001-ui.github.io/calculator-klient/"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[KeyboardButton(
        text="📦 Рассчитать пакеты",
        web_app=WebAppInfo(url=WEB_APP_URL),
    )]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)

    await update.message.reply_text(
        "Добро пожаловать! 🎉\n\n"
        "Нажмите кнопку ниже, чтобы открыть калькулятор пакетов.\n"
        "Вы сможете рассчитать стоимость и сразу отправить заявку.",
        reply_markup=reply_markup,
    )


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[KeyboardButton(
        text="📦 Рассчитать пакеты",
        web_app=WebAppInfo(url=WEB_APP_URL),
    )]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)

    await update.message.reply_text(
        "Откройте калькулятор для расчёта стоимости пакетов:",
        reply_markup=reply_markup,
    )


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = update.effective_message.web_app_data.data
    user = update.effective_user

    logger.info("WebApp data from %s (id=%s): %s", user.username, user.id, data)

    message_text = (
        f"📨 Новая заявка от @{user.username} (ID: {user.id}):\n\n"
        f"{data}"
    )

    await update.message.reply_text(
        "Спасибо! Ваша заявка отправлена. ✅\n"
        "Менеджер свяжется с вами в ближайшее время."
    )

    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
    except Exception as e:
        logger.error("Failed to forward data: %s", e)


def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set! Create .env file with BOT_TOKEN=<your_token>")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("calc", calc))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))

    logger.info("Bot started. Web App URL: %s", WEB_APP_URL)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
