import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

# Conversation states (Q1 = 0, Q2 = 1, Q3 = 2, Q4 = 3, DONE = 4)
Q1, Q2, Q3, Q4, DONE = range(5)

QUESTIONS = {
    Q1: ("Do you want to earn money online?", ["Yes", "No"]),
    Q2: ("Are you willing to join a live call?", ["Yes", "No"]),
    Q3: ("Are you ready to explore a new p2e game?", ["Yes", "No"]),
    Q4: ("Will you join our Telegram channel?", ["Yes", "No"]),
}

CHANNEL_LINK = "https://t.me/dailyplug37"
IMAGE_PATH = "survey_image.png"
IMAGE_CAPTION = "Did you know you can make up to ₦300k monthly?"

# In-memory store (resets when the worker restarts)
completed_users = set()

def fmt_time(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"⏳ Countdown: {h:02d}:{m:02d}:{s:02d}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Please answer the following questions to qualify."
    )
    return await ask_question(update, context, Q1)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE, state: int):
    question, options = QUESTIONS[state]
    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"{state}:{opt}")] for opt in options
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(question, reply_markup=reply_markup)
    else:
        await update.message.reply_text(question, reply_markup=reply_markup)
    return state

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logger.info("Received callback: %s", query.data)   # helpful for debugging
    await query.answer()

    state_str, _answer = query.data.split(":")
    state = int(state_str)

    # Send the image right after Q3 is answered
    if state == Q3:
        try:
            with open(IMAGE_PATH, "rb") as photo:
                await query.message.reply_photo(photo=photo, caption=IMAGE_CAPTION)
        except FileNotFoundError:
            logger.error("Image %s not found — sending text instead", IMAGE_PATH)
            await query.message.reply_text(IMAGE_CAPTION)

    next_state = state + 1
    if next_state in QUESTIONS:
        return await ask_question(update, context, next_state)

    # All questions answered
    chat_id = query.message.chat_id
    completed_users.add(chat_id)

    await query.edit_message_text(
        f"Thank you! Here is your channel link: {CHANNEL_LINK}\n\n"
        "Your countdown is starting below 👇"
    )
    context.job_queue.run_once(countdown_job, 1, data=chat_id)
    return DONE

async def countdown_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    total = 6 * 60 * 60  # 6 hours in seconds
    msg = await context.bot.send_message(chat_id, fmt_time(total))

    remaining = total
    while remaining > 0:
        # 60s steps normally, 5s steps in the final minute (avoids flood limits)
        step = 5 if remaining <= 60 else 60
        await asyncio.sleep(step)
        remaining = max(remaining - step, 0)
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=fmt_time(remaining),
            )
        except Exception as e:
            logger.warning("Countdown edit failed: %s", e)

    await context.bot.send_message(
        chat_id,
        "🎉 Countdown finished! The live call is starting now. Stay tuned.",
    )

async def hourly_reminder(context: ContextTypes.DEFAULT_TYPE):
    if not completed_users:
        return
    text = (
        "📢 Reminder: Once we hit 10 joins, we host the live call tomorrow "
        "17th at 11:00 AM and 7:00 PM."
    )
    for chat_id in list(completed_users):
        try:
            await context.bot.send_message(chat_id, text)
        except Exception as e:
            logger.warning("Reminder to %s failed: %s", chat_id, e)

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            Q1: [CallbackQueryHandler(handle_answer, pattern=r"^0:")],
            Q2: [CallbackQueryHandler(handle_answer, pattern=r"^1:")],
            Q3: [CallbackQueryHandler(handle_answer, pattern=r"^2:")],
            Q4: [CallbackQueryHandler(handle_answer, pattern=r"^3:")],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)

    # First reminder after 10s, then every hour
    application.job_queue.run_repeating(hourly_reminder, interval=3600, first=10)

    logger.info("Bot is starting…")
    application.run_polling()

if __name__ == "__main__":
    main()
