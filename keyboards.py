from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import database as db

ADMIN_ID = 8639222385


def main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="📱 APKlar"),   KeyboardButton(text="🎬 Videolar")],
        [KeyboardButton(text="📝 Yozuvlar")],
    ]
    if user_id == ADMIN_ID:
        rows.append([KeyboardButton(text="⚙️ Admin panel")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def apks_reply_keyboard() -> ReplyKeyboardMarkup:
    """APK nomlarini 2 ustunli reply keyboard sifatida qaytaradi."""
    apks = db.get_all_apks()
    rows = []
    row = []
    for apk in apks:
        row.append(KeyboardButton(text=apk["name"]))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([KeyboardButton(text="🔙 Orqaga")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def videos_reply_keyboard() -> ReplyKeyboardMarkup:
    """Video sarlavhalarini 2 ustunli reply keyboard sifatida qaytaradi."""
    videos = db.get_all_videos()
    rows = []
    row = []
    for v in videos:
        row.append(KeyboardButton(text=v["title"]))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([KeyboardButton(text="🔙 Orqaga")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def posts_reply_keyboard() -> ReplyKeyboardMarkup:
    """Post sarlavhalarini 2 ustunli reply keyboard sifatida qaytaradi."""
    posts = db.get_all_posts()
    rows = []
    row = []
    for p in posts:
        row.append(KeyboardButton(text=p["title"]))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([KeyboardButton(text="🔙 Orqaga")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


ADMIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        # APK bo'limi
        [KeyboardButton(text="➕ APK qo'shish"),    KeyboardButton(text="✏️ APK tahrirlash")],
        [KeyboardButton(text="🗑 APK o'chirish"),   KeyboardButton(text="📂 Kategoriya yaratish")],
        # Video bo'limi
        [KeyboardButton(text="🎬 Video qo'shish"),  KeyboardButton(text="✏️ Video tahrirlash")],
        [KeyboardButton(text="🗑 Video o'chirish")],
        # Post bo'limi
        [KeyboardButton(text="📝 Post qo'shish"),   KeyboardButton(text="✏️ Post tahrirlash")],
        [KeyboardButton(text="🗑 Post o'chirish")],
        # Orqaga
        [KeyboardButton(text="🔙 Orqaga")],
    ],
    resize_keyboard=True,
)


# ─── APK inline ───────────────────────────────────────────────────────────────

def categories_inline(prefix: str = "cat") -> InlineKeyboardMarkup:
    cats = db.get_all_categories()
    buttons = [
        [InlineKeyboardButton(text=c["name"], callback_data=f"{prefix}:{c['id']}")]
        for c in cats
    ]
    buttons.append([InlineKeyboardButton(text="❌ Bekor", callback_data="ap:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def apks_inline(prefix: str) -> InlineKeyboardMarkup:
    apks = db.get_all_apks()
    buttons = [
        [InlineKeyboardButton(
            text=f"{a['name']}" + (f"  [{a['category_name']}]" if a['category_name'] else ""),
            callback_data=f"{prefix}:{a['id']}"
        )]
        for a in apks
    ]
    buttons.append([InlineKeyboardButton(text="❌ Bekor", callback_data="ap:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def apk_edit_fields_inline(apk_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Nom",        callback_data=f"ef:{apk_id}:name"),
            InlineKeyboardButton(text="📄 Tavsif",     callback_data=f"ef:{apk_id}:description"),
        ],
        [
            InlineKeyboardButton(text="🎥 Video",      callback_data=f"ef:{apk_id}:video_file_id"),
            InlineKeyboardButton(text="📦 APK fayl",   callback_data=f"ef:{apk_id}:file_id"),
        ],
        [
            InlineKeyboardButton(text="📂 Kategoriya", callback_data=f"ef:{apk_id}:category_id"),
            InlineKeyboardButton(text="❌ Bekor",       callback_data="ap:cancel"),
        ],
    ])


def confirm_delete_inline(apk_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ha, o'chir", callback_data=f"delconfirm:{apk_id}"),
        InlineKeyboardButton(text="❌ Yo'q",       callback_data="ap:cancel"),
    ]])


# ─── Video inline ─────────────────────────────────────────────────────────────

def videos_inline(prefix: str) -> InlineKeyboardMarkup:
    videos = db.get_all_videos()
    buttons = [
        [InlineKeyboardButton(text=v["title"], callback_data=f"{prefix}:{v['id']}")]
        for v in videos
    ]
    buttons.append([InlineKeyboardButton(text="❌ Bekor", callback_data="ap:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def video_edit_fields_inline(vid_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Sarlavha",  callback_data=f"vf:{vid_id}:title"),
            InlineKeyboardButton(text="📄 Tavsif",    callback_data=f"vf:{vid_id}:description"),
        ],
        [
            InlineKeyboardButton(text="🎬 Video fayl", callback_data=f"vf:{vid_id}:file_id"),
            InlineKeyboardButton(text="❌ Bekor",       callback_data="ap:cancel"),
        ],
    ])


def confirm_delete_video_inline(vid_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ha, o'chir", callback_data=f"delvidconfirm:{vid_id}"),
        InlineKeyboardButton(text="❌ Yo'q",       callback_data="ap:cancel"),
    ]])


# ─── Post inline ──────────────────────────────────────────────────────────────

def posts_inline(prefix: str) -> InlineKeyboardMarkup:
    posts = db.get_all_posts()
    buttons = [
        [InlineKeyboardButton(text=p["title"], callback_data=f"{prefix}:{p['id']}")]
        for p in posts
    ]
    buttons.append([InlineKeyboardButton(text="❌ Bekor", callback_data="ap:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def post_edit_fields_inline(post_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Sarlavha", callback_data=f"ptf:{post_id}:title"),
            InlineKeyboardButton(text="📄 Matn",     callback_data=f"ptf:{post_id}:content"),
        ],
        [
            InlineKeyboardButton(text="🖼 Rasm",     callback_data=f"ptf:{post_id}:photo_file_id"),
            InlineKeyboardButton(text="❌ Bekor",    callback_data="ap:cancel"),
        ],
    ])


def confirm_delete_post_inline(post_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ha, o'chir", callback_data=f"delpostconfirm:{post_id}"),
        InlineKeyboardButton(text="❌ Yo'q",       callback_data="ap:cancel"),
    ]])
