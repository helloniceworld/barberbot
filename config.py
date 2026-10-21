import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN", "8993710605:AAFS2jVBH_KxGWWquVPLvQtkijth7gSwJBY")
BOT_USERNAME = os.getenv("BOT_USERNAME", "culturebarbersbot")

# PostgreSQL Database URL
# Mahalliy test uchun (Public URL): postgresql://postgres:auIPwtnYVuVuXQYkZfvQgHqOyXbPxWlC@hayabusa.proxy.rlwy.net:23861/railway
# Railway serverda (Internal URL): postgresql://postgres:auIPwtnYVuVuXQYkZfvQgHqOyXbPxWlC@postgres.railway.internal:5432/railway
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:auIPwtnYVuVuXQYkZfvQgHqOyXbPxWlC@hayabusa.proxy.rlwy.net:23861/railway"
)

# Barbershop ish vaqtlari (har 1 soatlik slotlar)
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
    "20:00"
]

# Master toifalari
CATEGORIES = {
    "PRO": "⭐️ PRO Master",
    "TOP": "🔥 TOP Master",
    "VIP": "👑 VIP Master"
}
