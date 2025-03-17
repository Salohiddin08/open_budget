import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

TOKEN = "7984206417:AAGqGAAaQeo0pTjkk1hHRJQKpf_ajtlf4-4"
GROUP_ID = -1001234567890  
ADMIN_ID = 1913322681  

bot = Bot(token=TOKEN)
dp = Dispatcher()

conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    username TEXT,
    phone_number TEXT NOT NULL
);
""")
conn.commit()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )
    await message.answer("📞 Ro'yhatdan o'tish uchun telefon raqamingizni yuboring:", reply_markup=keyboard)

@dp.message(Command("send_my_db"))
async def send_database(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        try:
            await message.answer_document(types.FSInputFile("users.db"))
        except Exception as e:
            await message.answer(f"❌ Xatolik yuz berdi: {e}")
    else:
        await message.answer("❌ Bu buyruq faqat admin uchun!")

@dp.message()
async def contact_handler(message: types.Message):
    if message.contact:
        phone_number = message.contact.phone_number
        user_id = message.from_user.id
        full_name = message.from_user.full_name
        username = message.from_user.username or "Mavjud emas"

        cursor.execute("INSERT INTO users (user_id, full_name, username, phone_number) VALUES (?, ?, ?, ?)", 
                       (user_id, full_name, username, phone_number))
        conn.commit()

        await message.answer("✅ Ro'yhatdan muvaffaqiyatli o'tildi!")
        
        group_message = f"""
🆕 Yangi foydalanuvchi roʻyxatdan oʻtdi!
👤 Ism: {full_name}
🔗 Username: @{username}
📞 Telefon: {phone_number}
🆔 Telegram ID: {user_id}
        """
        await bot.send_message(GROUP_ID, group_message)
    else:
        await message.answer("❌ Iltimos, pastdagi tugma orqali telefon raqamingizni yuboring!")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
