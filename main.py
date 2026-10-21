import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

import config
import database
from handlers import client, barber

# Windows konsolida emojilar xatosiz chiqishi uchun UTF-8 o'rnatish
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("culture_barber_bot")


async def set_bot_commands(bot: Bot):
    """
    Telegram bot buyruqlar menyusini o'rnatish
    """
    commands = [
        BotCommand(command="start", description="💈 Bosh menyu / Bron qilish"),
        BotCommand(command="barber", description="✂️ Master kabineti (Usta hisobini ulash)"),
        BotCommand(command="bronlar", description="📋 Kunlik jadval (Masterlar uchun)"),
    ]
    await bot.set_my_commands(commands)


async def main():
    logger.info("=" * 50)
    logger.info("💈 Culture Barbershop Telegram boti ishga tushirilmoqda...")
    logger.info(f"Bot Username: @{config.BOT_USERNAME}")
    logger.info("=" * 50)

    # 1. PostgreSQL bazasini ishga tushirish
    try:
        await database.init_db(config.DATABASE_URL)
    except Exception as e:
        logger.critical(f"❌ Ma'lumotlar bazasiga ulanishda jiddiy xatolik: {e}")
        return

    # 2. Bot va Dispatcher obyektlarini yaratish
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # 3. Routerlarni ro'yxatdan o'tkazish
    dp.include_router(client.router)
    dp.include_router(barber.router)

    # 4. Bot buyruqlarini o'rnatish
    await set_bot_commands(bot)

    # 5. Eski to'planib qolgan yangilanishlarni tozalash (Drop pending updates)
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("🚀 Bot to'liq tayyor va yangilanishlarni qabul qilishni boshladi!")
    
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Bot to'xtatilmoqda...")
        await database.close_db()
        await bot.session.close()
        logger.info("Bot to'liq to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot qo'lda to'xtatildi.")
