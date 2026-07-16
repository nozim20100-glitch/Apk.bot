from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import database as db
from keyboards import main_keyboard, videos_reply_keyboard

router = Router()


class BrowseVideoState(StatesGroup):
    selecting = State()


@router.message(F.text == "🎬 Videolar")
async def show_all_videos(message: Message, state: FSMContext) -> None:
    videos = db.get_all_videos()
    if not videos:
        await message.answer("📭 Hozircha hech qanday video mavjud emas.")
        return
    await state.set_state(BrowseVideoState.selecting)
    await message.answer("🎬 <b>Videoni tanlang:</b>",
                         reply_markup=videos_reply_keyboard(),
                         parse_mode="HTML")


@router.message(BrowseVideoState.selecting, F.text)
async def video_selected(message: Message, state: FSMContext) -> None:
    text = message.text.strip()

    if text == "🔙 Orqaga":
        await state.clear()
        await message.answer("🏠 Asosiy menyu",
                             reply_markup=main_keyboard(message.from_user.id))
        return

    videos = db.get_all_videos()
    vid = next((v for v in videos if v["title"] == text), None)
    if not vid:
        return

    caption = f"🎬 <b>{vid['title']}</b>"
    if vid["description"]:
        caption += f"\n\n📄 {vid['description']}"

    await message.answer_video(
        video=vid["file_id"],
        caption=caption,
        parse_mode="HTML",
    )
