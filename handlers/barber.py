import logging
from datetime import date, datetime, timedelta
from typing import Any
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

import database
import keyboards as kb

logger = logging.getLogger(__name__)

router = Router()


# ================== /BARBER BUYRUG'I ==================

@router.message(Command("barber"))
async def cmd_barber(message: Message):
    """
    /barber buyrug'i: Usta o'z Telegram akkauntini bazadagi usta bilan bog'laydi
    """
    user_id = message.from_user.id
    current_barber = await database.get_barber_by_telegram_id(user_id)

    if current_barber:
        text = (
            f"💈 <b>Siz allaqachon usta sifatida ulangansiz!</b>\n\n"
            f"👤 <b>Ism:</b> {current_barber['name']}\n"
            f"⭐️ <b>Toifa:</b> {current_barber['category']}\n\n"
            "Kunlik qabullaringizni ko'rish uchun /bronlar buyrug'idan foydalaning."
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Bugungi bronlar", callback_data=f"view_day_{date.today().strftime('%Y-%m-%d')}")],
            [InlineKeyboardButton(text="🔓 Akkauntni uzish (Chiqish)", callback_data="unlink_barber")]
        ])
        await message.answer(text, reply_markup=markup, parse_mode="HTML")
        return

    # Usta hali ulanmagan bo'lsa ro'yxatni ko'rsatamiz
    all_barbers = await database.get_all_barbers()
    text = (
        "💈 <b>Master kabinetiga xush kelibsiz!</b>\n\n"
        "O'z Telegram akkauntingizni tizimdagi profilingiz bilan bog'lash uchun "
        "quyidagi ro'yxatdan o'z ismingizni tanlang:\n\n"
        "<i>(Akkaunt ulangandan so'ng, yangi bronlar haqidagi xabarlar to'g'ridan-to'g'ri sizga keladi)</i>"
    )
    await message.answer(text, reply_markup=kb.barber_claim_kb(all_barbers), parse_mode="HTML")


@router.callback_query(F.data.startswith("claim_barber_"))
async def cb_claim_barber(callback: CallbackQuery):
    """
    Master o'z ismini tanlab akkauntni bog'laganda
    """
    barber_id = int(callback.data.split("_")[2])
    barber = await database.get_barber_by_id(barber_id)

    if not barber:
        await callback.answer("Master topilmadi.", show_alert=True)
        return

    success = await database.link_barber(barber_id, callback.from_user.id)
    if success:
        text = (
            f"🎉 <b>Muvaffaqiyatli ulandingiz!</b>\n\n"
            f"Siz endi tizimda <b>{barber['name']}</b> ({barber['category']}) sifatida qayd etildingiz.\n\n"
            "🔔 Mijozlar sizga yozilganda, tasdiqlash uchun xabarnomalar shu yerga yuboriladi.\n"
            "📅 Kunlik jadvalingizni ko'rish uchun: /bronlar"
        )
        await callback.message.edit_text(text, parse_mode="HTML")
        await callback.answer("Ulanish muvaffaqiyatli!", show_alert=False)
    else:
        await callback.answer("Bog'lashda xatolik yuz berdi.", show_alert=True)


@router.callback_query(F.data == "unlink_barber")
async def cb_unlink_barber(callback: CallbackQuery):
    """
    Masterni tizimdan uzish
    """
    await database.unlink_barber(callback.from_user.id)
    await callback.message.edit_text(
        "🔓 Akkauntingiz usta profilidan uzildi.\n\nQayta ulanish uchun: /barber",
        parse_mode="HTML"
    )
    await callback.answer("Akkaunt uzildi.")


@router.callback_query(F.data == "cancel_master_action")
async def cb_cancel_master(callback: CallbackQuery):
    """
    Master amalini bekor qilish
    """
    await callback.message.delete()
    await callback.answer("Bekor qilindi.")


# ================== /BRONLAR BUYRUG'I ==================

@router.message(Command("bronlar"))
async def cmd_bronlar(message: Message):
    """
    /bronlar buyrug'i: Masterning bugungi va yaqin kunlik jadvali
    """
    user_id = message.from_user.id
    barber = await database.get_barber_by_telegram_id(user_id)

    if not barber:
        await message.answer(
            "⚠️ Siz usta sifatida ro'yxatdan o'tmagansiz.\n\n"
            "Akkauntingizni bog'lash uchun /barber buyrug'ini bosing.",
            parse_mode="HTML"
        )
        return

    today = date.today()
    await send_barber_schedule(message, barber, today)


@router.callback_query(F.data.startswith("view_day_"))
async def cb_view_day(callback: CallbackQuery):
    """
    Kun bo'yicha jadvalni almashtirish
    """
    date_str = callback.data.split("_")[2]
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    barber = await database.get_barber_by_telegram_id(callback.from_user.id)
    if not barber:
        await callback.answer("Siz usta emassiz.", show_alert=True)
        return

    await send_barber_schedule(callback.message, barber, target_date, is_edit=True)
    await callback.answer()


async def send_barber_schedule(
    message: Message,
    barber: Any,
    target_date: date,
    is_edit: bool = False
):
    """
    Master jadvalini chiroyli matn sifatida chiqarish
    """
    appointments = await database.get_barber_appointments_for_date(barber["id"], target_date)
    day_label = "Bugungi" if target_date == date.today() else f"{target_date.strftime('%Y-%m-%d')}"

    header = (
        f"📋 <b>{day_label} kunlik jadval ({target_date.strftime('%Y-%m-%d')}):</b>\n"
        f"💈 <b>Master:</b> {barber['name']} (<i>{barber['category']}</i>)\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    if not appointments:
        body = "<i>Ushbu kunga hali bronlar mavjud emas.</i>\n\n"
    else:
        body = ""
        for i, app in enumerate(appointments, 1):
            status_icon = "✅" if app["status"] == "confirmed" else ("⏳" if app["status"] == "pending" else "❌")
            status_name = "Tasdiqlangan" if app["status"] == "confirmed" else ("Kutilmoqda" if app["status"] == "pending" else "Bekor qilingan")
            price_formatted = f"{app['price']:,}".replace(",", " ")
            username_part = f" (@{app['client_username']})" if app["client_username"] else ""

            body += (
                f"<b>{i}. ⏰ {app['appointment_time']}</b> — {status_icon} {status_name}\n"
                f"   👤 <b>Mijoz:</b> {app['client_name']}{username_part}\n"
                f"   📞 <b>Tel:</b> {app['client_phone'] or 'Kiritilmagan'}\n"
                f"   ✂️ <b>Xizmat:</b> {app['service_name']} ({price_formatted} so'm)\n\n"
            )

    full_text = header + body
    markup = kb.barber_schedule_nav_kb(target_date)

    if is_edit:
        await message.edit_text(full_text, reply_markup=markup, parse_mode="HTML")
    else:
        await message.answer(full_text, reply_markup=markup, parse_mode="HTML")


# ================== MASTER BRONNI TASDIQLASH / BEKOR QILISH ==================

@router.callback_query(F.data.startswith("m_accept_"))
async def cb_master_accept(callback: CallbackQuery, bot: Bot):
    """
    Master bronni tasdiqlaganda
    """
    app_id = int(callback.data.split("_")[2])
    data = await database.get_appointment_with_details(app_id)

    if not data:
        await callback.answer("Bron topilmadi.", show_alert=True)
        return

    # Statusni confirmed ga o'zgartiramiz
    await database.update_appointment_status(app_id, "confirmed")

    # Masterning xabarini yangilaymiz
    price_str = f"{data['price']:,}".replace(",", " ")
    updated_text = (
        f"✅ <b>BRON TASDIQLANDI! (#{app_id})</b>\n\n"
        f"👤 <b>Mijoz:</b> {data['client_name']}\n"
        f"📞 <b>Tel:</b> {data['client_phone']}\n"
        f"✂️ <b>Xizmat:</b> {data['service_name']} ({price_str} so'm)\n"
        f"📅 <b>Sana:</b> {data['appointment_date']}\n"
        f"⏰ <b>Vaqt:</b> {data['appointment_time']}\n\n"
        "<i>Mijozga tasdiq xabarnomasi yuborildi.</i>"
    )
    await callback.message.edit_text(updated_text, parse_mode="HTML")
    await callback.answer("✅ Bron tasdiqlandi!")

    # MIJOZGA TASDIQ BILDIRISHNOMASINI YUBORISH
    try:
        client_msg = (
            f"🎉 <b>Hurmatli {data['client_name']}!</b>\n\n"
            f"Sizning <b>#{app_id}-sonli broningiz</b> master tomonidan <b>TASDIQLANDI</b>! ✅\n\n"
            f"💈 <b>Master:</b> {data['barber_name']} (<i>{data['barber_category']}</i>)\n"
            f"✂️ <b>Xizmat:</b> {data['service_name']}\n"
            f"💰 <b>Narxi:</b> {price_str} so'm\n"
            f"📅 <b>Sana:</b> {data['appointment_date']}\n"
            f"⏰ <b>Vaqt:</b> {data['appointment_time']}\n"
            f"📍 <b>Manzil:</b> Culture Barbershop, Amir Temur shoh ko'chasi 45\n\n"
            "Sizni kutamiz! Iltimos, belgilangan vaqtdan 5-10 daqiqa oldinroq tashrif buyuring."
        )
        await bot.send_message(
            chat_id=data["client_telegram_id"],
            text=client_msg,
            parse_mode="HTML"
        )
        logger.info(f"Mijoz {data['client_name']} ga tasdiq xabari yuborildi.")
    except Exception as e:
        logger.error(f"Mijozga xabar yuborishda xatolik: {e}")


@router.callback_query(F.data.startswith("m_reject_"))
async def cb_master_reject(callback: CallbackQuery, bot: Bot):
    """
    Master bronni bekor qilganda
    """
    app_id = int(callback.data.split("_")[2])
    data = await database.get_appointment_with_details(app_id)

    if not data:
        await callback.answer("Bron topilmadi.", show_alert=True)
        return

    # Statusni cancelled ga o'zgartiramiz
    await database.update_appointment_status(app_id, "cancelled")

    # Masterning xabarini yangilaymiz
    updated_text = (
        f"❌ <b>BRON BEKOR QILINDI (#{app_id})</b>\n\n"
        f"👤 <b>Mijoz:</b> {data['client_name']}\n"
        f"📅 <b>Sana:</b> {data['appointment_date']} {data['appointment_time']}\n\n"
        "<i>Mijozga bekor qilinganligi haqida xabar yuborildi. Ushbu vaqt sloti yana bo'shatildi.</i>"
    )
    await callback.message.edit_text(updated_text, parse_mode="HTML")
    await callback.answer("❌ Bron bekor qilindi.")

    # MIJOZGA BEKOR XABARINI YUBORISH
    try:
        client_msg = (
            f"😔 <b>Hurmatli {data['client_name']}!</b>\n\n"
            f"Afsuski, master siz tanlagan vaqtdagi (<b>#{app_id}-sonli</b>) bronni qabul qila olmadi va uni bekor qildi.\n\n"
            f"💈 <b>Master:</b> {data['barber_name']}\n"
            f"📅 <b>Sana:</b> {data['appointment_date']} {data['appointment_time']}\n\n"
            "Siz boshqa qulay vaqtni yoki boshqa masterimizni tanlashingiz mumkin:\n"
            "Qayta bron qilish: /start"
        )
        await bot.send_message(
            chat_id=data["client_telegram_id"],
            text=client_msg,
            parse_mode="HTML"
        )
        logger.info(f"Mijoz {data['client_name']} ga bekor xabari yuborildi.")
    except Exception as e:
        logger.error(f"Mijozga xabar yuborishda xatolik: {e}")
