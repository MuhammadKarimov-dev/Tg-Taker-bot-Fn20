import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
TOKEN = '7861235950:AAFrjamSx87kHzgGHCpT93YviJ6_hoDbeEg'
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', 7474435850))
GROUP_CHAT_ID = int(os.getenv('GROUP_CHAT_ID', -1002515772883))

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set!")

user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        await update.message.reply_text(
            f"Salom, {user.first_name}! Yutuqni olish uchun raqamingizni yuboring.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📲 Yutuqni olish uchun raqamni yuborish", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text("Kechirasiz, xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        contact = update.message.contact
        user = update.effective_user
        phone_number = contact.phone_number
        username = user.username or "username yo'q"
        first_name = user.first_name

        user_data_store[user.id] = {
            "phone_number": phone_number,
            "username": username,
            "first_name": first_name,
            "location": None
        }

        location_keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Yutuqni olish uchun joylashuvingizni yuboring", request_location=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await update.message.reply_text(
            f"Rahmat, {first_name}.\nRaqamingiz qabul qilindi.\nEndi yutuqni olish uchun joylashuvingizni yuboring.",
            reply_markup=location_keyboard
        )
    except Exception as e:
        logger.error(f"Error in contact handler: {e}")
        await update.message.reply_text("Kechirasiz, xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        location = update.message.location
        user = update.effective_user

        if user.id not in user_data_store:
            await update.message.reply_text("Iltimos, avval raqamingizni yuboring.")
            return

        user_data_store[user.id]["location"] = (location.latitude, location.longitude)
        data = user_data_store[user.id]
        maps_link = f"https://www.google.com/maps?q={location.latitude},{location.longitude}"

        message_to_send = (
            f"Yangi foydalanuvchi yutuq ma'lumotlari:\n"
            f"Ism: {data['first_name']}\n"
            f"Telefon raqam: {data['phone_number']}\n"
            f"Username: @{data['username']}\n"
            f"Joylashuv: [Google Mapsda ko'rish]({maps_link})"
        )

        # Admin chatga yuborish
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message_to_send, parse_mode="Markdown")
        # Guruhga yuborish
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message_to_send, parse_mode="Markdown")

        await update.message.reply_text("Ma'lumotlar uchun rahmat! Yutug'ingiz tez orada sizga yetkaziladi.")
        
        # Clear user data after successful submission
        del user_data_store[user.id]
        
    except Exception as e:
        logger.error(f"Error in location handler: {e}")
        await update.message.reply_text("Kechirasiz, xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    try:
        app = ApplicationBuilder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
        app.add_handler(MessageHandler(filters.LOCATION, location_handler))
        app.add_error_handler(error_handler)

        logger.info("Bot ishga tushdi...")
        app.run_polling()
    except Exception as e:
        logger.error(f"Bot ishga tushishida xatolik yuz berdi: {e}")
