from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import database as db
from keyboards import (
    ADMIN_KEYBOARD,
    main_keyboard,
    categories_inline,
    apks_inline,
    apk_edit_fields_inline,
    confirm_delete_inline,
    videos_inline,
    video_edit_fields_inline,
    confirm_delete_video_inline,
    posts_inline,
    post_edit_fields_inline,
    confirm_delete_post_inline,
)

ADMIN_ID = 8639222385
router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ─── FSM States ───────────────────────────────────────────────────────────────

class CategoryState(StatesGroup):
    waiting_name = State()


class AddApkState(StatesGroup):
    select_category = State()
    waiting_file    = State()
    waiting_name    = State()
    waiting_desc    = State()
    waiting_video   = State()


class EditApkState(StatesGroup):
    select_apk    = State()
    select_field  = State()
    waiting_value = State()
    select_cat    = State()


class DeleteApkState(StatesGroup):
    select_apk = State()


class AddVideoState(StatesGroup):
    waiting_file  = State()
    waiting_title = State()
    waiting_desc  = State()


class EditVideoState(StatesGroup):
    select_video  = State()
    select_field  = State()
    waiting_value = State()


class DeleteVideoState(StatesGroup):
    select_video = State()


class AddPostState(StatesGroup):
    waiting_title   = State()
    waiting_content = State()
    waiting_photo   = State()


class EditPostState(StatesGroup):
    select_post   = State()
    select_field  = State()
    waiting_value = State()


class DeletePostState(StatesGroup):
    select_post = State()


# Eski state-lar (qoldirish uchun)
class AddVideoApkState(StatesGroup):
    select_apk    = State()
    waiting_video = State()


class AddDescState(StatesGroup):
    select_apk   = State()
    waiting_desc = State()


# ─── Admin panel kirish ───────────────────────────────────────────────────────

@router.message(F.text == "⚙️ Admin panel")
async def open_admin_panel(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("⚙️ <b>Admin panel</b>", reply_markup=ADMIN_KEYBOARD, parse_mode="HTML")


@router.message(F.text == "🔙 Orqaga")
async def back_to_main(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🏠 Asosiy menyu", reply_markup=main_keyboard(message.from_user.id))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=ADMIN_KEYBOARD)


@router.callback_query(F.data == "ap:cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.answer()


# ─── 📂 Kategoriya yaratish ──────────────────────────────────────────────────

@router.message(F.text == "📂 Kategoriya yaratish")
async def start_add_category(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    await state.set_state(CategoryState.waiting_name)
    await message.answer("📂 Yangi kategoriya nomini kiriting:\n\n/cancel — bekor qilish")


@router.message(CategoryState.waiting_name, F.text)
async def save_category(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    ok = db.add_category(name)
    await state.clear()
    msg = f"✅ <b>{name}</b> kategoriyasi yaratildi!" if ok else f"⚠️ <b>{name}</b> allaqachon mavjud."
    await message.answer(msg, parse_mode="HTML", reply_markup=ADMIN_KEYBOARD)


# ─── ➕ APK qo'shish ──────────────────────────────────────────────────────────

@router.message(F.text == "➕ APK qo'shish")
async def start_add_apk(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    cats = db.get_all_categories()
    if not cats:
        await message.answer("⚠️ Avval kamida bitta kategoriya yarating.")
        return
    await state.set_state(AddApkState.select_category)
    await message.answer("📂 Kategoriyani tanlang:", reply_markup=categories_inline("addcat"))


@router.callback_query(AddApkState.select_category, F.data.startswith("addcat:"))
async def apk_cat_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    cat_id = int(callback.data.split(":")[1])
    cat = db.get_category_by_id(cat_id)
    await state.update_data(category_id=cat_id)
    await state.set_state(AddApkState.waiting_file)
    await callback.message.edit_text(
        f"📂 Kategoriya: <b>{cat['name']}</b>\n\n📦 .apk faylini yuboring:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AddApkState.waiting_file, F.document)
async def apk_file_in(message: Message, state: FSMContext) -> None:
    if not message.document.file_name.lower().endswith(".apk"):
        await message.answer("❌ Faqat .apk fayl yuboring.")
        return
    await state.update_data(file_id=message.document.file_id)
    await state.set_state(AddApkState.waiting_name)
    await message.answer("✅ Fayl qabul qilindi!\n\n📝 APK nomini kiriting:")


@router.message(AddApkState.waiting_file)
async def apk_file_bad(message: Message) -> None:
    await message.answer("❌ .apk fayl yuboring yoki /cancel bilan bekor qiling.")


@router.message(AddApkState.waiting_name, F.text)
async def apk_name_in(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(AddApkState.waiting_desc)
    await message.answer("📄 Tavsif kiriting  |  /skip — o'tkazish")


@router.message(AddApkState.waiting_desc, F.text)
async def apk_desc_in(message: Message, state: FSMContext) -> None:
    await state.update_data(
        description=None if message.text.strip() == "/skip" else message.text.strip()
    )
    await state.set_state(AddApkState.waiting_video)
    await message.answer("🎥 Video yuboring  |  /skip — o'tkazish")


@router.message(AddApkState.waiting_video, F.video)
async def apk_video_in(message: Message, state: FSMContext) -> None:
    await state.update_data(video_file_id=message.video.file_id)
    await _finish_add_apk(message, state)


@router.message(AddApkState.waiting_video, F.text)
async def apk_video_skip(message: Message, state: FSMContext) -> None:
    await state.update_data(video_file_id=None)
    await _finish_add_apk(message, state)


async def _finish_add_apk(message: Message, state: FSMContext) -> None:
    d = await state.get_data()
    db.add_apk(d["name"], d["file_id"], d.get("category_id"), d.get("description"), d.get("video_file_id"))
    await state.clear()
    await message.answer(f"✅ <b>{d['name']}</b> muvaffaqiyatli saqlandi!", parse_mode="HTML", reply_markup=ADMIN_KEYBOARD)


# ─── ✏️ APK tahrirlash ────────────────────────────────────────────────────────

@router.message(F.text == "✏️ APK tahrirlash")
async def start_edit_apk(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    if not db.get_all_apks():
        await message.answer("📭 Bazada APK mavjud emas.")
        return
    await state.set_state(EditApkState.select_apk)
    await message.answer("✏️ Qaysi APKni tahrirlaysiz?", reply_markup=apks_inline("editapk"))


@router.callback_query(EditApkState.select_apk, F.data.startswith("editapk:"))
async def edit_apk_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    apk_id = int(callback.data.split(":")[1])
    apk = db.get_apk_by_id(apk_id)
    await state.update_data(apk_id=apk_id)
    await state.set_state(EditApkState.select_field)
    await callback.message.edit_text(
        f"✏️ <b>{apk['name']}</b> — nimani o'zgartirish kerak?",
        reply_markup=apk_edit_fields_inline(apk_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(EditApkState.select_field, F.data.startswith("ef:"))
async def edit_field_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    _, apk_id, field = callback.data.split(":")
    await state.update_data(apk_id=int(apk_id), field=field)

    if field == "category_id":
        await state.set_state(EditApkState.select_cat)
        await callback.message.edit_text("📂 Yangi kategoriyani tanlang:", reply_markup=categories_inline("editcat"))
    elif field == "file_id":
        await state.set_state(EditApkState.waiting_value)
        await callback.message.edit_text("📦 Yangi .apk faylini yuboring:")
    elif field == "video_file_id":
        await state.set_state(EditApkState.waiting_value)
        await callback.message.edit_text("🎥 Yangi videoni yuboring:")
    else:
        prompts = {"name": "📝 Yangi nomni kiriting:", "description": "📄 Yangi tavsifni kiriting:"}
        await state.set_state(EditApkState.waiting_value)
        await callback.message.edit_text(prompts.get(field, "Yangi qiymat kiriting:"))
    await callback.answer()


@router.callback_query(EditApkState.select_cat, F.data.startswith("editcat:"))
async def edit_cat_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    cat_id = int(callback.data.split(":")[1])
    d = await state.get_data()
    db.update_apk_field(d["apk_id"], "category_id", cat_id)
    cat = db.get_category_by_id(cat_id)
    await state.clear()
    await callback.message.edit_text(f"✅ Kategoriya → <b>{cat['name']}</b>", parse_mode="HTML")
    await callback.answer()


@router.message(EditApkState.waiting_value, F.document)
async def edit_file_in(message: Message, state: FSMContext) -> None:
    if not message.document.file_name.lower().endswith(".apk"):
        await message.answer("❌ Faqat .apk fayl yuboring.")
        return
    d = await state.get_data()
    db.update_apk_field(d["apk_id"], "file_id", message.document.file_id)
    await state.clear()
    await message.answer("✅ APK fayl yangilandi!", reply_markup=ADMIN_KEYBOARD)


@router.message(EditApkState.waiting_value, F.video)
async def edit_video_in(message: Message, state: FSMContext) -> None:
    d = await state.get_data()
    db.update_apk_field(d["apk_id"], "video_file_id", message.video.file_id)
    await state.clear()
    await message.answer("✅ Video yangilandi!", reply_markup=ADMIN_KEYBOARD)


@router.message(EditApkState.waiting_value, F.text)
async def edit_text_in(message: Message, state: FSMContext) -> None:
    d = await state.get_data()
    db.update_apk_field(d["apk_id"], d["field"], message.text.strip())
    await state.clear()
    await message.answer("✅ Yangilandi!", reply_markup=ADMIN_KEYBOARD)


# ─── 🗑 APK o'chirish ─────────────────────────────────────────────────────────

@router.message(F.text == "🗑 APK o'chirish")
async def start_delete_apk(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    if not db.get_all_apks():
        await message.answer("📭 Bazada APK mavjud emas.")
        return
    await state.set_state(DeleteApkState.select_apk)
    await message.answer("🗑 Qaysi APKni o'chirmoqchisiz?", reply_markup=apks_inline("delapk"))


@router.callback_query(DeleteApkState.select_apk, F.data.startswith("delapk:"))
async def delete_apk_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    apk_id = int(callback.data.split(":")[1])
    apk = db.get_apk_by_id(apk_id)
    await state.clear()
    await callback.message.edit_text(
        f"⚠️ <b>{apk['name']}</b> o'chirilsinmi?",
        reply_markup=confirm_delete_inline(apk_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delconfirm:"))
async def delete_confirmed(callback: CallbackQuery) -> None:
    apk_id = int(callback.data.split(":")[1])
    apk = db.get_apk_by_id(apk_id)
    name = apk["name"] if apk else "APK"
    db.delete_apk(apk_id)
    await callback.message.edit_text(f"🗑 <b>{name}</b> o'chirildi.", parse_mode="HTML")
    await callback.answer("O'chirildi!")


# ─── 🎬 Video qo'shish (mustaqil) ────────────────────────────────────────────

@router.message(F.text == "🎬 Video qo'shish")
async def start_add_video(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AddVideoState.waiting_file)
    await message.answer("🎬 Videoni yuboring:\n\n/cancel — bekor qilish")


@router.message(AddVideoState.waiting_file, F.video)
async def add_video_file_in(message: Message, state: FSMContext) -> None:
    await state.update_data(file_id=message.video.file_id)
    await state.set_state(AddVideoState.waiting_title)
    await message.answer("📝 Video sarlavhasini kiriting:")


@router.message(AddVideoState.waiting_file)
async def add_video_bad(message: Message) -> None:
    await message.answer("❌ Video yuboring yoki /cancel bilan bekor qiling.")


@router.message(AddVideoState.waiting_title, F.text)
async def add_video_title_in(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await state.set_state(AddVideoState.waiting_desc)
    await message.answer("📄 Tavsif kiriting  |  /skip — o'tkazish")


@router.message(AddVideoState.waiting_desc, F.text)
async def add_video_desc_in(message: Message, state: FSMContext) -> None:
    d = await state.get_data()
    desc = None if message.text.strip() == "/skip" else message.text.strip()
    db.add_video(d["title"], d["file_id"], desc)
    await state.clear()
    await message.answer(f"✅ <b>{d['title']}</b> videosi saqlandi!", parse_mode="HTML", reply_markup=ADMIN_KEYBOARD)


# ─── ✏️ Video tahrirlash ──────────────────────────────────────────────────────

@router.message(F.text == "✏️ Video tahrirlash")
async def start_edit_video(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    if not db.get_all_videos():
        await message.answer("📭 Bazada video mavjud emas.")
        return
    await state.set_state(EditVideoState.select_video)
    await message.answer("✏️ Qaysi videoni tahrirlaysiz?", reply_markup=videos_inline("editvid"))


@router.callback_query(EditVideoState.select_video, F.data.startswith("editvid:"))
async def edit_video_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    vid_id = int(callback.data.split(":")[1])
    vid = db.get_video_by_id(vid_id)
    await state.update_data(vid_id=vid_id)
    await state.set_state(EditVideoState.select_field)
    await callback.message.edit_text(
        f"✏️ <b>{vid['title']}</b> — nimani o'zgartirish kerak?",
        reply_markup=video_edit_fields_inline(vid_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(EditVideoState.select_field, F.data.startswith("vf:"))
async def edit_video_field_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    _, vid_id, field = callback.data.split(":")
    await state.update_data(vid_id=int(vid_id), field=field)
    await state.set_state(EditVideoState.waiting_value)
    if field == "file_id":
        await callback.message.edit_text("🎬 Yangi videoni yuboring:")
    elif field == "title":
        await callback.message.edit_text("📝 Yangi sarlavhani kiriting:")
    else:
        await callback.message.edit_text("📄 Yangi tavsifni kiriting:")
    await callback.answer()


@router.message(EditVideoState.waiting_value, F.video)
async def edit_video_file_in(message: Message, state: FSMContext) -> None:
    d = await state.get_data()
    db.update_video_field(d["vid_id"], "file_id", message.video.file_id)
    await state.clear()
    await message.answer("✅ Video fayl yangilandi!", reply_markup=ADMIN_KEYBOARD)


@router.message(EditVideoState.waiting_value, F.text)
async def edit_video_text_in(message: Message, state: FSMContext) -> None:
    d = await state.get_data()
    db.update_video_field(d["vid_id"], d["field"], message.text.strip())
    await state.clear()
    await message.answer("✅ Yangilandi!", reply_markup=ADMIN_KEYBOARD)


# ─── 🗑 Video o'chirish ───────────────────────────────────────────────────────

@router.message(F.text == "🗑 Video o'chirish")
async def start_delete_video(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    if not db.get_all_videos():
        await message.answer("📭 Bazada video mavjud emas.")
        return
    await state.set_state(DeleteVideoState.select_video)
    await message.answer("🗑 Qaysi videoni o'chirmoqchisiz?", reply_markup=videos_inline("delvid"))


@router.callback_query(DeleteVideoState.select_video, F.data.startswith("delvid:"))
async def delete_video_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    vid_id = int(callback.data.split(":")[1])
    vid = db.get_video_by_id(vid_id)
    await state.clear()
    await callback.message.edit_text(
        f"⚠️ <b>{vid['title']}</b> o'chirilsinmi?",
        reply_markup=confirm_delete_video_inline(vid_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delvidconfirm:"))
async def delete_video_confirmed(callback: CallbackQuery) -> None:
    vid_id = int(callback.data.split(":")[1])
    vid = db.get_video_by_id(vid_id)
    name = vid["title"] if vid else "Video"
    db.delete_video(vid_id)
    await callback.message.edit_text(f"🗑 <b>{name}</b> o'chirildi.", parse_mode="HTML")
    await callback.answer("O'chirildi!")


# ─── 📝 Post qo'shish ─────────────────────────────────────────────────────────

@router.message(F.text == "📝 Post qo'shish")
async def start_add_post(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AddPostState.waiting_title)
    await message.answer("📝 Post sarlavhasini kiriting:\n\n/cancel — bekor qilish")


@router.message(AddPostState.waiting_title, F.text)
async def add_post_title_in(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await state.set_state(AddPostState.waiting_content)
    await message.answer("📄 Post matnini kiriting  |  /skip — o'tkazish")


@router.message(AddPostState.waiting_content, F.text)
async def add_post_content_in(message: Message, state: FSMContext) -> None:
    await state.update_data(
        content=None if message.text.strip() == "/skip" else message.text.strip()
    )
    await state.set_state(AddPostState.waiting_photo)
    await message.answer("🖼 Rasm yuboring  |  /skip — o'tkazish")


@router.message(AddPostState.waiting_photo, F.photo)
async def add_post_photo_in(message: Message, state: FSMContext) -> None:
    await state.update_data(photo_file_id=message.photo[-1].file_id)
    await _finish_add_post(message, state)


@router.message(AddPostState.waiting_photo, F.text)
async def add_post_photo_skip(message: Message, state: FSMContext) -> None:
    await state.update_data(photo_file_id=None)
    await _finish_add_post(message, state)


async def _finish_add_post(message: Message, state: FSMContext) -> None:
    d = await state.get_data()
    db.add_post(d["title"], d.get("content"), d.get("photo_file_id"))
    await state.clear()
    await message.answer(f"✅ <b>{d['title']}</b> post saqlandi!", parse_mode="HTML", reply_markup=ADMIN_KEYBOARD)


# ─── ✏️ Post tahrirlash ───────────────────────────────────────────────────────

@router.message(F.text == "✏️ Post tahrirlash")
async def start_edit_post(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    if not db.get_all_posts():
        await message.answer("📭 Bazada post mavjud emas.")
        return
    await state.set_state(EditPostState.select_post)
    await message.answer("✏️ Qaysi postni tahrirlaysiz?", reply_markup=posts_inline("editpost"))


@router.callback_query(EditPostState.select_post, F.data.startswith("editpost:"))
async def edit_post_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    post_id = int(callback.data.split(":")[1])
    post = db.get_post_by_id(post_id)
    await state.update_data(post_id=post_id)
    await state.set_state(EditPostState.select_field)
    await callback.message.edit_text(
        f"✏️ <b>{post['title']}</b> — nimani o'zgartirish kerak?",
        reply_markup=post_edit_fields_inline(post_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(EditPostState.select_field, F.data.startswith("ptf:"))
async def edit_post_field_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    _, post_id, field = callback.data.split(":")
    await state.update_data(post_id=int(post_id), field=field)
    await state.set_state(EditPostState.waiting_value)
    if field == "photo_file_id":
        await callback.message.edit_text("🖼 Yangi rasmni yuboring:")
    elif field == "title":
        await callback.message.edit_text("📝 Yangi sarlavhani kiriting:")
    else:
        await callback.message.edit_text("📄 Yangi matnni kiriting:")
    await callback.answer()


@router.message(EditPostState.waiting_value, F.photo)
async def edit_post_photo_in(message: Message, state: FSMContext) -> None:
    d = await state.get_data()
    db.update_post_field(d["post_id"], "photo_file_id", message.photo[-1].file_id)
    await state.clear()
    await message.answer("✅ Rasm yangilandi!", reply_markup=ADMIN_KEYBOARD)


@router.message(EditPostState.waiting_value, F.text)
async def edit_post_text_in(message: Message, state: FSMContext) -> None:
    d = await state.get_data()
    db.update_post_field(d["post_id"], d["field"], message.text.strip())
    await state.clear()
    await message.answer("✅ Yangilandi!", reply_markup=ADMIN_KEYBOARD)


# ─── 🗑 Post o'chirish ────────────────────────────────────────────────────────

@router.message(F.text == "🗑 Post o'chirish")
async def start_delete_post(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    if not db.get_all_posts():
        await message.answer("📭 Bazada post mavjud emas.")
        return
    await state.set_state(DeletePostState.select_post)
    await message.answer("🗑 Qaysi postni o'chirmoqchisiz?", reply_markup=posts_inline("delpost"))


@router.callback_query(DeletePostState.select_post, F.data.startswith("delpost:"))
async def delete_post_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    post_id = int(callback.data.split(":")[1])
    post = db.get_post_by_id(post_id)
    await state.clear()
    await callback.message.edit_text(
        f"⚠️ <b>{post['title']}</b> o'chirilsinmi?",
        reply_markup=confirm_delete_post_inline(post_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delpostconfirm:"))
async def delete_post_confirmed(callback: CallbackQuery) -> None:
    post_id = int(callback.data.split(":")[1])
    post = db.get_post_by_id(post_id)
    name = post["title"] if post else "Post"
    db.delete_post(post_id)
    await callback.message.edit_text(f"🗑 <b>{name}</b> o'chirildi.", parse_mode="HTML")
    await callback.answer("O'chirildi!")
