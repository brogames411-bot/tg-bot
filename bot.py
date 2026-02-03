import asyncio
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

# ================== ENV ==================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

BONUS_FILE = os.getenv("BONUS_FILE", "images.jpg")
BONUS_CAPTION = os.getenv("BONUS_CAPTION", "🎁 Спасибо за подписку! Вот твой файл.")

# ================== BOT ==================
dp = Dispatcher()


# ================== KEYBOARDS ==================
def subscribe_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Подписаться", url=CHANNEL_LINK)
    kb.button(text="✅ Проверить подписку", callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()


def get_file_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎁 Получить файл", callback_data="get_file")
    kb.adjust(1)
    return kb.as_markup()


# ================== SUB CHECK ==================
async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ("creator", "administrator", "member")
    except TelegramBadRequest:
        return False


# ================== SEND FILE ==================
async def send_file(bot: Bot, user_id: int):
    file = FSInputFile(BONUS_FILE)
    await bot.send_document(user_id, file, caption=BONUS_CAPTION)


# ================== START ==================
@dp.message(Command("start"))
async def start(message: Message):
    bot = message.bot
    ok = await is_subscribed(bot, message.from_user.id)

    if ok:
        await message.answer(
            "✅ Подписка есть!\nНажми кнопку чтобы получить файл:",
            reply_markup=get_file_kb()
        )
    else:
        await message.answer(
            "🔒 Чтобы получить файл, подпишись на канал:",
            reply_markup=subscribe_kb()
        )


# ================== CHECK SUB ==================
@dp.callback_query(F.data == "check_sub")
async def check_sub(call: CallbackQuery):
    ok = await is_subscribed(call.bot, call.from_user.id)

    if ok:
        await call.message.edit_text(
            "✅ Подписка подтверждена!\nТеперь можешь получить файл 🎁",
            reply_markup=get_file_kb()
        )
    else:
        await call.answer("❌ Подписка не найдена!", show_alert=True)


# ================== GET FILE ==================
@dp.callback_query(F.data == "get_file")
async def get_file(call: CallbackQuery):
    ok = await is_subscribed(call.bot, call.from_user.id)

    if not ok:
        await call.answer("🔒 Сначала подпишись!", show_alert=True)
        await call.message.edit_text(
            "Подпишись на канал:",
            reply_markup=subscribe_kb()
        )
        return

    await send_file(call.bot, call.from_user.id)
    await call.answer("🎁 Файл отправлен!")


# ================== MAIN ==================
async def main():
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
