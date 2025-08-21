import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command

TOKEN = "7984206417:AAGqGAAaQeo0pTjkk1hHRJQKpf_ajtlf4-4"
ADMIN_ID = 1913322681
GROUP_ID = -1001234567890

bot = Bot(token=TOKEN)
dp = Dispatcher()

# DB yaratish
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    username TEXT,
    phone_number TEXT NOT NULL
);
""")
conn.commit()

VOTE_LINK = "https://openbudget.uz/boards/initiatives/initiative/52/e5cd7258-b1b0-478f-840a-3aa555c0770b"

def get_vote_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗳️ Ovoz berish", url=VOTE_LINK)]
        ]
    )

# /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if user:
        # Foydalanuvchi allaqachon ro'yxatdan o'tgan bo'lsa
        await message.answer("Assalomu alaykum! 👋\nSiz allaqachon ro‘yxatdan o‘tgan ekansiz.")
        await message.answer("📢 Ovoz berish uchun pastdagi tugmani bosing:", reply_markup=get_vote_keyboard())
    else:
        await message.answer("Assalomu alaykum! 👋\nOpen Budget botimizga xush kelibsiz.")
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
            resize_keyboard=True
        )
        await message.answer("📞 Ro'yhatdan o'tish uchun telefon raqamingizni yuboring:", reply_markup=keyboard)

# Kontakt handler
@dp.message()
async def contact_handler(message: types.Message):
    if message.contact:
        user_id = message.from_user.id
        full_name = message.from_user.full_name
        username = message.from_user.username or "Mavjud emas"
        phone_number = message.contact.phone_number

        # Foydalanuvchi allaqachon ro'yxatdan o'tgan bo'lsa, yangilanmaydi
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.execute(
                "INSERT INTO users (user_id, full_name, username, phone_number) VALUES (?, ?, ?, ?)",
                (user_id, full_name, username, phone_number)
            )
            conn.commit()

            # Admin kanalga xabar
            await bot.send_message(GROUP_ID, f"🆕 Yangi foydalanuvchi ro‘yxatdan oʻtdi:\n👤 {full_name}\n🔗 @{username}\n📞 {phone_number}\n🆔 {user_id}")

        # ReplyKeyboard ni yo'q qilish
        remove_keyboard = ReplyKeyboardRemove()
        
        # Ovoz berish tugmasi
        await message.answer("✅ Ro'yhatdan muvaffaqiyatli o'tdingiz!\n📢 Ovoz berish uchun pastdagi tugmani bosing:", 
                             reply_markup=get_vote_keyboard())
        await message.answer("Telefon raqam tugmasi yo'qolgan.", reply_markup=remove_keyboard)

    else:
        await message.answer("❌ Iltimos, pastdagi tugma orqali telefon raqamingizni yuboring!")

# Admin DB jo'natish
@dp.message(Command("send_my_db"))
async def send_database(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        try:
            await message.answer_document(types.FSInputFile("users.db"))
        except Exception as e:
            await message.answer(f"❌ Xatolik yuz berdi: {e}")
    else:
        await message.answer("❌ Bu buyruq faqat admin uchun!")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
