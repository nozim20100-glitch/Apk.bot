import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database import init_db
import admin
import apk_list
import video_list
import post_list
import start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ─── Ping server (UptimeRobot uchun) ─────────────────────────────────────────

async def health(request):
    return web.Response(text="Bot ishlayapti ✅")

async def run_web_server():
    port = int(os.environ.get("PORT", 3000))
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web server port {port} da ishga tushdi.")


# ─── Asosiy bot ───────────────────────────────────────────────────────────────

async def main() -> None:
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN muhit o'zgaruvchisi topilmadi!")

    init_db()
    logger.info("Ma'lumotlar bazasi tayyor.")

    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Tartib muhim: admin → apk_list → video_list → post_list → start
    dp.include_router(admin.router)
    dp.include_router(apk_list.router)
    dp.include_router(video_list.router)
    dp.include_router(post_list.router)
    dp.include_router(start.router)

    # Web server va botni parallel ishga tushirish
    await run_web_server()

    logger.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
