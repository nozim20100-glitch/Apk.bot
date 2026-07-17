"""
Database layer — SQLite (local/Replit) yoki PostgreSQL (Railway) ni avtomatik tanlaydi.
DATABASE_URL muhit o'zgaruvchisi bo'lsa PostgreSQL, bo'lmasa SQLite ishlatiladi.
"""
import os
import sqlite3
from typing import Optional

DATABASE_URL = os.environ.get("DATABASE_URL", "")

# ─── Adapter: har ikki DB uchun bir xil interfeys ─────────────────────────────

if DATABASE_URL:
    print("POSTGRESQL ISHLAYAPTI")

    import psycopg2
    import psycopg2.extras
    import psycopg2.errors

    def get_connection():
        return psycopg2.connect(DATABASE_URL)

    def _cursor(conn):
        return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    PH = "%s"
    IS_PG = True

else:
    print("SQLITE ISHLAYAPTI")

    def get_connection():
        conn = sqlite3.connect(
            os.path.join(os.path.dirname(__file__), "apks.db")
        )
        conn.row_factory = sqlite3.Row
        return conn

    def _cursor(conn):
        return conn.cursor()

    PH = "?"
    IS_PG = False


# ─── DB boshlash ──────────────────────────────────────────────────────────────

def init_db() -> None:
    with get_connection() as conn:
        cur = _cursor(conn)

        if IS_PG:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id         SERIAL PRIMARY KEY,
                    name       TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS apks (
                    id            SERIAL PRIMARY KEY,
                    name          TEXT NOT NULL UNIQUE,
                    file_id       TEXT NOT NULL,
                    category_id   INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                    description   TEXT,
                    video_file_id TEXT,
                    added_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id          SERIAL PRIMARY KEY,
                    title       TEXT NOT NULL,
                    file_id     TEXT NOT NULL,
                    description TEXT,
                    added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id            SERIAL PRIMARY KEY,
                    title         TEXT NOT NULL,
                    content       TEXT,
                    photo_file_id TEXT,
                    added_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    name       TEXT NOT NULL UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS apks (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    name          TEXT NOT NULL UNIQUE,
                    file_id       TEXT NOT NULL,
                    category_id   INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                    description   TEXT,
                    video_file_id TEXT,
                    added_at      DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    title       TEXT NOT NULL,
                    file_id     TEXT NOT NULL,
                    description TEXT,
                    added_at    DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    title         TEXT NOT NULL,
                    content       TEXT,
                    photo_file_id TEXT,
                    added_at      DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            _migrate_sqlite(conn)
            return

        conn.commit()


def _migrate_sqlite(conn) -> None:
    """SQLite uchun ustun qo'shish (eski DB larda)."""
    cur = conn.cursor()
    existing_apks = {row[1] for row in cur.execute("PRAGMA table_info(apks)").fetchall()}
    for col, defn in [
        ("category_id", "INTEGER REFERENCES categories(id) ON DELETE SET NULL"),
        ("description",   "TEXT"),
        ("video_file_id", "TEXT"),
    ]:
        if col not in existing_apks:
            cur.execute(f"ALTER TABLE apks ADD COLUMN {col} {defn}")

    existing_videos = {row[1] for row in cur.execute("PRAGMA table_info(videos)").fetchall()}
    if "description" not in existing_videos:
        cur.execute("ALTER TABLE videos ADD COLUMN description TEXT")

    conn.commit()


# ─── Yordamchi: qator dict ga aylantirish ────────────────────────────────────

def _row(row) -> Optional[dict]:
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    return dict(row)


def _rows(rows) -> list[dict]:
    return [_row(r) for r in rows]


# ─── Kategoriyalar ────────────────────────────────────────────────────────────

def add_category(name: str) -> bool:
    try:
        with get_connection() as conn:
            cur = _cursor(conn)
            cur.execute(f"INSERT INTO categories (name) VALUES ({PH})", (name,))
            conn.commit()
        return True
    except Exception as e:
        err = str(e).lower()
        if "unique" in err or "duplicate" in err:
            return False
        raise


def get_all_categories() -> list[dict]:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute("SELECT id, name FROM categories ORDER BY name")
        return _rows(cur.fetchall())


def get_category_by_id(cat_id: int) -> Optional[dict]:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(f"SELECT id, name FROM categories WHERE id = {PH}", (cat_id,))
        return _row(cur.fetchone())


def delete_category(cat_id: int) -> None:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(f"DELETE FROM categories WHERE id = {PH}", (cat_id,))
        conn.commit()


# ─── APKlar ───────────────────────────────────────────────────────────────────

def add_apk(name: str, file_id: str, category_id: Optional[int] = None,
            description: Optional[str] = None, video_file_id: Optional[str] = None) -> None:
    with get_connection() as conn:
        cur = _cursor(conn)
        if IS_PG:
            cur.execute(f"""
                INSERT INTO apks (name, file_id, category_id, description, video_file_id)
                VALUES ({PH}, {PH}, {PH}, {PH}, {PH})
                ON CONFLICT (name) DO UPDATE SET
                    file_id       = EXCLUDED.file_id,
                    category_id   = EXCLUDED.category_id,
                    description   = EXCLUDED.description,
                    video_file_id = EXCLUDED.video_file_id
            """, (name, file_id, category_id, description, video_file_id))
        else:
            cur.execute(f"""
                INSERT INTO apks (name, file_id, category_id, description, video_file_id)
                VALUES ({PH}, {PH}, {PH}, {PH}, {PH})
                ON CONFLICT(name) DO UPDATE SET
                    file_id       = excluded.file_id,
                    category_id   = excluded.category_id,
                    description   = excluded.description,
                    video_file_id = excluded.video_file_id
            """, (name, file_id, category_id, description, video_file_id))
        conn.commit()


def get_all_apks() -> list[dict]:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(f"""
            SELECT a.id, a.name, a.file_id, a.description, a.video_file_id,
                   a.category_id, c.name AS category_name
            FROM apks a
            LEFT JOIN categories c ON a.category_id = c.id
            ORDER BY a.added_at DESC
        """)
        return _rows(cur.fetchall())


def get_apks_by_category(category_id: int) -> list[dict]:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(f"""
            SELECT a.id, a.name, a.file_id, a.description, a.video_file_id,
                   a.category_id, c.name AS category_name
            FROM apks a
            LEFT JOIN categories c ON a.category_id = c.id
            WHERE a.category_id = {PH}
            ORDER BY a.added_at DESC
        """, (category_id,))
        return _rows(cur.fetchall())


def get_apk_by_id(apk_id: int) -> Optional[dict]:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(f"""
            SELECT a.id, a.name, a.file_id, a.description, a.video_file_id,
                   a.category_id, c.name AS category_name
            FROM apks a
            LEFT JOIN categories c ON a.category_id = c.id
            WHERE a.id = {PH}
        """, (apk_id,))
        return _row(cur.fetchone())


def update_apk_field(apk_id: int, field: str, value) -> None:
    allowed = {"name", "file_id", "category_id", "description", "video_file_id"}
    if field not in allowed:
        raise ValueError(f"Noma'lum maydon: {field}")
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(f"UPDATE apks SET {field} = {PH} WHERE id = {PH}", (value, apk_id))
        conn.commit()


def delete_apk(apk_id: int) -> None:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(f"DELETE FROM apks WHERE id = {PH}", (apk_id,))
        conn.commit()


# ─── Videolar ─────────────────────────────────────────────────────────────────

def add_video(title: str, file_id: str, description: Optional[str] = None) -> None:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(
            f"INSERT INTO videos (title, file_id, description) VALUES ({PH}, {PH}, {PH})",
            (title, file_id, description),
        )
        conn.commit()


def get_all_videos() -> list[dict]:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute("SELECT id, title, file_id, description FROM videos ORDER BY added_at DESC")
        return _rows(cur.fetchall())


def get_video_by_id(vid_id: int) -> Optional[dict]:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(
            f"SELECT id, title, file_id, description FROM videos WHERE id = {PH}", (vid_id,)
        )
        return _row(cur.fetchone())


def update_video_field(vid_id: int, field: str, value) -> None:
    allowed = {"title", "file_id", "description"}
    if field not in allowed:
        raise ValueError(f"Noma'lum maydon: {field}")
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(f"UPDATE videos SET {field} = {PH} WHERE id = {PH}", (value, vid_id))
        conn.commit()


def delete_video(vid_id: int) -> None:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(f"DELETE FROM videos WHERE id = {PH}", (vid_id,))
        conn.commit()


# ─── Yozuvlar (Posts) ─────────────────────────────────────────────────────────

def add_post(title: str, content: Optional[str] = None,
             photo_file_id: Optional[str] = None) -> None:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(
            f"INSERT INTO posts (title, content, photo_file_id) VALUES ({PH}, {PH}, {PH})",
            (title, content, photo_file_id),
        )
        conn.commit()


def get_all_posts() -> list[dict]:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(
            "SELECT id, title, content, photo_file_id FROM posts ORDER BY added_at DESC"
        )
        return _rows(cur.fetchall())


def get_post_by_id(post_id: int) -> Optional[dict]:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(
            f"SELECT id, title, content, photo_file_id FROM posts WHERE id = {PH}", (post_id,)
        )
        return _row(cur.fetchone())


def update_post_field(post_id: int, field: str, value) -> None:
    allowed = {"title", "content", "photo_file_id"}
    if field not in allowed:
        raise ValueError(f"Noma'lum maydon: {field}")
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(f"UPDATE posts SET {field} = {PH} WHERE id = {PH}", (value, post_id))
        conn.commit()


def delete_post(post_id: int) -> None:
    with get_connection() as conn:
        cur = _cursor(conn)
        cur.execute(f"DELETE FROM posts WHERE id = {PH}", (post_id,))
        conn.commit()
