import asyncpg
import logging
from datetime import date, time
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        raise RuntimeError("Ma'lumotlar bazasi pooli hali ishga tushirilmagan.")
    return _pool


async def init_db(dsn: str):
    """
    Railway PostgreSQL bazasiga ulanish va jadvallarni tekshirish / sozlash.
    """
    global _pool
    logger.info("Railway PostgreSQL bazasiga ulanish o'rnatilmoqda...")
    _pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=10)

    async with _pool.acquire() as conn:
        # 1. clients jadvalini mavjudligini ta'minlash
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                full_name VARCHAR(255),
                phone_number VARCHAR(50)
            );
        """)
        # Qo'shimcha ustunlarni xavfsiz qo'shish
        await conn.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS username VARCHAR(255);")
        await conn.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;")

        # 2. barbers jadvalini mavjudligini ta'minlash
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS barbers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                telegram_id BIGINT UNIQUE
            );
        """)
        await conn.execute("ALTER TABLE barbers ADD COLUMN IF NOT EXISTS phone_number VARCHAR(50);")
        await conn.execute("ALTER TABLE barbers ADD COLUMN IF NOT EXISTS experience_years INT DEFAULT 3;")
        await conn.execute("ALTER TABLE barbers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;")

        # 3. services jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(50) DEFAULT 'main',
                price_pro INT NOT NULL DEFAULT 80000,
                price_top INT NOT NULL DEFAULT 120000,
                price_vip INT NOT NULL DEFAULT 180000
            );
        """)

        # 4. appointments jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                client_id INT REFERENCES clients(id) ON DELETE CASCADE,
                barber_id INT REFERENCES barbers(id) ON DELETE CASCADE,
                service_id INT REFERENCES services(id) ON DELETE CASCADE,
                appointment_date DATE NOT NULL,
                appointment_time TIME WITHOUT TIME ZONE NOT NULL,
                status VARCHAR(50) DEFAULT 'pending'
            );
        """)

        # Faol bronlar uchun unikal indeks (bir vaqtda bir usta faqat bitta faol bronga ega bo'lishi mumkin)
        await conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_booking 
            ON appointments (barber_id, appointment_date, appointment_time) 
            WHERE status != 'cancelled';
        """)

        # Har bir toifada kamida bitta master borligini ta'minlash
        categories = ['PRO', 'TOP', 'VIP']
        default_barbers_data = {
            'PRO': [('Jasur (PRO)', 3), ('Sardor (PRO)', 4)],
            'TOP': [('Abduvali (TOP)', 5), ('Aziz (TOP)', 6)],
            'VIP': [('Niyozali (VIP)', 8), ('Bekzod (VIP)', 10)]
        }
        for cat in categories:
            cat_count = await conn.fetchval("SELECT COUNT(*) FROM barbers WHERE category = $1;", cat)
            if cat_count == 0:
                for b_name, exp in default_barbers_data[cat]:
                    await conn.execute("""
                        INSERT INTO barbers (name, category, experience_years, is_active)
                        VALUES ($1, $2, $3, TRUE);
                    """, b_name, cat, exp)

        # Xizmatlarni to'ldirish
        srv_count = await conn.fetchval("SELECT COUNT(*) FROM services;")
        if srv_count < 4:
            additional_services = [
                ("Soch va Soqol kompleksi", "complex", 120000, 180000, 250000),
                ("Soqol tekislash va shakl berish", "beard", 50000, 75000, 110000),
                ("VIP Spa muolajasi va parvarish", "spa", 70000, 100000, 150000),
            ]
            for s_name, s_type, p_pro, p_top, p_vip in additional_services:
                await conn.execute("""
                    INSERT INTO services (name, type, price_pro, price_top, price_vip)
                    SELECT $1::varchar, $2::varchar, $3::int, $4::int, $5::int
                    WHERE NOT EXISTS (SELECT 1 FROM services WHERE name = $1::varchar);
                """, s_name, s_type, p_pro, p_top, p_vip)

    logger.info("✅ PostgreSQL bazasi sozlamalari va jadvallari muvaffaqiyatli tayyorlandi.")


async def close_db():
    global _pool
    if _pool:
        await _pool.close()
        logger.info("PostgreSQL ulanishi yopildi.")


# ================== MIJOZLAR (CLIENTS) ==================

async def add_or_get_client(telegram_id: int, full_name: str, username: Optional[str] = None) -> asyncpg.Record:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
            INSERT INTO clients (telegram_id, full_name, username)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) DO UPDATE 
            SET full_name = EXCLUDED.full_name,
                username = COALESCE(EXCLUDED.username, clients.username)
            RETURNING *;
        """, telegram_id, full_name, username)


async def get_client_by_telegram_id(telegram_id: int) -> Optional[asyncpg.Record]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM clients WHERE telegram_id = $1;", telegram_id)


async def update_client_phone(telegram_id: int, phone_number: str) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE clients 
            SET phone_number = $1 
            WHERE telegram_id = $2;
        """, phone_number, telegram_id)


# ================== MASTERLAR (BARBERS) ==================

async def get_barbers_by_category(category: str) -> List[asyncpg.Record]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT * FROM barbers 
            WHERE category = $1 AND is_active = TRUE 
            ORDER BY id ASC;
        """, category)


async def get_barber_by_id(barber_id: int) -> Optional[asyncpg.Record]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM barbers WHERE id = $1;", barber_id)


async def get_barber_by_telegram_id(telegram_id: int) -> Optional[asyncpg.Record]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM barbers WHERE telegram_id = $1;", telegram_id)


async def link_barber(barber_id: int, telegram_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Avval bu telegram_id boshqa ustada bo'lsa tozalaymiz
        await conn.execute("UPDATE barbers SET telegram_id = NULL WHERE telegram_id = $1;", telegram_id)
        # Endi yangi ustaga biriktiramiz
        result = await conn.execute("UPDATE barbers SET telegram_id = $1 WHERE id = $2;", telegram_id, barber_id)
        return "UPDATE 1" in result


async def unlink_barber(telegram_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("UPDATE barbers SET telegram_id = NULL WHERE telegram_id = $1;", telegram_id)
        return "UPDATE 1" in result


async def get_all_barbers() -> List[asyncpg.Record]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM barbers ORDER BY category, id ASC;")


# ================== XIZMATLAR (SERVICES) ==================

async def get_all_services() -> List[asyncpg.Record]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM services ORDER BY id ASC;")


async def get_service_by_id(service_id: int) -> Optional[asyncpg.Record]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM services WHERE id = $1;", service_id)


def calculate_service_price(service_row: asyncpg.Record, barber_category: str) -> int:
    """
    Master toifasiga ko'ra narxni aniqlash (PRO, TOP, VIP).
    """
    cat = barber_category.upper()
    if cat == "PRO":
        return service_row["price_pro"]
    elif cat == "TOP":
        return service_row["price_top"]
    elif cat == "VIP":
        return service_row["price_vip"]
    return service_row["price_pro"]


# ================== BRONLAR (APPOINTMENTS) ==================

async def get_booked_times(barber_id: int, appointment_date: date) -> List[str]:
    """
    Tanlangan usta va sanada band bo'lgan vaqtlar ro'yxati (Format: '10:00', '11:00').
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT to_char(appointment_time, 'HH24:MI') as b_time
            FROM appointments
            WHERE barber_id = $1 
              AND appointment_date = $2 
              AND status != 'cancelled';
        """, barber_id, appointment_date)
        return [r["b_time"] for r in rows]


async def create_appointment(
    client_db_id: int,
    barber_id: int,
    service_id: int,
    appointment_date: date,
    appointment_time_str: str
) -> Optional[int]:
    """
    Yangi bron qo'shish. Agar muvaffaqiyatli bo'lsa appointment_id qaytaradi, aks holda None.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow("""
                INSERT INTO appointments (client_id, barber_id, service_id, appointment_date, appointment_time, status)
                VALUES ($1, $2, $3, $4, $5::time, 'pending')
                RETURNING id;
            """, client_db_id, barber_id, service_id, appointment_date, appointment_time_str)
            return row["id"] if row else None
        except asyncpg.UniqueViolationError:
            return None


async def get_appointment_with_details(appointment_id: int) -> Optional[Dict[str, Any]]:
    """
    Bron haqida barcha bog'liq ma'lumotlar bilan qaytaradi.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT 
                a.id,
                a.client_id,
                a.barber_id,
                a.service_id,
                a.appointment_date,
                to_char(a.appointment_time, 'HH24:MI') AS appointment_time,
                a.status,
                c.telegram_id AS client_telegram_id,
                c.full_name AS client_name,
                c.username AS client_username,
                c.phone_number AS client_phone,
                b.name AS barber_name,
                b.category AS barber_category,
                b.telegram_id AS barber_telegram_id,
                s.name AS service_name,
                s.price_pro,
                s.price_top,
                s.price_vip
            FROM appointments a
            JOIN clients c ON a.client_id = c.id
            JOIN barbers b ON a.barber_id = b.id
            JOIN services s ON a.service_id = s.id
            WHERE a.id = $1;
        """, appointment_id)
        if not row:
            return None
        data = dict(row)
        cat = data["barber_category"].upper()
        if cat == "PRO":
            data["price"] = data["price_pro"]
        elif cat == "TOP":
            data["price"] = data["price_top"]
        else:
            data["price"] = data["price_vip"]
        return data


async def update_appointment_status(appointment_id: int, status: str) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        res = await conn.execute("""
            UPDATE appointments 
            SET status = $1 
            WHERE id = $2;
        """, status, appointment_id)
        return "UPDATE 1" in res


async def get_barber_appointments_for_date(barber_id: int, target_date: date) -> List[Dict[str, Any]]:
    """
    Master uchun tanlangan kundagi barcha bronlar.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT 
                a.id,
                to_char(a.appointment_time, 'HH24:MI') AS appointment_time,
                a.status,
                c.full_name AS client_name,
                c.phone_number AS client_phone,
                c.username AS client_username,
                s.name AS service_name,
                b.category AS barber_category,
                s.price_pro,
                s.price_top,
                s.price_vip
            FROM appointments a
            JOIN clients c ON a.client_id = c.id
            JOIN barbers b ON a.barber_id = b.id
            JOIN services s ON a.service_id = s.id
            WHERE a.barber_id = $1 
              AND a.appointment_date = $2
            ORDER BY a.appointment_time ASC;
        """, barber_id, target_date)
        res = []
        for r in rows:
            d = dict(r)
            cat = d["barber_category"].upper()
            if cat == "PRO":
                d["price"] = d["price_pro"]
            elif cat == "TOP":
                d["price"] = d["price_top"]
            else:
                d["price"] = d["price_vip"]
            res.append(d)
        return res


async def get_client_upcoming_appointments(client_telegram_id: int) -> List[Dict[str, Any]]:
    """
    Mijozning kelgusi faol bronlari.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT 
                a.id,
                a.appointment_date,
                to_char(a.appointment_time, 'HH24:MI') AS appointment_time,
                a.status,
                b.name AS barber_name,
                b.category AS barber_category,
                s.name AS service_name,
                s.price_pro,
                s.price_top,
                s.price_vip
            FROM appointments a
            JOIN clients c ON a.client_id = c.id
            JOIN barbers b ON a.barber_id = b.id
            JOIN services s ON a.service_id = s.id
            WHERE c.telegram_id = $1 
              AND a.appointment_date >= CURRENT_DATE
              AND a.status != 'cancelled'
            ORDER BY a.appointment_date ASC, a.appointment_time ASC;
        """, client_telegram_id)
        res = []
        for r in rows:
            d = dict(r)
            cat = d["barber_category"].upper()
            if cat == "PRO":
                d["price"] = d["price_pro"]
            elif cat == "TOP":
                d["price"] = d["price_top"]
            else:
                d["price"] = d["price_vip"]
            res.append(d)
        return res


async def cancel_appointment_by_client(appointment_id: int, client_telegram_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        res = await conn.execute("""
            UPDATE appointments 
            SET status = 'cancelled'
            WHERE id = $1 
              AND client_id IN (SELECT id FROM clients WHERE telegram_id = $2);
        """, appointment_id, client_telegram_id)
        return "UPDATE 1" in res
