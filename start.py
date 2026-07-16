from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import main_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = message.from_user
    ism = user.full_name if user else "Foydalanuvchi"

    await message.answer(
        f"👋 Assalomu alaykum, <b>{ism}</b>!\n\n"
        "📱 <b>APKlar</b> — ilovalar yuklab olish\n"
        "🎬 <b>Videolar</b> — qiziqarli videolar\n"
        "📝 <b>Yozuvlar</b> — foydali maqolalar\n\n"
        "Kerakli bo'limni tanlang 👇",
        reply_markup=main_keyboard(user.id),
        parse_mode="HTML",
    )
