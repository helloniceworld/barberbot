import logging
from datetime import date, datetime, timedelta
from typing import Optional
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

import database
import services

logger = logging.getLogger(__name__)

router = Router()


def get_staff_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Bugungi navbatlar"), KeyboardButton(text="🗓 Ertangi navbatlar")],
            [KeyboardButton(text="📋 Faol bronlar"), KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="👤 Profilim")]
        ],
        resize_keyboard=True
    )


# ================== /START ==================

@router.message(Command("start"))
async def cmd_staff_start(message: Message):
    user_id = message.from_user.id
    barber = await database.get_barber_by_telegram_id(user_id)

    if barber:
        text = (
            f"💈 <b>Culture Barbershop | Xodimlar Boti</b>\n\n"
            f"Assalomu alaykum, <b>{barber['name']}</b>!\n"
            f"Toifangiz: <b>{barber['category']}</b>\n"
            f"Reyting: <b>⭐ {barber['rating']}</b>\n\n"
            f"Mijozlar @culturebarbersbot orqali bron qilishganda, yangi buyurtmalar to'g'ridan-to'g'ri shu yerga keladi."
        )
        await message.answer(text, reply_markup=get_staff_menu())
    else:
        # Bog'lanmagan ustalar ro'yxati
        unlinked = await database.get_unlinked_barbers()
        text = (
            f"💈 <b>Culture Staff Botiga xush kelibsiz!</b>\n\n"
            f"Sizning Telegram ID: <code>{user_id}</code>\n\n"
            f"Siz hali tizimda usta sifatida ro'yxatdan o'tmagansiz.\n"
            f"Iltimos, pastdagi ro'yxatdan o'z ismingizni tanlang:"
        )

        buttons = []
        for b in unlinked:
            buttons.append([InlineKeyboardButton(
                text=f"✂️ {b['name']} ({b['category']})",
                callback_data=f"staff_claim_{b['id']}"
            )])

        if not buttons:
            text += "\n\n<i>Hozirda bo'sh turgan usta profillari mavjud emas. Admin bilan bog'laning.</i>"
            kb = None
        else:
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(text, reply_markup=kb)


# ================== USTA PROFILINI ULASH ==================

@router.callback_query(F.data.startswith("staff_claim_"))
async def cb_staff_claim(query: CallbackQuery):
    barber_id = int(query.data.split("_")[2])
    user_id = query.from_user.id

    barber = await database.get_barber_by_id(barber_id)
    if not barber:
        await query.answer("Usta topilmadi!", show_alert=True)
        return

    text = (
        f"Tasdiqlash:\n\n"
        f"Haqiqatan ham siz <b>{barber['name']} ({barber['category']})</b> misiz?\n"
        f"Telegram ID'ingiz (<code>{user_id}</code>) ushbu profilga bog'lanadi."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, tasdiqlayman", callback_data=f"staff_confirm_claim_{barber_id}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="staff_cancel_claim")
        ]
    ])
    await query.message.edit_text(text, reply_markup=kb)
    await query.answer()


@router.callback_query(F.data.startswith("staff_confirm_claim_"))
async def cb_staff_confirm_claim(query: CallbackQuery):
    barber_id = int(query.data.split("_")[3])
    user_id = query.from_user.id

    success = await database.link_barber_telegram(barber_id, user_id)
    if success:
        barber = await database.get_barber_by_id(barber_id)
        await query.message.edit_text(
            f"✅ <b>Tabriklaymiz!</b> Siz <b>{barber['name']} ({barber['category']})</b> sifatida muvaffaqiyatli ulandingiz.\n\n"
            f"Endi mijozlar sizga navbat olganida barcha xabarlar shu yerga keladi."
        )
        await query.message.answer("Asosiy menyu:", reply_markup=get_staff_menu())
    else:
        await query.message.edit_text("❌ Profilni ulashda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
    await query.answer()


@router.callback_query(F.data == "staff_cancel_claim")
async def cb_staff_cancel_claim(query: CallbackQuery):
    await query.message.delete()
    await query.answer("Bekor qilindi.")


# ================== BUYURTMALARNI BOSHQARISH (QABUL / RAD ETISH) ==================

@router.callback_query(F.data.startswith("staff_accept_"))
async def cb_staff_accept(query: CallbackQuery):
    app_id = int(query.data.split("_")[2])
    app = await database.get_appointment_by_id(app_id)

    if not app:
        await query.answer("Bron topilmadi!", show_alert=True)
        return

    if app['status'] != 'pending':
        await query.answer(f"Ushbu buyurtma holati allaqachon: {app['status']}", show_alert=True)
        return

    await database.update_appointment_status(app_id, "confirmed")

    # Xizmatlar matni
    services_text = app.get('service_name') or "Standart xizmat"
    if app.get('service_ids'):
        srv_list = await database.get_services_by_ids(app['service_ids'])
        if srv_list:
            services_text = ", ".join(s['name'] for s in srv_list)

    date_str = app['appointment_date'].strftime("%d.%m.%Y")
    time_str = app['appointment_time'].strftime("%H:%M")
    total_price = f"{app['total_price']:,}".replace(",", " ")
    client_name = app.get('client_name') or "Mijoz"
    client_phone = app.get('client_phone') or "Kiritilmagan"

    new_text = (
        f"✅ <b>QABUL QILINDI! #BRON-{app['id']}</b>\n\n"
        f"🗓 <b>Sana:</b> {date_str} | ⏰ <b>Vaqt:</b> {time_str}\n"
        f"👤 <b>Mijoz:</b> {client_name} ({client_phone})\n"
        f"✂️ <b>Xizmat:</b> {services_text}\n"
        f"💰 <b>Summa:</b> {total_price} UZS\n\n"
        f"<i>Mijozga tasdiq xabari yuborildi.</i>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💈 Xizmat ko'rsatildi (Bajarildi)", callback_data=f"staff_done_{app['id']}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"staff_cancel_{app['id']}")
        ]
    ])

    await query.message.edit_text(new_text, reply_markup=kb)
    await query.answer("Buyurtma qabul qilindi!")

    # Mijozga bildirishnoma yuborish
    await services.notify_client_booking_confirmed(app_id)


@router.callback_query(F.data.startswith("staff_reject_"))
async def cb_staff_reject(query: CallbackQuery):
    app_id = int(query.data.split("_")[2])
    app = await database.get_appointment_by_id(app_id)

    if not app:
        await query.answer("Bron topilmadi!", show_alert=True)
        return

    await database.update_appointment_status(app_id, "cancelled", "Usta tomonidan rad etildi")

    date_str = app['appointment_date'].strftime("%d.%m.%Y")
    time_str = app['appointment_time'].strftime("%H:%M")
    client_name = app.get('client_name') or "Mijoz"
    client_phone = app.get('client_phone') or "Kiritilmagan"

    new_text = (
        f"❌ <b>RAD ETILDI #BRON-{app['id']}</b>\n\n"
        f"🗓 <b>Sana:</b> {date_str} | ⏰ <b>Vaqt:</b> {time_str}\n"
        f"👤 <b>Mijoz:</b> {client_name} ({client_phone})\n\n"
        f"<i>Mijozga bekor qilinganlik haqida xabar yuborildi.</i>"
    )

    await query.message.edit_text(new_text, reply_markup=None)
    await query.answer("Buyurtma rad etildi.")

    # Mijozga bildirishnoma
    await services.notify_client_booking_cancelled(app_id)


@router.callback_query(F.data.startswith("staff_done_"))
async def cb_staff_done(query: CallbackQuery):
    app_id = int(query.data.split("_")[2])
    await database.update_appointment_status(app_id, "completed")

    app = await database.get_appointment_by_id(app_id)
    date_str = app['appointment_date'].strftime("%d.%m.%Y")
    time_str = app['appointment_time'].strftime("%H:%M")
    total_price = f"{app['total_price']:,}".replace(",", " ")
    client_name = app.get('client_name') or "Mijoz"

    new_text = (
        f"💈 <b>XIZMAT KO'RSATILDI! (BAJARILDI) #BRON-{app['id']}</b>\n\n"
        f"🗓 <b>Sana:</b> {date_str} | ⏰ <b>Vaqt:</b> {time_str}\n"
        f"👤 <b>Mijoz:</b> {client_name}\n"
        f"💰 <b>Summa:</b> {total_price} UZS\n\n"
        f"<i>Buyurtma muvaffaqiyatli yakunlandi va statistikaga qo'shildi.</i>"
    )

    await query.message.edit_text(new_text, reply_markup=None)
    await query.answer("Xizmat yakunlandi!")

    # Mijozga keshbek berilgani haqida xabarnoma
    try:
        await services.notify_client_cashback_earned(app_id)
    except Exception as e:
        logger.error(f"Keshbek bildirishnomasini yuborishda xatolik: {e}")


@router.callback_query(F.data.startswith("staff_cancel_"))
async def cb_staff_cancel(query: CallbackQuery):
    app_id = int(query.data.split("_")[2])
    await database.update_appointment_status(app_id, "cancelled", "Usta tomonidan bekor qilindi")

    await query.message.edit_text(
        f"❌ <b>Bron #{app_id} bekor qilindi.</b>",
        reply_markup=None
    )
    await query.answer("Bekor qilindi.")
    await services.notify_client_booking_cancelled(app_id, "Usta tomonidan bekor qilindi")


# ================== MATNLI TUGMALAR (NAVBARLAR, STATISTIKA) ==================

@router.message(F.text == "📅 Bugungi navbatlar")
async def msg_today_appointments(message: Message):
    user_id = message.from_user.id
    barber = await database.get_barber_by_telegram_id(user_id)
    if not barber:
        await message.answer("Siz usta sifatida ulanmagansiz. /start buyrug'ini yuboring.")
        return

    today = date.today()
    apps = await database.get_barber_appointments(barber['id'], target_date=today)

    if not apps:
        await message.answer(f"Bugun ({today.strftime('%d.%m.%Y')}) uchun hozircha navbatlar yo'q.")
        return

    text = f"📅 <b>Bugungi navbatlaringiz ({today.strftime('%d.%m.%Y')}):</b>\n\n"
    for a in apps:
        status_emoji = {"pending": "⏳", "confirmed": "✅", "completed": "💈", "cancelled": "❌"}.get(a['status'], "•")
        t_str = a['appointment_time'].strftime("%H:%M")
        p_str = f"{a['total_price']:,}".replace(",", " ")
        c_name = a.get('client_name') or "Mijoz"
        c_phone = a.get('client_phone') or "Tel korsatilmagan"
        s_name = a.get('service_name') or "Xizmat"
        text += (
            f"{status_emoji} <b>{t_str}</b> — {c_name}\n"
            f"   📞 {c_phone}\n"
            f"   ✂️ {s_name} ({p_str} UZS)\n"
            f"   Holat: {a['status'].capitalize()}\n\n"
        )

    await message.answer(text)


@router.message(F.text == "🗓 Ertangi navbatlar")
async def msg_tomorrow_appointments(message: Message):
    user_id = message.from_user.id
    barber = await database.get_barber_by_telegram_id(user_id)
    if not barber:
        await message.answer("Siz usta sifatida ulanmagansiz. /start buyrug'ini yuboring.")
        return

    tomorrow = date.today() + timedelta(days=1)
    apps = await database.get_barber_appointments(barber['id'], target_date=tomorrow)

    if not apps:
        await message.answer(f"Ertaga ({tomorrow.strftime('%d.%m.%Y')}) uchun hozircha navbatlar yo'q.")
        return

    text = f"🗓 <b>Ertangi navbatlaringiz ({tomorrow.strftime('%d.%m.%Y')}):</b>\n\n"
    for a in apps:
        status_emoji = {"pending": "⏳", "confirmed": "✅", "completed": "💈", "cancelled": "❌"}.get(a['status'], "•")
        t_str = a['appointment_time'].strftime("%H:%M")
        p_str = f"{a['total_price']:,}".replace(",", " ")
        c_name = a.get('client_name') or "Mijoz"
        c_phone = a.get('client_phone') or "Tel korsatilmagan"
        s_name = a.get('service_name') or "Xizmat"
        text += (
            f"{status_emoji} <b>{t_str}</b> — {c_name}\n"
            f"   📞 {c_phone}\n"
            f"   ✂️ {s_name} ({p_str} UZS)\n"
            f"   Holat: {a['status'].capitalize()}\n\n"
        )

    await message.answer(text)


@router.message(F.text == "📋 Faol bronlar")
async def msg_active_appointments(message: Message):
    user_id = message.from_user.id
    barber = await database.get_barber_by_telegram_id(user_id)
    if not barber:
        await message.answer("Siz usta sifatida ulanmagansiz.")
        return

    apps = await database.get_barber_appointments(barber['id'])
    today = date.today()
    active_apps = [a for a in apps if a['status'] in ('pending', 'confirmed') and a['appointment_date'] >= today]

    if not active_apps:
        await message.answer("Hozirda kelgusi faol bronlar mavjud emas.")
        return

    text = "📋 <b>Kelgusi faol bronlaringiz:</b>\n\n"
    for a in active_apps:
        status_emoji = "⏳ Kutilmoqda" if a['status'] == 'pending' else "✅ Tasdiqlangan"
        d_str = a['appointment_date'].strftime("%d.%m.%Y")
        t_str = a['appointment_time'].strftime("%H:%M")
        p_str = f"{a['total_price']:,}".replace(",", " ")
        c_name = a.get('client_name') or "Mijoz"
        c_phone = a.get('client_phone') or "Tel korsatilmagan"
        s_name = a.get('service_name') or "Xizmat"
        text += (
            f"🗓 <b>{d_str}</b> | ⏰ <b>{t_str}</b>\n"
            f"👤 {c_name} ({c_phone})\n"
            f"✂️ {s_name} • {p_str} UZS\n"
            f"Holat: {status_emoji}\n"
            f"───────────────\n"
        )

    await message.answer(text)


@router.message(F.text == "📊 Statistika")
async def msg_barber_stats(message: Message):
    user_id = message.from_user.id
    barber = await database.get_barber_by_telegram_id(user_id)
    if not barber:
        await message.answer("Siz usta sifatida ulanmagansiz.")
        return

    stats = await database.get_barber_stats(barber['id'])
    income_str = f"{stats['today_income']:,}".replace(",", " ")

    text = (
        f"📊 <b>Mening Statistikam: {barber['name']}</b>\n\n"
        f"📅 <b>Bugun xizmat ko'rsatilgan:</b> {stats['today_clients']} ta mijoz\n"
        f"💰 <b>Bugungi tushum:</b> {income_str} UZS\n"
        f"⏳ <b>Kutilayotgan faol navbatlar:</b> {stats['pending_count']} ta\n"
        f"🏆 <b>Jami xizmat ko'rsatilgan:</b> {stats['total_completed']} ta mijoz\n"
        f"⭐ <b>Reyting:</b> {barber['rating']} / 5.0"
    )
    await message.answer(text)


@router.message(F.text == "👤 Profilim")
async def msg_barber_profile(message: Message):
    user_id = message.from_user.id
    barber = await database.get_barber_by_telegram_id(user_id)
    if not barber:
        await message.answer("Siz usta sifatida ulanmagansiz.")
        return

    active_status = "🟢 Faol" if barber['is_active'] else "🔴 Nofaol"
    text = (
        f"👤 <b>Usta Profili</b>\n\n"
        f"Ism: <b>{barber['name']}</b>\n"
        f"Toifa: <b>{barber['category']}</b>\n"
        f"Tajriba: <b>{barber['experience_years']} yil</b>\n"
        f"Reyting: <b>⭐ {barber['rating']}</b>\n"
        f"Telegram ID: <code>{barber['telegram_id']}</code>\n"
        f"Holat: <b>{active_status}</b>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Akkauntni uzish (Chiqish)", callback_data=f"staff_unlink_{barber['id']}")]
    ])
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("staff_unlink_"))
async def cb_staff_unlink(query: CallbackQuery):
    barber_id = int(query.data.split("_")[2])
    await database.unlink_barber_telegram(barber_id)
    await query.message.edit_text("Siz usta profilidan uzildingiz. Qayta ulash uchun /start bosing.")
    await query.answer("Profil uzildi.")
