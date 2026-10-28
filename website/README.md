# Culture Barbershop — Netlify Deployment Guide

Ushbu papka (`website/`) Netlify'ga mustaqil (standalone) veb-sayt sifatida deploy qilish uchun to'liq tayyorlangan.

## 🚀 Netlify'ga yuklash usullari:

### 1-usul: Netlify Drop orqali (Eng oson, 30 soniyada)
1. Brauzerda [app.netlify.com/drop](https://app.netlify.com/drop) sahifasini oching.
2. Ushbu `website` papkasini sichqoncha bilan ushlab, Netlify oynasiga tashlang (drag & drop).
3. Sayt darhol ishga tushadi va sizga bepul `https://...netlify.app` domeni beriladi!

### 2-usul: GitHub orqali
1. Netlify boshqaruv panelidan **"Add new site" -> "Import an existing project"** ni bosing.
2. `barberbot` repozitoriyasini tanlang.
3. Sozlamalarda quyidagilarni ko'rsating:
   - **Base directory:** `website`
   - **Publish directory:** `website`
4. **Deploy** tugmasini bosing. Har safar GitHub'ga push qilganingizda Netlify avtomatik yangilanadi.

---

## 🔗 Web App integratsiyasi
Saytdagi barcha **"Onlayn yozilish"** va narxlar jadvalidagi **"Yozilish"** tugmalari to'g'ridan-to'g'ri Render'dagi Web App'ga (`https://culture-barbershop.onrender.com`) ulanadi.

Foydalanuvchi ma'lum bir toifani (masalan: VIP) tanlab yozilishni bossa, Web App darhol o'sha toifadagi sartaroshlar ro'yxatini ochadi.
