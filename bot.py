import os
import logging
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = "https://andkuv001-ui.github.io/calculator-klient/"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


CALC_BUTTON_TEXT = "📦 Рассчитать пакеты"


def get_inline_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=CALC_BUTTON_TEXT,
            web_app=WebAppInfo(url=WEB_APP_URL),
        )]
    ])


def get_channel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=CALC_BUTTON_TEXT,
            url=WEB_APP_URL,
        )]
    ])


def get_reply_keyboard():
    keyboard = [[KeyboardButton(
        text=CALC_BUTTON_TEXT,
        web_app=WebAppInfo(url=WEB_APP_URL),
    )]]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)


async def post_in_chat(context: ContextTypes.DEFAULT_TYPE, chat_id: int, is_channel: bool = False) -> None:
    text = (
        "📦 *Калькулятор пакетов с печатью*\n\n"
        "Рассчитайте стоимость вашего тиража за несколько секунд.\n"
        "Нажмите кнопку ниже, выберите параметры и отправьте заявку — "
        "мы свяжемся с вами в ближайшее время!"
    )

    kb = get_channel_keyboard() if is_channel else get_inline_keyboard()

    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=kb,
    )

    try:
        await context.bot.pin_chat_message(chat_id=chat_id, message_id=msg.message_id)
    except Exception as e:
        logger.warning("Could not pin message: %s", e)


async def start_private(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Добро пожаловать! 🎉\n\n"
        "Нажмите кнопку ниже, чтобы открыть калькулятор пакетов.\n"
        "Вы сможете рассчитать стоимость и сразу отправить заявку.",
        reply_markup=get_reply_keyboard(),
    )


async def post_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat

    if chat.type in ("channel",):
        sender = update.effective_user
        if sender:
            try:
                member = await chat.get_member(sender.id)
                if member.status not in ("administrator", "creator"):
                    return
            except Exception as e:
                logger.error("Failed to check channel member: %s", e)
                return

        channel_post = update.channel_post or update.effective_message
        if channel_post:
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=channel_post.message_id)
            except Exception as e:
                logger.warning("Could not delete channel post: %s", e)

        await post_in_chat(context, chat.id, is_channel=True)
        return

    if chat.type in ("group", "supergroup"):
        user = update.effective_user
        try:
            member = await chat.get_member(user.id)
            if member.status not in ("administrator", "creator"):
                await update.message.reply_text("Только администраторы могут публиковать калькулятор.")
                return
        except Exception as e:
            logger.error("Failed to check member status: %s", e)
            await update.message.reply_text("Не удалось проверить права.")
            return

        await update.message.delete()
        await post_in_chat(context, chat.id)
        return

    await update.message.reply_text("Эта команда работает в канале или группе.")


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = update.effective_message.web_app_data.data
    user = update.effective_user
    chat = update.effective_chat

    logger.info("WebApp data from %s (id=%s) in chat %s: %s", user.username, user.id, chat.id, data)

    full_name = user.full_name or "Неизвестный"
    username = f"@{user.username}" if user.username else "нет username"

    order_text = (
        "📨 *Новая заявка*\n\n"
        f"👤 {full_name} ({username})\n"
        f"🆔 ID: `{user.id}`\n"
        f"💬 Чат: `{chat.id}`\n\n"
        f"```{data}```"
    )

    if chat.type in ("private",):
        await update.message.reply_text(
            "Спасибо! Ваша заявка отправлена. ✅\n"
            "Менеджер свяжется с вами в ближайшее время."
        )

        forward_to = os.getenv("ADMIN_CHAT_ID")
        if forward_to:
            try:
                await context.bot.send_message(
                    chat_id=int(forward_to),
                    text=order_text,
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error("Failed to forward to admin: %s", e)
    else:
        await context.bot.send_message(
            chat_id=chat.id,
            text=order_text,
            parse_mode="Markdown",
        )


def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set! Create .env file with BOT_TOKEN=<your_token>")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_private, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("post", post_calculator, filters=filters.ChatType.GROUPS | filters.ChatType.CHANNEL))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))

    logger.info("Bot started. Web App URL: %s", WEB_APP_URL)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
