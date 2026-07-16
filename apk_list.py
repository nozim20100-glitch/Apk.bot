from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import database as db
from keyboards import main_keyboard, apks_reply_keyboard

router = Router()


class BrowseApkState(StatesGroup):
    selecting = State()


@router.message(F.text == "📱 APKlar")
async def show_all_apks(message: Message, state: FSMContext) -> None:
    apks = db.get_all_apks()
    if not apks:
        await message.answer("📭 Hozircha hech qanday APK mavjud emas.")
        return
    await state.set_state(BrowseApkState.selecting)
    await message.answer("📱 <b>APKni tanlang:</b>",
                         reply_markup=apks_reply_keyboard(),
                         parse_mode="HTML")


@router.message(BrowseApkState.selecting, F.text)
async def apk_selected(message: Message, state: FSMContext) -> None:
    text = message.text.strip()

    # Orqaga tugmasi
    if text == "🔙 Orqaga":
        await state.clear()
        await message.answer("🏠 Asosiy menyu",
                             reply_markup=main_keyboard(message.from_user.id))
        return

    # APK nomiga mos qidirish
    apks = db.get_all_apks()
    apk = next((a for a in apks if a["name"] == text), None)
    if not apk:
        return  # noma'lum tugma — e'tiborsiz

    # Tavsif
    if apk["description"]:
        await message.answer(
            f"📦 <b>{apk['name']}</b>\n\n📄 {apk['description']}",
            parse_mode="HTML",
        )

    # Video
    if apk["video_file_id"]:
        await message.answer_video(
            video=apk["video_file_id"],
            caption=f"🎥 <b>{apk['name']}</b>",
            parse_mode="HTML",
        )

    # APK fayl
    await message.answer_document(
        document=apk["file_id"],
        caption=f"📥 <b>{apk['name']}</b>\nYuklab olganingiz uchun rahmat! 🙏",
        parse_mode="HTML",
    )
