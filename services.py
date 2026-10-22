import logging
from typing import Optional, Dict, Any
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
import database

logger = logging.getLogger(__name__)

# Bot instansiyalari
client_bot: Optional[Bot] = None
staff_bot: Optional[Bot] = None


def get_client_bot() -> Bot:
    global client_bot
    if client_bot is None:
        client_bot = Bot(
            token=config.CLIENT_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    return client_bot


def get_staff_bot() -> Bot:
    global staff_bot
    if staff_bot is None:
        staff_bot = Bot(
            token=config.STAFF_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    return staff_bot


async def notify_barber_new_booking(appointment_id: int) -> bool:
    """
    Yangi bron qilinganda tegishli ustaga @culturestaffbot orqali xabar va tasdiqlash tugmalarini yuboradi.
    """
    app = await database.get_appointment_by_id(appointment_id)
    if not app:
        logger.error(f"Bron topilmadi: {appointment_id}")
        return False

    barber_tg_id = app.get('barber_telegram_id')
    if not barber_tg_id:
        logger.warning(f"Usta {app.get('barber_name')} hali @culturestaffbot da Telegram ID ga ega emas!")
        return False

    # Xizmatlar ro'yxati matni
    services_text = app.get('service_name') or "Standart xizmat"
    if app.get('service_ids'):
        srv_list = await database.get_services_by_ids(app['service_ids'])
        if srv_list:
            services_text = ", ".join(s['name'] for s in srv_list)

    points_used = app.get('points_used') or 0
    discount_amount = app.get('discount_amount') or 0
    total_price_formatted = f"{app['total_price']:,}".replace(",", " ")
    if discount_amount > 0:
        original_price = app['total_price'] + discount_amount
        orig_formatted = f"{original_price:,}".replace(",", " ")
        disc_formatted = f"{discount_amount:,}".replace(",", " ")
        price_display = f"<b>{total_price_formatted} UZS</b> (Asl narx: {orig_formatted} UZS | ⭐ Chegirma: -{disc_formatted} UZS)"
    else:
        price_display = f"<b>{total_price_formatted} UZS</b>"

    date_str = app['appointment_date'].strftime("%d.%m.%Y")
    time_str = app['appointment_time'].strftime("%H:%M")

    client_name = app.get('client_name') or "Nomalum"
    client_phone = app.get('client_phone') or "Kiritilmagan"
    client_username = f"@{app['client_username']}" if app.get('client_username') else "Mavjud emas"

    text = (
        f"🔔 <b>YANGI BRON BUYURTMASI! #BRON-{app['id']}</b>\n\n"
        f"🗓 <b>Sana:</b> {date_str}\n"
        f"⏰ <b>Vaqt:</b> {time_str}\n"
        f"✂️ <b>Xizmat:</b> {services_text}\n"
        f"💰 <b>To'lov:</b> {price_display}\n\n"
        f"👤 <b>Mijoz:</b> {client_name}\n"
        f"📞 <b>Telefon:</b> {client_phone}\n"
        f"💬 <b>Telegram:</b> {client_username}\n\n"
        f"<b>Holat:</b> ⏳ Kutilmoqda\n\n"
        f"Iltimos, buyurtmani qabul qiling yoki rad eting:"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"staff_accept_{app['id']}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"staff_reject_{app['id']}")
        ]
    ])

    try:
        s_bot = get_staff_bot()
        await s_bot.send_message(chat_id=barber_tg_id, text=text, reply_markup=kb)
        logger.info(f"Bron #{appointment_id} bo'yicha ustaga ({barber_tg_id}) xabar muvaffaqiyatli bordi.")
        return True
    except Exception as e:
        logger.error(f"Ustaga (@culturestaffbot) xabar yuborishda xatolik: {e}")
        return False


async def notify_client_new_booking(appointment_id: int) -> bool:
    """
    Mijozga bron qilinganligi va tasdiqlanishi kutilayotgani haqida @culturebarbersbot orqali xabar yuboradi.
    """
    app = await database.get_appointment_by_id(appointment_id)
    if not app or not app.get('client_telegram_id'):
        return False

    services_text = app.get('service_name') or "Standart xizmat"
    if app.get('service_ids'):
        srv_list = await database.get_services_by_ids(app['service_ids'])
        if srv_list:
            services_text = ", ".join(s['name'] for s in srv_list)

    points_used = app.get('points_used') or 0
    discount_amount = app.get('discount_amount') or 0
    total_price_formatted = f"{app['total_price']:,}".replace(",", " ")
    if discount_amount > 0:
        original_price = app['total_price'] + discount_amount
        orig_formatted = f"{original_price:,}".replace(",", " ")
        disc_formatted = f"{discount_amount:,}".replace(",", " ")
        price_display = f"<b>{total_price_formatted} UZS</b> (Asl narx: {orig_formatted} UZS | ⭐ Chegirma: -{disc_formatted} UZS)"
    else:
        price_display = f"<b>{total_price_formatted} UZS</b>"

    date_str = app['appointment_date'].strftime("%d.%m.%Y")
    time_str = app['appointment_time'].strftime("%H:%M")

    text = (
        f"⏳ <b>Bron buyurtmangiz qabul qilindi! #BRON-{app['id']}</b>\n\n"
        f"💈 <b>Usta:</b> {app.get('barber_name')} ({app.get('barber_category')})\n"
        f"🗓 <b>Sana:</b> {date_str}\n"
        f"⏰ <b>Vaqt:</b> {time_str}\n"
        f"✂️ <b>Xizmat:</b> {services_text}\n"
        f"💰 <b>To'lov:</b> {price_display}\n\n"
        f"<i>Usta buyurtmangizni ko'rib chiqmoqda. Tasdiqlanishi bilan sizga xabar beramiz.</i>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Mening bronlarim", callback_data="client_my_bookings")]
    ])

    try:
        c_bot = get_client_bot()
        await c_bot.send_message(chat_id=app['client_telegram_id'], text=text, reply_markup=kb)
        return True
    except Exception as e:
        logger.error(f"Mijozga (@culturebarbersbot) xabar yuborishda xatolik: {e}")
        return False


async def notify_client_booking_confirmed(appointment_id: int) -> bool:
    """
    Usta qabul qilganda mijozga @culturebarbersbot orqali tasdiqlash xabari yuboradi.
    """
    app = await database.get_appointment_by_id(appointment_id)
    if not app or not app.get('client_telegram_id'):
        return False

    services_text = app.get('service_name') or "Standart xizmat"
    if app.get('service_ids'):
        srv_list = await database.get_services_by_ids(app['service_ids'])
        if srv_list:
            services_text = ", ".join(s['name'] for s in srv_list)

    date_str = app['appointment_date'].strftime("%d.%m.%Y")
    time_str = app['appointment_time'].strftime("%H:%M")
    
    points_used = app.get('points_used') or 0
    discount_amount = app.get('discount_amount') or 0
    total_price_formatted = f"{app['total_price']:,}".replace(",", " ")
    if discount_amount > 0:
        original_price = app['total_price'] + discount_amount
        orig_formatted = f"{original_price:,}".replace(",", " ")
        disc_formatted = f"{discount_amount:,}".replace(",", " ")
        price_display = f"<b>{total_price_formatted} UZS</b> (Asl narx: {orig_formatted} UZS | ⭐ Chegirma: -{disc_formatted} UZS)"
    else:
        price_display = f"<b>{total_price_formatted} UZS</b>"

    text = (
        f"🎉 <b>BRONINGIZ TASDIQLANDI! #BRON-{app['id']}</b>\n\n"
        f"💈 <b>Sartarosh:</b> {app.get('barber_name')} ({app.get('barber_category')})\n"
        f"🗓 <b>Sana:</b> {date_str}\n"
        f"⏰ <b>Vaqt:</b> {time_str}\n"
        f"✂️ <b>Xizmat:</b> {services_text}\n"
        f"💰 <b>To'lov summasi:</b> {price_display}\n"
        f"📍 <b>Manzil:</b> {config.SHOP_ADDRESS}\n\n"
        f"Sizni belgilangan vaqtda kutamiz! Iltimos, o'z vaqtida kelishingizni so'raymiz."
    )

    try:
        c_bot = get_client_bot()
        await c_bot.send_message(chat_id=app['client_telegram_id'], text=text)
        return True
    except Exception as e:
        logger.error(f"Mijozga tasdiq xabarini yuborishda xatolik: {e}")
        return False


async def notify_client_cashback_earned(appointment_id: int) -> bool:
    """
    Xizmat ko'rsatilgach, mijozga keshbek berilganligi haqida @culturebarbersbot orqali xabar yuboradi.
    """
    app = await database.get_appointment_by_id(appointment_id)
    if not app or not app.get('client_telegram_id'):
        return False

    client_tg_id = app['client_telegram_id']
    profile = await database.get_loyalty_profile(client_tg_id)
    points_earned = int((app['total_price'] or 0) * 0.05)
    current_points = profile.get('points', 0) if profile else 0

    points_str = f"{points_earned:,}".replace(",", " ")
    balance_str = f"{current_points:,}".replace(",", " ")

    text = (
        f"⭐️ <b>KESHBEK VA BALLAR TAQDIM ETILDI! #BRON-{app['id']}</b>\n\n"
        f"Culture Barbershop ga tashrifingiz uchun rahmat!\n"
        f"Ushbu tashrif uchun hisobingizga <b>+{points_str} ball</b> (5% keshbek) o'tkazildi.\n\n"
        f"💳 <b>Sizning balansingiz:</b> <code>{balance_str}</code> ball\n"
        f"🎖 <b>Darajangiz:</b> {profile.get('tier_name', 'Member')}\n\n"
        f"<i>💡 To'plangan ballarni keyingi safar to'lovda ishlatishingiz (1 ball = 1 UZS chegirma) "
        f"yoki maxsus sovg'alarga (soch voski, soqol moyi, yuz spa) almashtirishingiz mumkin!</i>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Sodiqlik klubi & Sovg'alar", callback_data="client_loyalty_view")]
    ])

    try:
        c_bot = get_client_bot()
        await c_bot.send_message(chat_id=client_tg_id, text=text, reply_markup=kb)
        return True
    except Exception as e:
        logger.error(f"Mijozga keshbek xabari yuborishda xatolik: {e}")
        return False


async def notify_client_booking_cancelled(appointment_id: int, reason: Optional[str] = None) -> bool:
    """
    Usta rad etganda mijozga xabar berish.
    """
    app = await database.get_appointment_by_id(appointment_id)
    if not app or not app.get('client_telegram_id'):
        return False

    date_str = app['appointment_date'].strftime("%d.%m.%Y")
    time_str = app['appointment_time'].strftime("%H:%M")
    reason_str = reason or "Usta ushbu vaqtda band yoki jadvalda o'zgarish"

    text = (
        f"⚠️ <b>BRON BEKOR QILINDI #BRON-{app['id']}</b>\n\n"
        f"Afsuski, usta {app.get('barber_name')} {date_str} {time_str} vaqtiga bo'lgan bronni qabul qila olmadi.\n"
        f"<i>Sabab: {reason_str}</i>\n\n"
        f"Iltimos, boshqa vaqt yoki boshqa ustani tanlang."
    )

    try:
        c_bot = get_client_bot()
        await c_bot.send_message(chat_id=app['client_telegram_id'], text=text)
        return True
    except Exception as e:
        logger.error(f"Mijozga bekor qilinganlik xabarini yuborishda xatolik: {e}")
        return False


async def notify_barber_client_cancelled(appointment_id: int) -> bool:
    """
    Mijoz o'z bronini bekor qilganda ustaga @culturestaffbot orqali xabar yuborish.
    """
    app = await database.get_appointment_by_id(appointment_id)
    if not app or not app.get('barber_telegram_id'):
        return False

    date_str = app['appointment_date'].strftime("%d.%m.%Y")
    time_str = app['appointment_time'].strftime("%H:%M")
    client_name = app.get('client_name') or "Mijoz"

    text = (
        f"ℹ️ <b>DIQQAT: #BRON-{app['id']} mijoz tomonidan bekor qilindi.</b>\n\n"
        f"🗓 <b>Sana:</b> {date_str}\n"
        f"⏰ <b>Vaqt:</b> {time_str}\n"
        f"👤 <b>Mijoz:</b> {client_name}\n\n"
        f"Ushbu vaqt oraligi qaytadan boshadi."
    )

    try:
        s_bot = get_staff_bot()
        await s_bot.send_message(chat_id=app['barber_telegram_id'], text=text)
        return True
    except Exception as e:
        logger.error(f"Ustaga bekor qilish haqida xabar yuborishda xatolik: {e}")
        return False
