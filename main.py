import asyncio
import logging
import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from aiogram import Dispatcher

import config
import database
import services
from api.routes import router as api_router
from bots.client_bot import router as client_router
from bots.staff_bot import router as staff_router

# ================== LOGGING SOZLAMALARI ==================
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s : %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("culture_main")


# ================== FASTAPI ILOVASI ==================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ma'lumotlar bazasini initsializatsiya qilish
    logger.info("Ma'lumotlar bazasi initsializatsiyasi boshlandi...")
    await database.init_db(config.DATABASE_URL)
    logger.info("Baza tayyor.")
    yield
    # Shutdown
    logger.info("Server to'xtatilmoqda...")

app = FastAPI(
    title="Culture Barbershop API & WebApp",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statik fayllar (CSS, JS, Rasmlar)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
WEBSITE_DIR = os.path.join(BASE_DIR, "website")

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
if os.path.exists(WEBSITE_DIR):
    app.mount("/site", StaticFiles(directory=WEBSITE_DIR, html=True), name="site")

# API marshrutlari
app.include_router(api_router)


# Asosiy sahifa - Telegram Web App (To'liq bron qilish ilovasi)
@app.get("/")
async def serve_webapp():
    index_path = os.path.join(WEB_DIR, "index.html")
    return FileResponse(index_path)


# Standalone Booking Web App (/booking va /app)
@app.get("/booking")
@app.get("/app")
async def serve_standalone_booking():
    booking_path = os.path.join(WEB_DIR, "booking.html")
    return FileResponse(booking_path)


# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Culture Barbershop Multi-Bot & WebApp"}


# ================== ASOSIY ASINXRON FUNKSIYA ==================

async def run_client_bot(dp: Dispatcher, bot):
    try:
        logger.info(f"Mijoz boti (@{config.CLIENT_BOT_USERNAME}) polling boshlandi...")
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    except asyncio.CancelledError:
        logger.info("Mijoz boti to'xtatildi.")
    except Exception as e:
        logger.error(f"Mijoz botida xatolik: {e}")


async def run_staff_bot(dp: Dispatcher, bot):
    try:
        logger.info(f"Xodimlar boti (@{config.STAFF_BOT_USERNAME}) polling boshlandi...")
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    except asyncio.CancelledError:
        logger.info("Xodimlar boti to'xtatildi.")
    except Exception as e:
        logger.error(f"Xodimlar botida xatolik: {e}")


async def run_web_server():
    server_config = uvicorn.Config(
        app=app,
        host=config.HOST,
        port=config.PORT,
        log_level="info",
        access_log=False
    )
    server = uvicorn.Server(server_config)
    logger.info(f"Web server ishga tushmoqda: http://{config.HOST}:{config.PORT}")
    await server.serve()


async def main():
    logger.info("=" * 60)
    logger.info("💈 CULTURE BARBERSHOP MULTI-BOT & WEBAPP ISHGA TUSHMOQDA...")
    logger.info(f"💈 Client Bot: @{config.CLIENT_BOT_USERNAME}")
    logger.info(f"💈 Staff Bot:  @{config.STAFF_BOT_USERNAME}")
    logger.info(f"💈 Web App:    {config.WEBAPP_URL}")
    logger.info("=" * 60)

    # 1. Baza ulanishini tekshirish
    await database.init_db(config.DATABASE_URL)

    # 2. Botlarni olish
    c_bot = services.get_client_bot()
    s_bot = services.get_staff_bot()

    # 3. Dispatcherlarni sozlash
    client_dp = Dispatcher()
    client_dp.include_router(client_router)

    staff_dp = Dispatcher()
    staff_dp.include_router(staff_router)

    # 4. Eski kutilayotgan update'larni tozalash (drop pending updates)
    try:
        await c_bot.delete_webhook(drop_pending_updates=True)
        await s_bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"Webhook tozalashda ogohlantirish: {e}")

    # 5. Hammasini bir vaqtda ishga tushirish (Web Server + Client Bot + Staff Bot)
    try:
        await asyncio.gather(
            run_web_server(),
            run_client_bot(client_dp, c_bot),
            run_staff_bot(staff_dp, s_bot)
        )
    finally:
        logger.info("Resurslar tozalanmoqda...")
        await c_bot.session.close()
        await s_bot.session.close()
        pool = await database.get_pool()
        await pool.close()
        logger.info("Barcha xizmatlar to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Tizim foydalanuvchi tomonidan to'xtatildi.")
