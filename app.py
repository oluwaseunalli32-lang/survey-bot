import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters, ContextTypes
)

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token from environment variable (set on Render)
TOKEN = os.environ.get("BOT_TOKEN")

# Conversation states
Q1, Q2, Q3, Q4, DONE = range(5)

# Questions and options
QUESTIONS = {
    Q1: ("Do you want to earn money online?", ["Yes", "No"]),
    Q2: ("Are you willing to join a live call?", ["Yes", "No"]),
    Q3: ("Are you ready to explore a new p2e game?", ["Yes", "No"]),
    Q4: ("Will you join our Telegram channel?", ["Yes", "No"]),
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Please answer the following questions to qualify."
    )
    return await ask_question(update, context, Q1)

async def ask_question(update, context, state):
    question, options = QUESTIONS[state]
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"{state}:{opt}")] for opt in options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(question, reply_markup=reply_markup)
    else:
        await update.message.reply_text(question, reply_markup=reply_markup)
    return state

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    state_str, answer = query.data.split(":")
    state = int(state_str)

    if state == Q3:
        # Send image after Q3
        with open("survey_image.jpg", "rb") as photo:
            await query.message.reply_photo(photo=photo, caption="Did you know you can make up to ₦300k monthly?")

    next_state = state + 1
    if next_state in QUESTIONS:
        return await ask_question(update, context, next_state)
    else:
        # All questions answered
        await query.edit_message_text("Thank you! Here is your channel link: t.me/dailyplug37")
        # Start countdown
        context.job_queue.run_once(countdown_job, 1, data=query.message.chat_id)
        return DONE

async def countdown_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    seconds = 6 * 60 * 60  # 6 hours
    msg = await context.bot.send_message(chat_id, "⏳ Countdown: 06:00:00")
    for i in range(seconds, 0, -1):
        hours, rem = divmod(i, 3600)
        minutes, secs = divmod(rem, 60)
        text = f"⏳ Countdown: {hours:02d}:{minutes:02d}:{secs:02d}"
        await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=text)
        await asyncio.sleep(1)

async def hourly_reminder(context: ContextTypes.DEFAULT_TYPE):
    # Broadcast to all users (you should store chat_ids in a database)
    # For demo, we assume a global list
    for chat_id in context.bot_data.get("users", []):
        await context.bot.send_message(
            chat_id,
            "Reminder: Once we hit 10 joins, we host the live call tomorrow "
            "17th at 11:00 AM and 7:00 PM."
        )

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            Q1: [CallbackQueryHandler(handle_answer, pattern=r"^1:")],
            Q2: [CallbackQueryHandler(handle_answer, pattern=r"^2:")],
            Q3: [CallbackQueryHandler(handle_answer, pattern=r"^3:")],
            Q4: [CallbackQueryHandler(handle_answer, pattern=r"^4:")],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)

    # Schedule hourly reminder
    application.job_queue.run_repeating(hourly_reminder, interval=3600, first=10)

    # Run the bot (polling mode for simplicity; see webhook note below)
    application.run_polling()

if __name__ == "__main__":
    import asyncio
    main()
