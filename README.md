# 💈 Culture Barbershop — Telegram Web App & Dual-Bot Ecosystem

Ushbu loyiha **Culture Barbershop** uchun maxsus ishlab chiqilgan bo'lib, o'zida ikkita ixtisoslashgan Telegram bot va Figma dizayni asosida 1:1 formatda yaratilgan hashamatli **Telegram Web App (Mini App)** tizimini birlashtiradi.

---

## 🌟 Loyiha Arxitekturasi

```
                          ┌──────────────────────────┐
                          │   PostgreSQL (Railway)   │
                          └─────────────┬────────────┘
                                        │
           ┌────────────────────────────┼───────────────────────────┐
           │                            │                           │
           ▼                            ▼                           ▼
┌──────────────────────┐   ┌───────────────────────────┐   ┌──────────────────────┐
│  @culturebarbersbot  │   │    FastAPI & Web App      │   │   @culturestaffbot   │
│   (Mijozlar Boti)    │   │  (1:1 Figma Luxury App)   │   │  (Sartaroshlar Boti) │
└──────────────────────┘   └───────────────────────────┘   └──────────────────────┘
       Mijoz bron                 Web App interfeysi             Usta Telegramiga
        qiladi                    va REST API'lar               to'g'ridan-to'g'ri
                                                                   buyurtma boradi
```

### 1. 🤖 Mijozlar Boti: `@culturebarbersbot`
- **Token:** `8993710605:AAFS2jVBH_KxGWWquVPLvQtkijth7gSwJBY`
- **Vazifasi:**
  - Mijozlarni kutib olish va **"💈 Bron qilish (Web App)"** tugmasi orqali Mini App interfeysini ochish.
  - Mijoz o'zining barcha bronlarini ko'rishi va bekor qilishi mumkin bo'lgan **"Mening bronlarim"** bo'limi.
  - Manzil, ish vaqti (10:00 - 22:00) va aloqa ma'lumotlari.
  - **Avtomatik bildirishnomalar:** Usta buyurtmani qabul qilganida yoki rad etganida mijozga real-vaqtda xabar keladi.

### 2. ✂️ Sartaroshlar Boti: `@culturestaffbot`
- **Token:** `8887166444:AAHRK7kUUGOE8Z56C_ZAEGDn7gmEPs62LTE`
- **Vazifasi:**
  - Har bir sartarosh `/start` bosganda o'z profilini (masalan: *Abduvali (TOP)*, *Jasur (PRO)*, *Niyozali (VIP)*) tanlab, Telegram ID sini profilga biriktiradi.
  - **Yangi bron xabari:** Mijoz Web App yoki bot orqali bron qilishi bilan, aynan tanlangan ustaning botdagi shaxsiy chatiga quyidagi formatda bildirishnoma boradi:
    - 🗓 Sana va Vaqt
    - ✂️ Xizmatlar
    - 💰 Jami summa
    - 👤 Mijoz ismi, telefon raqami va Telegram profili
    - `[ ✅ Qabul qilish ]` va `[ ❌ Rad etish ]` tugmalari
  - Usta `✅ Qabul qilish` tugmasini bosishi bilanoq, mijozning `@culturebarbersbot`iga tasdiqlash xabari avtomatik yuboriladi.
  - **Kun tartibi va statistika:**
    - `📅 Bugungi navbatlar`
    - `🗓 Ertangi navbatlar`
    - `📋 Faol bronlar`
    - `📊 Statistika` (bugungi tushum, mijozlar soni, umumiy natijalar)

### 3. 📱 Telegram Web App (Mini App) — Figma 1:1 Dizayn
- **Figma manbasi:** [Luxury Barbershop App Design](https://www.figma.com/make/hAXwLgAPSlnQI6QF4KqUk2/Luxury-Barbershop-App-Design?t=i4V2sGAhazFcLuWm-20&fullscreen=1)
- **Dizayn xususiyatlari:**
  - **Ranglar:** Obsidian qora (`#0C0C0E`), chuqur grafit (`#141418`), hashamatli oltin (`#D4AF37`, `#E5A93C`) va glowing effektlar.
  - **Tipografika:** *Playfair Display* (sarlavhalar) va *Plus Jakarta Sans* (interfeys).
  - **1-qadam (Step 1):** *Choose your level of craft* — 4 toifadagi kartochkalar:
    - **PRO Barber** (✦ Standard Excellence — from 80 000 UZS)
    - **TOP Barber** (★ POPULAR nishonli, tilla ramkali — from 120 000 UZS)
    - **VIP Barber** (👑 Signature Luxury — from 180 000 UZS)
    - **BRAND Barber** (💎 Artistic Director — from 250 000 UZS)
  - **2-qadam (Step 2):** *Select your Barber* — Tanlangan toifadagi tajribali ustalarni ko'rish va tanlash.
  - **3-qadam (Step 3):** *Choose Services* — Ko'p tanlovli (multi-select) xizmatlar, jonli narx hisoblagich.
  - **4-qadam (Step 4):** *Select Date & Time* — Gorizontal kunlar lentasi va dinamik bo'sh vaqt slotlari (band vaqtlar bloklanadi).
  - **5-qadam (Step 5):** *Booking Summary & Contact* — Telegram foydalanuvchi ma'lumotlarini avtomatik to'ldirish va tasdiqlash.
  - **6-qadam (Step 6):** Hashamatli animatsion tilla chek va qabul qilinganlik holati.
  - **Mening bronlarim:** Istalgan vaqtda yuqori o'ng burchakdagi profil ikonkasi orqali barcha bronlarni ko'rish va bekor qilish.

---

## 🛠 Fayllar Tuzilishi

```
barberbot/
├── .env                  # Maxfiy kalitlar va sozlamalar
├── .env.example          # Namuna sozlamalar
├── config.py             # Global konstantalar, toifalar va narxlar
├── database.py           # PostgreSQL asyncpg boshqaruvi va modellar
├── services.py           # Ikkala bot o'rtasidagi xabarnomalar xizmati
├── bots/
│   ├── __init__.py
│   ├── client_bot.py     # @culturebarbersbot boshqaruvi
│   └── staff_bot.py      # @culturestaffbot (ustalar boti) boshqaruvi
├── api/
│   ├── __init__.py
│   └── routes.py         # REST API endpointlari (/api/slots, /api/book, ...)
├── web/
│   ├── index.html        # Telegram Web App HTML
│   ├── css/
│   │   └── style.css     # Figma 1:1 hashamatli dizayn tizimi
│   └── js/
│       └── app.js        # Telegram WebApp SDK va interaktiv bron oqimi
├── main.py               # Web server + 2 ta botni birgalikda ishga tushiruvchi markaziy fayl
├── requirements.txt      # Python kutubxonalari
└── Procfile              # Railway / Cloud deploy fayli
```

---

## 🚀 Ishga Tushirish Qo'llanmasi

### 1. Talablar
- Python 3.10 yoki undan yuqori
- PostgreSQL ma'lumotlar bazasi (Railway ulanishi allaqachon tayyor)

### 2. O'rnatish
```bash
# Virtual muhitni faollashtirish
.\venv\Scripts\activate

# Kutubxonalarni o'rnatish
pip install -r requirements.txt
```

### 3. Server va Botlarni Ishga Tushirish
Bitta buyruq orqali Web server, Mijoz boti va Xodimlar boti parallel ravishda ishga tushadi:
```bash
python main.py
```

### 4. Railway orqali Deploy qilish
1. Ushbu repozitoriyni GitHub ga yuklang.
2. Railway da loyiha ochib, GitHub repoga ulang.
3. `.env` dagi barcha o'zgaruvchilarni Railway **Variables** bo'limiga qo'shing.
4. Railway taqdim etgan domen manzilini (masalan: `https://culturebarbershop.up.railway.app`) `WEBAPP_URL` sifatida o'rnating.
5. BotFather da `@culturebarbersbot` uchun Menu Button sifatida shu WebApp URL ni sozlang.
