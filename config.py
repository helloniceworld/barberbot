import os
from dotenv import load_dotenv

load_dotenv()

# ================== BOT TOKENS ==================
# 1. Mijozlar uchun bot (@culturebarbersbot)
CLIENT_BOT_TOKEN = os.getenv("CLIENT_BOT_TOKEN", "8993710605:AAHYkEM9HxVduNZ602fbyaiVikQg71ZoXgI").strip()
CLIENT_BOT_USERNAME = os.getenv("CLIENT_BOT_USERNAME", "culturebarbersbot").strip()

# 2. Xodimlar va Sartaroshlar uchun bot (@culturestaffbot)
STAFF_BOT_TOKEN = os.getenv("STAFF_BOT_TOKEN", "8887166444:AAFpOdLjgM7q3mrXI1oFGCSv6obWvuW93Jw").strip()
STAFF_BOT_USERNAME = os.getenv("STAFF_BOT_USERNAME", "culturestaffbot").strip()

# ================== DATABASE ==================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:auIPwtnYVuVuXQYkZfvQgHqOyXbPxWlC@hayabusa.proxy.rlwy.net:23861/railway"
).strip()

# ================== WEB APP & SERVER ==================
# Render avtomatik ravishda RENDER_EXTERNAL_URL beradi (masalan: https://barberbot.onrender.com)
render_url = os.getenv("RENDER_EXTERNAL_URL", "").strip()
if render_url and not render_url.startswith("http"):
    render_url = f"https://{render_url}"

WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip() or render_url or "http://localhost:8000"
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# ================== BARBERSHOP SETTINGS ==================
SHOP_NAME = "Culture Barbershop"
SHOP_ADDRESS = "Toshkent shahri, Amir Temur shoh ko'chasi 42"
SHOP_PHONE = "+998 90 000 00 00"
SHOP_LOCATION_URL = "https://maps.google.com"

# Ish vaqti slotlari (har 1 soatlik slot)
WORK_HOURS = [
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
    "19:00",
    "20:00",
    "21:00"
]

# Master toifalari (Figma dizayni bo'yicha)
CATEGORIES = {
    "PRO": {
        "id": "PRO",
        "name": "PRO Barber",
        "badge": None,
        "subtitle": "Standard Excellence",
        "description": "Everyday style & classic cuts",
        "base_price": 80000,
        "icon": "✦"
    },
    "TOP": {
        "id": "TOP",
        "name": "TOP Barber",
        "badge": "POPULAR",
        "subtitle": "Master Experience",
        "description": "Advanced precision & custom styling",
        "base_price": 120000,
        "icon": "★"
    },
    "VIP": {
        "id": "VIP",
        "name": "VIP Barber",
        "badge": "SIGNATURE",
        "subtitle": "Signature Luxury",
        "description": "Master cut, premium beard care & spa",
        "base_price": 180000,
        "icon": "👑"
    },
    "BRAND": {
        "id": "BRAND",
        "name": "BRAND Barber",
        "badge": "EXCLUSIVE",
        "subtitle": "Artistic Director",
        "description": "Exclusive full package & VIP lounge",
        "base_price": 250000,
        "icon": "💎"
    }
}
