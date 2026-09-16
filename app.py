import os
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

# Conversation states (A = 0 … H = 7)
A, B, C, D, E, F, G, H = range(8)

# ─── Assets (upload these to your repo root, same folder as app.py) ─────
PROOF_1 = "proof_screenshot_1.png"
PROOF_2 = "proof_screenshot_2.png"
ACCOUNT_ID_EXAMPLE = "account_id_example.png"

# ─── Links ────────────────────────────────────────────────────────────────
WINGO_URL = (
    "https://t.me/WinGo_funBot/GAME?startapp="
    "152284909961c9c9c39ec841604b9a7604ad39803da3bbbe1d3e1c36d199bcfa"
)
ADMIN_URL = "https://t.me/ads2defiCEO"

# ─── Text content ────────────────────────────────────────────────────────
STEP_A_TEXT = (
    "🎮 *New Opportunity!*\n\n"
    "There's a new opportunity to earn money by playing games. "
    "Here's proof of a user who earned money from the platform."
)
STEP_B_TEXT = (
    "💰 *Here's a Real Withdrawal*\n\n"
    "This is what one of our users withdrew just 2 hours after playing."
)
STEP_C_TEXT = (
    "🎮 *Play. Earn. Withdraw.*\n\n"
    "This is an opportunity to earn money by simply playing games. "
    "Once you complete the required activity, your earnings can be "
    "processed for withdrawal within 2 hours."
)
STEP_D_TEXT = (
    "🔥 *You're almost there!*\n\n"
    "You're just one step away from getting started and potentially "
    "earning up to ₦29,000 from the available game activities."
)
STEP_E_TEXT = (
    "💰 *Getting Started*\n\n"
    "To access the game, the platform requires a ₦3,200 deposit.\n\n"
    "Don't worry — our team will fund your account so you can get started."
)
STEP_F_TEXT = (
    "🎮 *That's all you need to do!*\n\n"
    "Play the game, earn your rewards, and request your withdrawal. "
    "Withdrawals are expected to be processed within 2 hours, subject to "
    "the platform's terms and requirements."
)
STEP_G_TEXT = (
    "🚀 *Create Your Account*\n\n"
    "Sign up on Wingo to start playing and earning."
)
WINGO_SHARE_TEXT = (
    "🔥 I have won $12!\n"
    "👇 Click the link to help me win more!\n"
    "💰 Click the link to start playing and see what you can earn!"
)
STEP_H_TEXT = (
    "✅ *Almost Done!*\n\n"
    "Send your Wingo Account ID to our admin so your account can be funded.\n\n"
    "Please make sure you send the correct Account ID shown in the "
    "registration/account section."
)


# ─── Helpers ─────────────────────────────────────────────────────────────
def kb(*rows):
    """Build an InlineKeyboardMarkup from rows of (text, callback_or_url) tuples."""
    keyboard = []
    for row in rows:
        line = []
        for label, value in row:
            if value.startswith("http"):
                line.append(InlineKeyboardButton(label, url=value))
            else:
                line.append(InlineKeyboardButton(label, callback_data=value))
        keyboard.append(line)
    return InlineKeyboardMarkup(keyboard)


# ─── Step A ──────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: send Step A with proof screenshot 1."""
    markup = kb([("Learn More", "a_learn"), ("No, Thanks", "a_no")])
    try:
        with open(PROOF_1, "rb") as photo:
            await update.message.reply_photo(
                photo=photo, caption=STEP_A_TEXT,
                parse_mode="Markdown", reply_markup=markup,
            )
    except FileNotFoundError:
        logger.error("Missing %s — sending text only", PROOF_1)
        await update.message.reply_text(
            STEP_A_TEXT, parse_mode="Markdown", reply_markup=markup,
        )
    return A


async def step_a_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Remove buttons from Step A so they can't be tapped again
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass

    if query.data == "a_no":
        await query.message.reply_text("No problem. Thanks for your time!")
        return ConversationHandler.END

    # "Learn More" → Step B
    markup = kb([("Tell Me More", "b_more")])
    try:
        with open(PROOF_2, "rb") as photo:
            await query.message.reply_photo(
                photo=photo, caption=STEP_B_TEXT,
                parse_mode="Markdown", reply_markup=markup,
            )
    except FileNotFoundError:
        logger.error("Missing %s — sending text only", PROOF_2)
        await query.message.reply_text(
            STEP_B_TEXT, parse_mode="Markdown", reply_markup=markup,
        )
    return B


# ─── Step B ──────────────────────────────────────────────────────────────
async def step_b_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass
    await query.message.reply_text(
        STEP_C_TEXT, parse_mode="Markdown",
        reply_markup=kb([("Continue", "c_next")]),
    )
    return C


# ─── Step C ──────────────────────────────────────────────────────────────
async def step_c_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass
    await query.message.reply_text(
        STEP_D_TEXT, parse_mode="Markdown",
        reply_markup=kb([("Continue", "d_next")]),
    )
    return D


# ─── Step D ──────────────────────────────────────────────────────────────
async def step_d_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass
    await query.message.reply_text(
        STEP_E_TEXT, parse_mode="Markdown",
        reply_markup=kb([("Continue", "e_next")]),
    )
    return E


# ─── Step E ──────────────────────────────────────────────────────────────
async def step_e_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass
    await query.message.reply_text(
        STEP_F_TEXT, parse_mode="Markdown",
        reply_markup=kb([("Continue — I'm Ready", "f_next")]),
    )
    return F


# ─── Step F ──────────────────────────────────────────────────────────────
async def step_f_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass
    await query.message.reply_text(
        STEP_G_TEXT, parse_mode="Markdown",
        reply_markup=kb(
            [("Go to Wingo", "g_wingo")],
            [("I've Finished Signing Up", "g_done")],
        ),
    )
    return G


# ─── Step G ──────────────────────────────────────────────────────────────
async def step_g_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "g_wingo":
        # Send the $12 win/share message with a URL button to open Wingo
        await query.message.reply_text(
            WINGO_SHARE_TEXT,
            reply_markup=kb([("🎮 Open Wingo", WINGO_URL)]),
        )
        # Stay in G — user can still tap "I've Finished Signing Up"
        return G

    # "I've Finished Signing Up" → Step H
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass

    markup = kb([("Message Admin", ADMIN_URL)])
    try:
        with open(ACCOUNT_ID_EXAMPLE, "rb") as photo:
            await query.message.reply_photo(
                photo=photo, caption=STEP_H_TEXT,
                parse_mode="Markdown", reply_markup=markup,
            )
    except FileNotFoundError:
        logger.error("Missing %s — sending text only", ACCOUNT_ID_EXAMPLE)
        await query.message.reply_text(
            STEP_H_TEXT, parse_mode="Markdown", reply_markup=markup,
        )
    return H


# ─── Main ────────────────────────────────────────────────────────────────
def main():
    application = Application.builder().token(TOKEN).build()

    # Clear any leftover webhook so polling can't conflict with a stale one
    application.bot.delete_webhook(drop_pending_updates=True)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            A: [CallbackQueryHandler(step_a_choice, pattern=r"^a_")],
            B: [CallbackQueryHandler(step_b_choice, pattern=r"^b_")],
            C: [CallbackQueryHandler(step_c_choice, pattern=r"^c_")],
            D: [CallbackQueryHandler(step_d_choice, pattern=r"^d_")],
            E: [CallbackQueryHandler(step_e_choice, pattern=r"^e_")],
            F: [CallbackQueryHandler(step_f_choice, pattern=r"^f_")],
            G: [CallbackQueryHandler(step_g_choice, pattern=r"^g_")],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    application.add_handler(conv_handler)

    logger.info("Bot is starting…")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
