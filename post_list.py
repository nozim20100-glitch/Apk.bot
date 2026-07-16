from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import database as db
from keyboards import main_keyboard, posts_reply_keyboard

router = Router()


class BrowsePostState(StatesGroup):
    selecting = State()


@router.message(F.text == "📝 Yozuvlar")
async def show_all_posts(message: Message, state: FSMContext) -> None:
    posts = db.get_all_posts()
    if not posts:
        await message.answer("📭 Hozircha hech qanday yozuv mavjud emas.")
        return
    await state.set_state(BrowsePostState.selecting)
    await message.answer("📝 <b>Yozuvni tanlang:</b>",
                         reply_markup=posts_reply_keyboard(),
                         parse_mode="HTML")


@router.message(BrowsePostState.selecting, F.text)
async def post_selected(message: Message, state: FSMContext) -> None:
    text = message.text.strip()

    if text == "🔙 Orqaga":
        await state.clear()
        await message.answer("🏠 Asosiy menyu",
                             reply_markup=main_keyboard(message.from_user.id))
        return

    posts = db.get_all_posts()
    post = next((p for p in posts if p["title"] == text), None)
    if not post:
        return

    body = f"📝 <b>{post['title']}</b>"
    if post["content"]:
        body += f"\n\n{post['content']}"

    if post["photo_file_id"]:
        await message.answer_photo(
            photo=post["photo_file_id"],
            caption=body,
            parse_mode="HTML",
        )
    else:
        await message.answer(body, parse_mode="HTML")
