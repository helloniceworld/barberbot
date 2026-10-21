# 💈 "Culture Barbershop" Telegram Boti

Zamonaviy **aiogram 3.x** va **Railway PostgreSQL** bazasi asosida yaratilgan, to'liq avtomatlashtirilgan Barbershop telegram boti.

* **Bot Username:** [@culturebarbersbot](https://t.me/culturebarbersbot)
* **Kutubxona:** Python `aiogram 3.x`, `asyncpg`, `python-dotenv`
* **Ma'lumotlar bazasi:** Railway PostgreSQL (Asinxron ulanish pooli bilan)

---

## 📁 Loyiha Strukturasi

```text
barberbot/
├── .env                  # Maxfiy tokenlar va DB URL (Lokal muhit)
├── .env.example          # Namuna sozlamalar
├── .gitignore            # Git uchun e'tiborsiz qoldiriladigan fayllar
├── requirements.txt      # Kerakli Python kutubxonalari
├── config.py             # Loyiha konfiguratsiyasi va ish soatlari
├── database.py           # PostgreSQL jadvallari, CRUD va asinxron mantiq
├── keyboards.py          # Inline va Reply klaviaturalar
├── main.py               # Asosiy ishga tushiruvchi fayl (Entrypoint)
├── handlers/
│   ├── __init__.py
│   ├── client.py         # Mijozlar uchun: /start, toifalar, xizmatlar, vaqt tanlash, bron
│   └── barber.py         # Masterlar uchun: /barber, /bronlar, tasdiqlash/bekor qilish
└── .vscode/
    ├── extensions.json   # Tavsiya etilgan VS Code plaginlari
    └── settings.json     # Python venv avtomatik tanlanishi sozlamasi
```

---

## 🛠 1. VS Code uchun Sozlamalar va Extension'lar

Loyiha papkasida ochganingizda VS Code quyidagi extension'larni avtomatik tavsiya qiladi (`.vscode/extensions.json`):

1. **Python (`ms-python.python`)**: Python tilini qo'llab-quvvatlash, sintaksisni tekshirish va ishga tushirish uchun.
2. **Pylance (`ms-python.vscode-pylance`)**: Juda tezkor autocompletion, tur tekshiruvi va kod tahlili uchun.
3. **Database Client (`cweijan.vscode-postgresql-client2`)**: Railway PostgreSQL bazasiga to'g'ridan-to'g'ri VS Code ichidan ulanib, jadvallarni vizual ko'rish va boshqarish uchun.
4. **DotENV (`mikestead.dotenv`)**: `.env` fayllaridagi o'zgaruvchilarni chiroyli ranglar bilan ajratib ko'rsatish uchun.

---

## 🚀 2. Kompyuterda Ishga Tushirish (Local Run)

### 1-qadam: Virtual muhit (venv) yaratish va faollashtirish
VS Code terminalida (`Ctrl + ~`):

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*(Agar skriptlarni ishga tushirish bloklangan bo'lsa: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2-qadam: Kerakli kutubxonalarni o'rnatish
```powershell
pip install -r requirements.txt
```

### 3-qadam: `.env` sozlamalarini tekshirish
Loyiha ildizidagi `.env` faylida quyidagi ma'lumotlar kiritilgan:
```env
BOT_TOKEN=8993710605:AAFS2jVBH_KxGWWquVPLvQtkijth7gSwJBY
BOT_USERNAME=culturebarbersbot

# Kompyuterdan test qilish uchun (Public URL):
DATABASE_URL=postgresql://postgres:auIPwtnYVuVuXQYkZfvQgHqOyXbPxWlC@hayabusa.proxy.rlwy.net:23861/railway

# Railway serverida deploy qilganda (Internal URL):
# DATABASE_URL=postgresql://postgres:auIPwtnYVuVuXQYkZfvQgHqOyXbPxWlC@postgres.railway.internal:5432/railway
```

### 4-qadam: Botni ishga tushirish
```powershell
python main.py
```

Konsolda quyidagi xabar paydo bo'ladi:
```text
💈 Culture Barbershop Telegram boti ishga tushirilmoqda...
✅ PostgreSQL bazasi sozlamalari va jadvallari muvaffaqiyatli tayyorlandi.
🚀 Bot to'liq tayyor va yangilanishlarni qabul qilishni boshladi!
```

---

## 💈 3. Bot Funksionalliklari va Ishlash Tartibi

### 👤 Mijozlar Uchun:
1. **/start buyrug'i:**
   - Mijoz ma'lumotlari avtomatik ravishda `clients` jadvaliga kiritiladi yoki yangilanadi.
   - Master toifalari chiroyli Inline tugmalar ko'rinishida taqdim etiladi:
     - `⭐️ PRO Masterlar`
     - `🔥 TOP Masterlar`
     - `👑 VIP Masterlar`
     - `📋 Mening bronlarim`
     - `ℹ️ Biz haqimizda / Manzil`
2. **Master va Xizmat tanlash:**
   - Tanlangan toifaga tegishli ustalar ro'yxati chiqadi (`barbers` jadvalidan).
   - Usta tanlangach, narxlari usta toifasiga moslashtirilgan xizmatlar menyusi chiqadi (`services` jadvalidan).
3. **Sana va Bo'sh vaqtlarni tanlash:**
   - Yaqin 5 kunlik sanalar chiqadi (Bugun, Ertaga va keyingi kunlar).
   - Sana tanlangach, masterning o'sha kungi jadvali tekshiriladi:
     - Bo'sh vaqtlar: `🟢 10:00`, `🟢 11:00` kabi yashil va bosiladigan holatda bo'ladi.
     - Band vaqtlar: `❌ 14:00 (Band)` deb chiqadi va bosish bloklanadi (foydalanuvchiga *"Bu vaqt allaqachon band"* xabarnomasi chiqadi).
4. **Tasdiqlash va Kontakt:**
   - Agar mijoz birinchi marta bron qilayotgan bo'lsa, telefon raqamini yuborish so'raladi.
   - Bron yakuniy tasdiqlanganda `appointments` jadvaliga `pending` (kutilmoqda) holatida saqlanadi.
5. **Mening bronlarim:**
   - Mijoz istalgan vaqt o'zining kelgusi bronlarini ko'rishi va kerak bo'lsa bekor qilishi mumkin.

---

### ✂️ Masterlar Uchun (Usta Kabineti):
1. **/barber buyrug'i (Akkauntni bog'lash):**
   - Har bir master o'z Telegram akkauntini bazadagi o'z ismi bilan 1 marta bog'lab oladi.
   - Bot ustalarni ro'yxat qilib chiqaradi (masalan: `💈 Jasur (PRO)`, `💈 Abduvali (TOP)`, `💈 Niyozali (VIP)`).
   - Usta o'z ismini bossa, uning `telegram_id` raqami bazada ushbu ustaga biriktiriladi.
2. **Yangi bron bildirishnomasi:**
   - Mijoz vaqt tanlab tasdiqlashi bilanoq, tegishli masterga Telegram orqali xabar boradi:
     ```text
     🔔 YANGI BRON! (#12)
     👤 Mijoz: Ali Valiyev (@ali_valiyev)
     📞 Tel: +998901234567
     ✂️ Xizmat: Soch va Soqol kompleksi (120 000 so'm)
     📅 Sana: 2026-10-21
     ⏰ Vaqt: 14:00
     ```
   - Master uchun ikkita interaktiv tugma chiqadi:
     - `✅ Tasdiqlash`
     - `❌ Bekor qilish`
   - Master `✅ Tasdiqlash` ni bossa:
     - Bazadagi holat `confirmed` ga o'zgaradi.
     - Mijozga darhol quvonchli bildirishnoma boradi: *"Sizning broningiz usta tomonidan TASDIQLANDI!"*.
   - Master `❌ Bekor qilish` ni bossa:
     - Bazadagi holat `cancelled` ga o'zgaradi va vaqt sloti yana boshqa mijozlar uchun bo'shaydi.
     - Mijozga usta bronni qabul qila olmaganligi xabar qilinadi.
3. **/bronlar buyrug'i (Kunlik jadval):**
   - Master o'zining bugungi va ertangi kungi qabullarini, mijozlar ismlari, telefon raqamlari va holatini bitta ro'yxatda ko'radi.

---

## ☁️ 4. Railway Serveriga Deploy Qilish (24/7 Ishlash)

Railway platformasida botni 24/7 rejimida to'xtovsiz ishlatish uchun:

1. Ushbu loyihani GitHub repozitoriyingizga push qiling (`git push origin main`).
2. [Railway.app](https://railway.app) ga kiring va yangi Service sifatida o'sha GitHub repozitoriyani tanlang.
3. **Variables** (Muhit o'zgaruvchilari) bo'limida quyidagilarni kiriting:
   - `BOT_TOKEN` = `8993710605:AAFS2jVBH_KxGWWquVPLvQtkijth7gSwJBY`
   - `BOT_USERNAME` = `culturebarbersbot`
   - `DATABASE_URL` = `postgresql://postgres:auIPwtnYVuVuXQYkZfvQgHqOyXbPxWlC@postgres.railway.internal:5432/railway`
     *(Railway ichki tarmog'ida tezroq va xavfsizroq ishlashi uchun Internal URL ishlatiladi)*
4. Railway avtomatik ravishda `requirements.txt` ni o'rnatadi va `python main.py` orqali botni 24/7 ishga tushiradi!
