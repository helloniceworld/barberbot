from datetime import date, timedelta
from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import asyncpg
import config
from database import calculate_service_price


def get_uzbek_month(month: int) -> str:
    months = {
        1: "yanvar", 2: "fevral", 3: "mart", 4: "aprel",
        5: "may", 6: "iyun", 7: "iyul", 8: "avgust",
        9: "sentyabr", 10: "oktyabr", 11: "noyabr", 12: "dekabr"
    }
    return months.get(month, "")


def get_uzbek_weekday(weekday: int) -> str:
    weekdays = {
        0: "Dushanba", 1: "Seshanba", 2: "Chorshanba",
        3: "Payshanba", 4: "Juma", 5: "Shanba", 6: "Yakshanba"
    }
    return weekdays.get(weekday, "")


# ================== MIJOZ KEYBOARDS ==================

def main_categories_kb() -> InlineKeyboardMarkup:
    """
    Bosh menyu: Master toifalari (PRO, TOP, VIP)
    """
    buttons = [
        [InlineKeyboardButton(text="⭐️ PRO Masterlar", callback_data="cat_PRO")],
        [InlineKeyboardButton(text="🔥 TOP Masterlar", callback_data="cat_TOP")],
        [InlineKeyboardButton(text="👑 VIP Masterlar", callback_data="cat_VIP")],
        [
            InlineKeyboardButton(text="📋 Mening bronlarim", callback_data="my_bookings"),
            InlineKeyboardButton(text="ℹ️ Biz haqimizda", callback_data="about_us")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def barbers_kb(barbers: List[asyncpg.Record], category: str) -> InlineKeyboardMarkup:
    """
    Toifaga tegishli masterlar ro'yxati
    """
    buttons = []
    for b in barbers:
        exp = b.get("experience_years", 3)
        buttons.append([
            InlineKeyboardButton(
                text=f"💈 {b['name']} ({exp} yil tajriba)",
                callback_data=f"barber_{b['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Toifalarga qaytish", callback_data="nav_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def services_kb(services: List[asyncpg.Record], barber: asyncpg.Record) -> InlineKeyboardMarkup:
    """
    Xizmatlar va narxlar (master toifasiga ko'ra)
    """
    buttons = []
    category = barber["category"]
    for s in services:
        price = calculate_service_price(s, category)
        formatted_price = f"{price:,}".replace(",", " ")
        buttons.append([
            InlineKeyboardButton(
                text=f"✂️ {s['name']} — {formatted_price} so'm",
                callback_data=f"srv_{barber['id']}_{s['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Ustalarga qaytish", callback_data=f"cat_{category}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def dates_kb(barber_id: int, service_id: int) -> InlineKeyboardMarkup:
    """
    Yaqin 5 kunlik sanalar
    """
    buttons = []
    today = date.today()
    for i in range(5):
        target_date = today + timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")
        day_str = f"{target_date.day}-{get_uzbek_month(target_date.month)}"
        if i == 0:
            label = f"Bugun ({day_str})"
        elif i == 1:
            label = f"Ertaga ({day_str})"
        else:
            wday = get_uzbek_weekday(target_date.weekday())
            label = f"{wday} ({day_str})"
        buttons.append([
            InlineKeyboardButton(
                text=f"📅 {label}",
                callback_data=f"date_{barber_id}_{service_id}_{date_str}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Xizmatlarga qaytish", callback_data=f"barber_{barber_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def times_kb(barber_id: int, service_id: int, date_str: str, booked_times: List[str]) -> InlineKeyboardMarkup:
    """
    Vaqtlar menyusi: Bo'sh vaqtlar yashil, band vaqtlar bloklangan (❌ Band).
    """
    buttons = []
    row = []
    for slot in config.WORK_HOURS:
        if slot in booked_times:
            # Band vaqt - bosilganda alert beradi
            btn = InlineKeyboardButton(
                text=f"❌ {slot} (Band)",
                callback_data="slot_is_booked"
            )
        else:
            # Bo'sh vaqt
            btn = InlineKeyboardButton(
                text=f"🟢 {slot}",
                callback_data=f"time_{barber_id}_{service_id}_{date_str}_{slot}"
            )
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Sanalarga qaytish",
            callback_data=f"srv_{barber_id}_{service_id}"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_booking_kb(barber_id: int, service_id: int, date_str: str, time_str: str) -> InlineKeyboardMarkup:
    """
    Mijoz bronini tasdiqlash
    """
    buttons = [
        [InlineKeyboardButton(text="✅ Bronni tasdiqlash", callback_data=f"cnf_{barber_id}_{service_id}_{date_str}_{time_str}")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_booking")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def phone_request_kb() -> ReplyKeyboardMarkup:
    """
    Telefon raqam so'rash klaviaturasi
    """
    kb = [
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)


# ================== MASTER KEYBOARDS ==================

def barber_decision_kb(appointment_id: int) -> InlineKeyboardMarkup:
    """
    Masterga yangi bron kelganda: Tasdiqlash / Bekor qilish
    """
    buttons = [
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"m_accept_{appointment_id}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"m_reject_{appointment_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def barber_claim_kb(barbers: List[asyncpg.Record]) -> InlineKeyboardMarkup:
    """
    /barber buyrug'ida usta o'z profilini tanlashi uchun
    """
    buttons = []
    for b in barbers:
        status_icon = "🟢" if b["telegram_id"] else "⚪️"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status_icon} {b['name']} ({b['category']})",
                callback_data=f"claim_barber_{b['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_master_action")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def barber_schedule_nav_kb(target_date: date) -> InlineKeyboardMarkup:
    """
    Jadvalda boshqa sanalarga o'tish (Bugun, Ertaga)
    """
    today = date.today()
    tomorrow = today + timedelta(days=1)
    buttons = [
        [
            InlineKeyboardButton(text="📅 Bugun", callback_data=f"view_day_{today.strftime('%Y-%m-%d')}"),
            InlineKeyboardButton(text="📅 Ertaga", callback_data=f"view_day_{tomorrow.strftime('%Y-%m-%d')}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def client_bookings_kb(bookings: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """
    Mijoz o'z bronlarini ko'rganda bekor qilish imkoni
    """
    buttons = []
    for b in bookings:
        status_text = "✅" if b["status"] == "confirmed" else "⏳"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status_text} #{b['id']} | {b['appointment_date']} {b['appointment_time']} ({b['barber_name']})",
                callback_data=f"details_booking_{b['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh sahifa", callback_data="nav_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
