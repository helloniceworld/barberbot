import logging
from datetime import date, datetime, timedelta
from typing import Optional
from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, MenuButtonWebApp, MenuButtonDefault
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import config
import database
import services

logger = logging.getLogger(__name__)

router = Router()


class BookingState(StatesGroup):
    category = State()
    barber = State()
    service = State()
    target_date = State()
    target_time = State()
    phone = State()


def get_client_main_keyboard() -> InlineKeyboardMarkup:
    rows = []
    
    # 1. Web App tugmasi faqat HTTPS bo'lgandagina ishlaydi
    if config.WEBAPP_URL and config.WEBAPP_URL.startswith("https://"):
        rows.append([
            InlineKeyboardButton(
                text="💈 Bron qilish (Web App)",
                web_app=WebAppInfo(url=config.WEBAPP_URL)
            )
        ])

    # 2. Bot ichida to'g'ridan-to'g'ri tezkor bron qilish tugmasi
    rows.append([
        InlineKeyboardButton(text="⚡️ Bot orqali tezkor bron", callback_data="client_start_booking")
    ])

    # 3. Qo'shimcha xizmatlar
    rows.append([
        InlineKeyboardButton(text="📋 Mening bronlarim", callback_data="client_my_bookings"),
        InlineKeyboardButton(text="📍 Manzil & Vaqt", callback_data="client_info_location")
    ])
    rows.append([
        InlineKeyboardButton(text="📞 Bog'lanish", callback_data="client_info_contact")
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


# ================== /START ==================

@router.message(Command("start"))
async def cmd_client_start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    user = message.from_user

    # Mijozni bazaga saqlash
    try:
        await database.get_or_create_client(
            telegram_id=user.id,
            full_name=user.full_name,
            username=user.username
        )
    except Exception as e:
        logger.error(f"Mijozni bazaga saqlashda xato: {e}")

    # Menu buttonni HTTPS bo'lsa sozlash
    try:
        if config.WEBAPP_URL and config.WEBAPP_URL.startswith("https://"):
            await bot.set_chat_menu_button(
                chat_id=message.chat.id,
                menu_button=MenuButtonWebApp(
                    text="💈 Bron qilish",
                    web_app=WebAppInfo(url=config.WEBAPP_URL)
                )
            )
        else:
            await bot.set_chat_menu_button(
                chat_id=message.chat.id,
                menu_button=MenuButtonDefault()
            )
    except Exception as e:
        logger.debug(f"Menu button sozlashda xato (e'tiborsiz): {e}")

    text = (
        f"💈 <b>Culture Barbershop ga xush kelibsiz!</b>\n\n"
        f"Assalomu alaykum, <b>{user.first_name}</b>!\n\n"
        f"Culture Barbershop ning qulay bron qilish xizmatidasiz. "
        f"Sevimli ustangizni, kerakli xizmatlarni va o'zingizga qulay vaqtni "
        f"quyidagi tugmalar orqali tanlang:\n\n"
        f"<i>Yuqori darajadagi xizmat va o'zgacha hashamatli muhit sizni kutmoqda!</i>"
    )

    try:
        await message.answer(text, reply_markup=get_client_main_keyboard())
    except Exception as e:
        logger.error(f"Xabar yuborishda xato: {e}")
        # Agar WebAppInfo xato bersa, oddiy inline keyboard bilan jo'natish
        fallback_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚡️ Bron qilish", callback_data="client_start_booking")],
            [InlineKeyboardButton(text="📋 Mening bronlarim", callback_data="client_my_bookings")]
        ])
        await message.answer(text, reply_markup=fallback_kb)


# ================== BOT ICHIDA INTERAKTIV BRON QILISH ==================

@router.callback_query(F.data == "client_start_booking")
async def cb_start_booking(query: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "<b>1-Qadam:</b> Sartarosh toifasini tanlang:\n\n"
        "✦ <b>PRO Barber:</b> Standart sifat va kundalik uslub (from 75 000 UZS)\n"
        "★ <b>TOP Barber (POPULAR):</b> Yuqori mahorat va zamonaviy uslub (from 95 000 UZS)\n"
        "👑 <b>VIP Barber (SIGNATURE):</b> Eksklyuziv parvarish va spa (from 125 000 UZS)"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✦ PRO Barber", callback_data="c_cat_PRO")],
        [InlineKeyboardButton(text="★ TOP Barber (POPULAR)", callback_data="c_cat_TOP")],
        [InlineKeyboardButton(text="👑 VIP Barber", callback_data="c_cat_VIP")],
        [InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="client_back_home")]
    ])
    await query.message.edit_text(text, reply_markup=kb)
    await query.answer()


@router.callback_query(F.data.startswith("c_cat_"))
async def cb_select_category(query: CallbackQuery, state: FSMContext):
    cat = query.data.split("_")[2]
    await state.update_data(category=cat)

    barbers = await database.get_barbers(category=cat)
    if not barbers:
        await query.answer("Ushbu toifada usta topilmadi, boshqa toifani tanlang.", show_alert=True)
        return

    buttons = []
    for b in barbers:
        buttons.append([InlineKeyboardButton(
            text=f"✂️ {b['name']} (⭐ {b['rating']} • {b['experience_years']} yil)",
            callback_data=f"c_barber_{b['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="client_start_booking")])

    text = f"<b>2-Qadam:</b> <b>{cat}</b> toifasidagi ustani tanlang:"
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await query.answer()


@router.callback_query(F.data.startswith("c_barber_"))
async def cb_select_barber(query: CallbackQuery, state: FSMContext):
    barber_id = int(query.data.split("_")[2])
    barber = await database.get_barber_by_id(barber_id)
    await state.update_data(barber_id=barber_id, barber_name=barber['name'], barber_category=barber['category'])

    services = await database.get_services()
    buttons = []
    cat_col = f"price_{barber['category'].lower()}"

    for s in services:
        price = s.get(cat_col) or s.get("price_pro") or 80000
        p_str = f"{price:,}".replace(",", " ")
        buttons.append([InlineKeyboardButton(
            text=f"💈 {s['name']} — {p_str} UZS",
            callback_data=f"c_srv_{s['id']}_{price}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"c_cat_{barber['category']}")])

    text = f"<b>3-Qadam:</b> Xizmat turini tanlang (Usta: <b>{barber['name']}</b>):"
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await query.answer()


@router.callback_query(F.data.startswith("c_srv_"))
async def cb_select_service(query: CallbackQuery, state: FSMContext):
    parts = query.data.split("_")
    service_id = int(parts[2])
    price = int(parts[3])
    service = await database.get_service_by_id(service_id)

    await state.update_data(service_id=service_id, service_name=service['name'], total_price=price)

    # Sana tanlash: Bugun, Erta, Indinga
    today = date.today()
    d1 = today
    d2 = today + timedelta(days=1)
    d3 = today + timedelta(days=2)

    buttons = [
        [InlineKeyboardButton(text=f"Bugun ({d1.strftime('%d.%m')})", callback_data=f"c_date_{d1.strftime('%Y-%m-%d')}")],
        [InlineKeyboardButton(text=f"Ertaga ({d2.strftime('%d.%m')})", callback_data=f"c_date_{d2.strftime('%Y-%m-%d')}")],
        [InlineKeyboardButton(text=f"Indinga ({d3.strftime('%d.%m')})", callback_data=f"c_date_{d3.strftime('%Y-%m-%d')}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="client_start_booking")]
    ]

    text = "<b>4-Qadam:</b> Qaysi sanaga bron qilmoqchisiz?"
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await query.answer()


@router.callback_query(F.data.startswith("c_date_"))
async def cb_select_date(query: CallbackQuery, state: FSMContext):
    date_str = query.data.split("_")[2]
    await state.update_data(appointment_date=date_str)
    data = await state.get_data()

    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    slots = await database.get_available_slots(data['barber_id'], target_date)

    if not slots:
        await query.answer("Kechirasiz, bu sanada barcha vaqtlar band. Boshqa sanani tanlang.", show_alert=True)
        return

    # Slotlarni 3 tadan qatorda joylash
    buttons = []
    row = []
    for s in slots:
        row.append(InlineKeyboardButton(text=s, callback_data=f"c_time_{s}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"c_barber_{data['barber_id']}")])

    text = f"<b>5-Qadam:</b> Bo'sh vaqt slotini tanlang ({date_str}):"
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await query.answer()


@router.callback_query(F.data.startswith("c_time_"))
async def cb_select_time(query: CallbackQuery, state: FSMContext):
    slot_time = query.data.split("_")[2]
    await state.update_data(appointment_time=slot_time)
    data = await state.get_data()

    p_str = f"{data['total_price']:,}".replace(",", " ")
    text = (
        f"📋 <b>BUYURTMANI TASDIQLASH:</b>\n\n"
        f"💈 <b>Usta:</b> {data['barber_name']} ({data['barber_category']})\n"
        f"✂️ <b>Xizmat:</b> {data['service_name']}\n"
        f"🗓 <b>Sana:</b> {data['appointment_date']}\n"
        f"⏰ <b>Vaqt:</b> {data['appointment_time']}\n"
        f"💰 <b>Jami summa:</b> {p_str} UZS\n\n"
        f"Bron qilishni tasdiqlaysizmi?"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash va bron qilish", callback_data="c_confirm_final")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="client_back_home")]
    ])

    await query.message.edit_text(text, reply_markup=kb)
    await query.answer()


@router.callback_query(F.data == "c_confirm_final")
async def cb_confirm_final(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = query.from_user

    app_date = datetime.strptime(data['appointment_date'], "%Y-%m-%d").date()
    app_time = datetime.strptime(data['appointment_time'], "%H:%M").time()

    # Bo'shligini qayta tekshirish
    is_free = await database.is_slot_available(data['barber_id'], app_date, app_time)
    if not is_free:
        await query.message.edit_text("❌ Kechirasiz, bu vaqt hozirgina boshqa mijoz tomonidan band qilindi. Iltimos, boshqa vaqtni tanlang.")
        await state.clear()
        return

    # Mijozni olish
    client = await database.get_or_create_client(
        telegram_id=user.id,
        full_name=user.full_name,
        username=user.username
    )

    appointment = await database.create_appointment(
        client_id=client['id'],
        barber_id=data['barber_id'],
        service_id=data['service_id'],
        appointment_date=app_date,
        appointment_time=app_time,
        total_price=data['total_price'],
        client_name=user.full_name,
        client_phone=client.get('phone_number') or "Telegram orqali",
        client_username=user.username,
        service_ids=[data['service_id']]
    )

    await state.clear()

    # Ustaga xabar yuborish (@culturestaffbot)
    try:
        await services.notify_barber_new_booking(appointment['id'])
    except Exception as e:
        logger.error(f"Ustaga xabar berishda xato: {e}")

    p_str = f"{data['total_price']:,}".replace(",", " ")
    success_text = (
        f"🎉 <b>Broningiz muvaffaqiyatli qabul qilindi! #BRON-{appointment['id']}</b>\n\n"
        f"💈 Usta: <b>{data['barber_name']}</b> ({data['barber_category']})\n"
        f"🗓 Sana: <b>{data['appointment_date']}</b> | ⏰ <b>{data['appointment_time']}</b>\n"
        f"✂️ Xizmat: {data['service_name']}\n"
        f"💰 Summa: {p_str} UZS\n\n"
        f"<i>Usta buyurtmangizni ko'rib chiqmoqda. Tasdiqlanishi bilan sizga xabar yuboramiz.</i>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Mening bronlarim", callback_data="client_my_bookings")],
        [InlineKeyboardButton(text="⬅️ Bosh sahifa", callback_data="client_back_home")]
    ])

    await query.message.edit_text(success_text, reply_markup=kb)
    await query.answer("Bron qabul qilindi!")


# ================== MENING BRONLARIM ==================

@router.callback_query(F.data == "client_my_bookings")
async def cb_client_my_bookings(query: CallbackQuery):
    user_id = query.from_user.id
    apps = await database.get_client_appointments(user_id)

    if not apps:
        text = (
            "📋 <b>Sizda hali hech qanday faol bron mavjud emas.</b>\n\n"
            "Quyidagi tugma orqali qulay va tez bron qiling!"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚡️ Bron qilish", callback_data="client_start_booking")],
            [InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="client_back_home")]
        ])
        await query.message.edit_text(text, reply_markup=kb)
        await query.answer()
        return

    text = "📋 <b>Sizning barcha bronlaringiz:</b>\n\n"
    buttons = []

    for a in apps[:6]:
        status_map = {
            "pending": ("⏳ Kutilmoqda", True),
            "confirmed": ("✅ Tasdiqlangan", True),
            "completed": ("💈 Bajarilgan", False),
            "cancelled": ("❌ Bekor qilingan", False)
        }
        status_text, can_cancel = status_map.get(a['status'], ("• Noma'lum", False))
        d_str = a['appointment_date'].strftime("%d.%m.%Y")
        t_str = a['appointment_time'].strftime("%H:%M")
        p_str = f"{a['total_price']:,}".replace(",", " ")

        text += (
            f"<b>#BRON-{a['id']}</b> — {status_text}\n"
            f"✂️ Usta: {a.get('barber_name')} ({a.get('barber_category')})\n"
            f"🗓 Sana: {d_str} | ⏰ {t_str}\n"
            f"💰 Summa: {p_str} UZS\n"
            f"────────────────\n"
        )

        if can_cancel:
            buttons.append([InlineKeyboardButton(
                text=f"❌ #BRON-{a['id']} ni bekor qilish",
                callback_data=f"client_cancel_req_{a['id']}"
            )])

    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="client_back_home")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await query.message.edit_text(text, reply_markup=kb)
    await query.answer()


@router.callback_query(F.data.startswith("client_cancel_req_"))
async def cb_client_cancel_req(query: CallbackQuery):
    app_id = int(query.data.split("_")[3])
    text = f"Haqiqatan ham <b>#BRON-{app_id}</b> buyurtmasini bekor qilmoqchimisiz?"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Ha, bekor qilish", callback_data=f"client_cancel_yes_{app_id}"),
            InlineKeyboardButton(text="⬅️ Yo'q, qolsin", callback_data="client_my_bookings")
        ]
    ])
    await query.message.edit_text(text, reply_markup=kb)
    await query.answer()


@router.callback_query(F.data.startswith("client_cancel_yes_"))
async def cb_client_cancel_yes(query: CallbackQuery):
    app_id = int(query.data.split("_")[3])
    await database.update_appointment_status(app_id, "cancelled", "Mijoz tomonidan bekor qilindi")

    # Ustaga bildirishnoma (@culturestaffbot)
    try:
        await services.notify_barber_client_cancelled(app_id)
    except Exception as e:
        logger.error(f"Ustaga bekor qilish haqida xabar berishda xato: {e}")

    text = f"✅ <b>#BRON-{app_id}</b> buyurtmangiz bekor qilindi."
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Barcha bronlarim", callback_data="client_my_bookings")],
        [InlineKeyboardButton(text="⬅️ Bosh sahifa", callback_data="client_back_home")]
    ])
    await query.message.edit_text(text, reply_markup=kb)
    await query.answer("Bron bekor qilindi.")


# ================== MA'LUMOT TUGMALARI ==================

@router.callback_query(F.data == "client_info_location")
async def cb_client_info_location(query: CallbackQuery):
    text = (
        f"📍 <b>Manzil va Ish tartibi</b>\n\n"
        f"💈 <b>Salon:</b> {config.SHOP_NAME}\n"
        f"📍 <b>Manzil:</b> {config.SHOP_ADDRESS}\n"
        f"⏰ <b>Ish vaqti:</b> Har kuni 10:00 dan 22:00 gacha\n"
        f"📞 <b>Telefon:</b> {config.SHOP_PHONE}\n\n"
        f"Lokatsiya xaritada: <a href='{config.SHOP_LOCATION_URL}'>Google Maps</a>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="client_back_home")]
    ])
    await query.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
    await query.answer()


@router.callback_query(F.data == "client_info_contact")
async def cb_client_info_contact(query: CallbackQuery):
    text = (
        f"📞 <b>Aloqa va Qo'llab-quvvatlash</b>\n\n"
        f"Savollar yoki takliflar bo'yicha biz bilan bog'lanishingiz mumkin:\n\n"
        f"☎️ <b>Telefon:</b> {config.SHOP_PHONE}\n"
        f"💬 <b>Administrator:</b> @cultureadmin\n"
        f"💈 <b>Xodimlar boti:</b> @{config.STAFF_BOT_USERNAME}\n\n"
        f"Sizga xizmat ko'rsatishdan mamnunmiz!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="client_back_home")]
    ])
    await query.message.edit_text(text, reply_markup=kb)
    await query.answer()


@router.callback_query(F.data == "client_back_home")
async def cb_client_back_home(query: CallbackQuery):
    user = query.from_user
    text = (
        f"💈 <b>Culture Barbershop</b>\n\n"
        f"Assalomu alaykum, <b>{user.first_name}</b>!\n\n"
        f"Sevimli ustangizni, kerakli xizmatlarni va o'zingizga qulay vaqtni "
        f"quyidagi tugmalar orqali tanlang."
    )
    await query.message.edit_text(text, reply_markup=get_client_main_keyboard())
    await query.answer()
