import logging
from datetime import datetime
from typing import Any
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database
import keyboards as kb

logger = logging.getLogger(__name__)

router = Router()


class BookingState(StatesGroup):
    waiting_for_phone = State()


# ================== /START VA ASOSIY MENYU ==================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    /start buyrug'i: Mijozni bazaga saqlash va toifalarni ko'rsatish
    """
    await state.clear()
    user = message.from_user
    full_name = f"{user.first_name} {user.last_name or ''}".strip()
    username = user.username

    # Mijozni bazaga yozish yoki yangilash
    await database.add_or_get_client(
        telegram_id=user.id,
        full_name=full_name,
        username=username
    )

    text = (
        f"💈 <b>\"Culture Barbershop\"ga xush kelibsiz, {user.first_name}!</b>\n\n"
        "Bizda professional masterlar, zamonaviy uslub va a'lo darajadagi servis kutmoqda.\n\n"
        "O'zingizga ma'qul kelgan <b>master toifasini</b> tanlang va qulay vaqtga bron qiling:"
    )
    await message.answer(text, reply_markup=kb.main_categories_kb(), parse_mode="HTML")


@router.callback_query(F.data == "nav_categories")
async def cb_nav_categories(callback: CallbackQuery, state: FSMContext):
    """
    Asosiy toifalar menyusiga qaytish
    """
    await state.clear()
    text = (
        "💈 <b>Culture Barbershop</b> — Master toifasini tanlang:\n\n"
        "⭐️ <b>PRO Masterlar</b> — Tajribali va sifatli xizmat ko'rsatuvchi mutaxassislar\n"
        "🔥 <b>TOP Masterlar</b> — Yuqori darajadagi tajribaga ega yetakchi ustalar\n"
        "👑 <b>VIP Masterlar</b> — Premial uslub, eksklyuziv parvarish va art-direktorlar"
    )
    await callback.message.edit_text(text, reply_markup=kb.main_categories_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "about_us")
async def cb_about_us(callback: CallbackQuery):
    """
    Barbershop haqida ma'lumot
    """
    text = (
        "💈 <b>\"Culture Barbershop\" haqida:</b>\n\n"
        "📍 <b>Manzil:</b> Toshkent shahri, Amir Temur shoh ko'chasi, 45-uy\n"
        "⏰ <b>Ish vaqti:</b> Har kuni 10:00 dan 21:00 gacha\n"
        "📞 <b>Aloqa:</b> +998 (71) 200-00-00\n"
        "📷 <b>Instagram:</b> @culturebarbershop\n\n"
        "Siz uchun bepul qahva, choy, qulay kutish zali va eng yaxshi atmosfera!"
    )
    await callback.message.edit_text(text, reply_markup=kb.main_categories_kb(), parse_mode="HTML")
    await callback.answer()


# ================== MASTERLAR VA XIZMATLAR ==================

@router.callback_query(F.data.startswith("cat_"))
async def cb_select_category(callback: CallbackQuery):
    """
    Toifa tanlanganda tegishli masterlarni chiqarish
    """
    category = callback.data.split("_")[1]
    barbers = await database.get_barbers_by_category(category)

    if not barbers:
        await callback.answer(f"Hozircha {category} toifasida usta topilmadi.", show_alert=True)
        return

    cat_title = {"PRO": "⭐️ PRO", "TOP": "🔥 TOP", "VIP": "👑 VIP"}.get(category, category)
    text = (
        f"💈 <b>{cat_title} toifasidagi masterlarimiz:</b>\n\n"
        "O'zingizga yoqqan master ustiga bosing:"
    )
    await callback.message.edit_text(text, reply_markup=kb.barbers_kb(barbers, category), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("barber_"))
async def cb_select_barber(callback: CallbackQuery):
    """
    Master tanlanganda xizmatlar va narxlarni chiqarish
    """
    barber_id = int(callback.data.split("_")[1])
    barber = await database.get_barber_by_id(barber_id)
    if not barber:
        await callback.answer("Master topilmadi.", show_alert=True)
        return

    services = await database.get_all_services()
    if not services:
        await callback.answer("Hozircha xizmatlar ro'yxati mavjud emas.", show_alert=True)
        return

    text = (
        f"💈 <b>Master:</b> {barber['name']} (<i>{barber['category']}</i>)\n\n"
        "Kerakli <b>xizmat turini</b> tanlang:"
    )
    await callback.message.edit_text(
        text,
        reply_markup=kb.services_kb(services, barber),
        parse_mode="HTML"
    )
    await callback.answer()


# ================== SANA VA VAQTNI TANLASH ==================

@router.callback_query(F.data.startswith("srv_"))
async def cb_select_service(callback: CallbackQuery):
    """
    Xizmat tanlanganda sanalar ro'yxatini chiqarish
    """
    parts = callback.data.split("_")
    barber_id = int(parts[1])
    service_id = int(parts[2])

    barber = await database.get_barber_by_id(barber_id)
    service = await database.get_service_by_id(service_id)

    if not barber or not service:
        await callback.answer("Ma'lumot topilmadi.", show_alert=True)
        return

    price = database.calculate_service_price(service, barber["category"])
    formatted_price = f"{price:,}".replace(",", " ")

    text = (
        f"💈 <b>Master:</b> {barber['name']}\n"
        f"✂️ <b>Xizmat:</b> {service['name']}\n"
        f"💰 <b>Narxi:</b> {formatted_price} so'm\n\n"
        "📅 <b>Qaysi sanaga yozilmoqchisiz?</b> Tanlang:"
    )
    await callback.message.edit_text(
        text,
        reply_markup=kb.dates_kb(barber_id, service_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("date_"))
async def cb_select_date(callback: CallbackQuery):
    """
    Sana tanlanganda bo'sh va band vaqtlarni chiqarish
    """
    parts = callback.data.split("_")
    barber_id = int(parts[1])
    service_id = int(parts[2])
    date_str = parts[3]
    booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    barber = await database.get_barber_by_id(barber_id)
    service = await database.get_service_by_id(service_id)

    # Band vaqtlarni bazadan olish
    booked_times = await database.get_booked_times(barber_id, booking_date)

    text = (
        f"💈 <b>Master:</b> {barber['name']}\n"
        f"✂️ <b>Xizmat:</b> {service['name']}\n"
        f"📅 <b>Sana:</b> {date_str}\n\n"
        "⏰ <b>Qulay vaqtni tanlang:</b>\n"
        "🟢 — Bo'sh vaqt\n"
        "❌ — Band qilingan vaqt"
    )
    await callback.message.edit_text(
        text,
        reply_markup=kb.times_kb(barber_id, service_id, date_str, booked_times),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "slot_is_booked")
async def cb_slot_booked(callback: CallbackQuery):
    """
    Band qilingan vaqt bosilganda xabar berish va bosishni bloklash
    """
    await callback.answer(
        "❌ Bu vaqt allaqachon band qilingan!\nIltimos, yashil 🟢 belgilangan bo'sh vaqtlardan birini tanlang.",
        show_alert=True
    )


# ================== BRONNI TASDIQLASH VA TELEFON ==================

@router.callback_query(F.data.startswith("time_"))
async def cb_select_time(callback: CallbackQuery, state: FSMContext):
    """
    Bo'sh vaqt tanlanganda telefon raqamini tekshirish va tasdiqlash sahifasini ko'rsatish
    """
    parts = callback.data.split("_")
    barber_id = int(parts[1])
    service_id = int(parts[2])
    date_str = parts[3]
    time_str = parts[4]

    # Mijoz telefon raqamini tekshirish
    client = await database.get_client_by_telegram_id(callback.from_user.id)
    if not client or not client["phone_number"]:
        # Telefon raqami yo'q bo'lsa, uni so'raymiz
        await state.set_state(BookingState.waiting_for_phone)
        await state.update_data(
            barber_id=barber_id,
            service_id=service_id,
            date_str=date_str,
            time_str=time_str
        )
        await callback.message.delete()
        await callback.message.answer(
            "📱 <b>Bronni yakunlash uchun telefon raqamingizni yuboring:</b>\n\n"
            "Pastdagi tugmani bosing yoki raqamingizni yozib yuboring (Masalan: +998901234567):",
            reply_markup=kb.phone_request_kb(),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    # Telefon bor bo'lsa to'g'ridan-to'g'ri tasdiqlashni ko'rsatamiz
    await show_confirmation(
        message=callback.message,
        client=client,
        barber_id=barber_id,
        service_id=service_id,
        date_str=date_str,
        time_str=time_str,
        is_edit=True
    )
    await callback.answer()


@router.message(BookingState.waiting_for_phone, F.contact)
@router.message(BookingState.waiting_for_phone, F.text)
async def process_phone(message: Message, state: FSMContext):
    """
    Telefon raqami qabul qilinganda
    """
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "Bron bekor qilindi.",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer("Bosh menyu:", reply_markup=kb.main_categories_kb())
        return

    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith("+"):
            phone = f"+{phone}"
    else:
        phone = message.text.strip()
        # Oddiy tekshiruv
        if len(phone) < 7:
            await message.answer("⚠️ Iltimos, to'g'ri telefon raqam kiriting (masalan: +998901234567):")
            return

    # Bazada telefonni yangilaymiz
    await database.update_client_phone(message.from_user.id, phone)
    data = await state.get_data()
    await state.clear()

    await message.answer(
        "✅ Telefon raqamingiz muvaffaqiyatli saqlandi!",
        reply_markup=ReplyKeyboardRemove()
    )

    client = await database.get_client_by_telegram_id(message.from_user.id)
    await show_confirmation(
        message=message,
        client=client,
        barber_id=data["barber_id"],
        service_id=data["service_id"],
        date_str=data["date_str"],
        time_str=data["time_str"],
        is_edit=False
    )


async def show_confirmation(
    message: Message,
    client: Any,
    barber_id: int,
    service_id: int,
    date_str: str,
    time_str: str,
    is_edit: bool = False
):
    """
    Bron haqida xulosa va tasdiqlash tugmasi
    """
    barber = await database.get_barber_by_id(barber_id)
    service = await database.get_service_by_id(service_id)
    price = database.calculate_service_price(service, barber["category"])
    formatted_price = f"{price:,}".replace(",", " ")

    summary_text = (
        "📋 <b>BRON MA'LUMOTLARI:</b>\n\n"
        f"💈 <b>Master:</b> {barber['name']} (<i>{barber['category']}</i>)\n"
        f"✂️ <b>Xizmat:</b> {service['name']}\n"
        f"💰 <b>Narxi:</b> {formatted_price} so'm\n"
        f"📅 <b>Sana:</b> {date_str}\n"
        f"⏰ <b>Vaqt:</b> {time_str}\n"
        f"👤 <b>Mijoz:</b> {client['full_name']}\n"
        f"📞 <b>Telefon:</b> {client['phone_number']}\n\n"
        "Ma'lumotlar to'g'rimi? <b>Tasdiqlash</b> tugmasini bosing:"
    )
    markup = kb.confirm_booking_kb(barber_id, service_id, date_str, time_str)

    if is_edit:
        await message.edit_text(summary_text, reply_markup=markup, parse_mode="HTML")
    else:
        await message.answer(summary_text, reply_markup=markup, parse_mode="HTML")


@router.callback_query(F.data.startswith("cnf_"))
async def cb_confirm_booking(callback: CallbackQuery, bot: Bot):
    """
    Mijoz bronni tasdiqlaganda: appointments jadvaliga yozish va masterga xabar yuborish
    """
    parts = callback.data.split("_")
    barber_id = int(parts[1])
    service_id = int(parts[2])
    date_str = parts[3]
    time_str = parts[4]
    booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    client = await database.get_client_by_telegram_id(callback.from_user.id)
    if not client:
        await callback.answer("Xatolik: Mijoz topilmadi.", show_alert=True)
        return

    # Bazaga yozish
    appointment_id = await database.create_appointment(
        client_db_id=client["id"],
        barber_id=barber_id,
        service_id=service_id,
        appointment_date=booking_date,
        appointment_time_str=time_str
    )

    if not appointment_id:
        await callback.answer(
            "⚠️ Kechirasiz, ushbu vaqt hozirgina boshqa mijoz tomonidan band qilindi. Iltimos, boshqa vaqtni tanlang.",
            show_alert=True
        )
        return

    barber = await database.get_barber_by_id(barber_id)
    service = await database.get_service_by_id(service_id)
    price = database.calculate_service_price(service, barber["category"])
    formatted_price = f"{price:,}".replace(",", " ")

    # Mijozga muvaffaqiyat xabari
    success_text = (
        f"✅ <b>Broningiz qabul qilindi! (#{appointment_id})</b>\n\n"
        f"💈 <b>Master:</b> {barber['name']}\n"
        f"✂️ <b>Xizmat:</b> {service['name']}\n"
        f"💰 <b>Narxi:</b> {formatted_price} so'm\n"
        f"📅 <b>Sana:</b> {date_str}\n"
        f"⏰ <b>Vaqt:</b> {time_str}\n\n"
        "⏳ <i>Arizangiz ustaga yuborildi. Usta tasdiqlashi bilan sizga xabar beramiz!</i>"
    )
    await callback.message.edit_text(success_text, parse_mode="HTML")
    await callback.answer("✅ Bron muvaffaqiyatli yaratildi!", show_alert=False)

    # MASTERGA XABAR YUBORISH (telegram_id orqali)
    if barber["telegram_id"] and barber["telegram_id"] > 10:
        try:
            barber_msg = (
                f"🔔 <b>YANGI BRON! (#{appointment_id})</b>\n\n"
                f"👤 <b>Mijoz:</b> {client['full_name']} (@{client['username'] or 'mavjud_emas'})\n"
                f"📞 <b>Telefon:</b> {client['phone_number'] or 'kiritilmagan'}\n"
                f"✂️ <b>Xizmat:</b> {service['name']}\n"
                f"💰 <b>Narxi:</b> {formatted_price} so'm\n"
                f"📅 <b>Sana:</b> {date_str}\n"
                f"⏰ <b>Vaqt:</b> {time_str}\n\n"
                "Bronni qabul qilasizmi?"
            )
            await bot.send_message(
                chat_id=barber["telegram_id"],
                text=barber_msg,
                reply_markup=kb.barber_decision_kb(appointment_id),
                parse_mode="HTML"
            )
            logger.info(f"Yangi bron #{appointment_id} haqida master {barber['name']} ga xabar yuborildi.")
        except Exception as e:
            logger.error(f"Master {barber['name']} ga xabar yuborishda xatolik: {e}")
    else:
        logger.warning(f"Master {barber['name']} hali o'z Telegram akkauntini bog'lamagan (telegram_id={barber['telegram_id']}).")


@router.callback_query(F.data == "cancel_booking")
async def cb_cancel_booking(callback: CallbackQuery):
    """
    Bron qilishni bekor qilish
    """
    await callback.message.edit_text(
        "❌ Bron qilish bekor qilindi.\n\nBosh menyuga qaytish uchun: /start",
        parse_mode="HTML"
    )
    await callback.answer()


# ================== MIJOZ BRONLARI ==================

@router.callback_query(F.data == "my_bookings")
async def cb_my_bookings(callback: CallbackQuery):
    """
    Mijozning faol bronlarini ko'rsatish
    """
    bookings = await database.get_client_upcoming_appointments(callback.from_user.id)
    if not bookings:
        await callback.answer("Sizda hali kelgusi faol bronlar mavjud emas.", show_alert=True)
        return

    text = "📋 <b>Sizning faol bronlaringiz:</b>\nBatafsil ko'rish yoki bekor qilish uchun bosing:\n"
    await callback.message.edit_text(
        text,
        reply_markup=kb.client_bookings_kb(bookings),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("details_booking_"))
async def cb_details_booking(callback: CallbackQuery):
    """
    Bitta bron tafsiloti
    """
    app_id = int(callback.data.split("_")[2])
    data = await database.get_appointment_with_details(app_id)
    if not data:
        await callback.answer("Bron topilmadi.", show_alert=True)
        return

    status_uz = {
        "pending": "⏳ Kutilmoqda (ustaning tasdiqlashi)",
        "confirmed": "✅ Tasdiqlangan",
        "cancelled": "❌ Bekor qilingan"
    }.get(data["status"], data["status"])

    price_str = f"{data['price']:,}".replace(",", " ")
    text = (
        f"📋 <b>Bron #{data['id']} tafsilotlari:</b>\n\n"
        f"💈 <b>Master:</b> {data['barber_name']} (<i>{data['barber_category']}</i>)\n"
        f"✂️ <b>Xizmat:</b> {data['service_name']}\n"
        f"💰 <b>Narxi:</b> {price_str} so'm\n"
        f"📅 <b>Sana:</b> {data['appointment_date']}\n"
        f"⏰ <b>Vaqt:</b> {data['appointment_time']}\n"
        f"📌 <b>Holati:</b> {status_uz}\n"
    )
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Ushbu bronni bekor qilish", callback_data=f"user_cancel_{app_id}")],
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="my_bookings")]
    ])
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("user_cancel_"))
async def cb_user_cancel(callback: CallbackQuery, bot: Bot):
    """
    Mijoz o'z bronini bekor qilishi
    """
    app_id = int(callback.data.split("_")[2])
    data = await database.get_appointment_with_details(app_id)
    success = await database.cancel_appointment_by_client(app_id, callback.from_user.id)

    if success:
        await callback.message.edit_text(
            f"❌ #{app_id}-sonli broningiz bekor qilindi.\n\nYangi bron qilish uchun: /start",
            parse_mode="HTML"
        )
        await callback.answer("Bron bekor qilindi.", show_alert=False)

        # Agar ustaga telegram_id ulangan bo'lsa, ustaga ham xabar beramiz
        if data and data.get("barber_telegram_id") and data["barber_telegram_id"] > 10:
            try:
                await bot.send_message(
                    chat_id=data["barber_telegram_id"],
                    text=(
                        f"⚠️ <b>Mijoz bronni bekor qildi:</b>\n"
                        f"Bron #{app_id} | {data['appointment_date']} {data['appointment_time']}\n"
                        f"Mijoz: {data['client_name']}"
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                pass
    else:
        await callback.answer("Bronni bekor qilib bo'lmadi.", show_alert=True)
