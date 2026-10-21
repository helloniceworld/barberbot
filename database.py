import logging
from datetime import date, time, datetime
from typing import Optional, List, Dict, Any
import asyncpg
import config

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        raise RuntimeError("Ma'lumotlar bazasi pooli hali ishga tushirilmagan.")
    return _pool


async def init_db(dsn: str):
    """
    PostgreSQL bazasiga ulanish va jadvallarni tekshirish / yaratish / sozlash.
    """
    global _pool
    logger.info("PostgreSQL bazasiga ulanish o'rnatilmoqda...")
    _pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=10)

    async with _pool.acquire() as conn:
        # 1. clients jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                full_name VARCHAR(255),
                username VARCHAR(255),
                phone_number VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. barbers jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS barbers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                telegram_id BIGINT UNIQUE,
                phone_number VARCHAR(50),
                experience_years INT DEFAULT 3,
                photo_url VARCHAR(500),
                rating NUMERIC(2, 1) DEFAULT 4.9,
                is_active BOOLEAN DEFAULT TRUE
            );
        """)
        # Ustunlar borligini kafolatlash
        await conn.execute("ALTER TABLE barbers ADD COLUMN IF NOT EXISTS phone_number VARCHAR(50);")
        await conn.execute("ALTER TABLE barbers ADD COLUMN IF NOT EXISTS experience_years INT DEFAULT 3;")
        await conn.execute("ALTER TABLE barbers ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500);")
        await conn.execute("ALTER TABLE barbers ADD COLUMN IF NOT EXISTS rating NUMERIC(2, 1) DEFAULT 4.9;")
        await conn.execute("ALTER TABLE barbers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;")

        # 3. services jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(50) DEFAULT 'main',
                duration_min INT DEFAULT 45,
                price_pro INT NOT NULL DEFAULT 80000,
                price_top INT NOT NULL DEFAULT 120000,
                price_vip INT NOT NULL DEFAULT 180000,
                price_brand INT NOT NULL DEFAULT 250000,
                is_active BOOLEAN DEFAULT TRUE
            );
        """)
        await conn.execute("ALTER TABLE services ADD COLUMN IF NOT EXISTS duration_min INT DEFAULT 45;")
        await conn.execute("ALTER TABLE services ADD COLUMN IF NOT EXISTS price_brand INT NOT NULL DEFAULT 250000;")
        await conn.execute("ALTER TABLE services ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;")

        # 4. appointments jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                client_id INT REFERENCES clients(id) ON DELETE CASCADE,
                barber_id INT REFERENCES barbers(id) ON DELETE CASCADE,
                service_id INT REFERENCES services(id) ON DELETE SET NULL,
                service_ids INT[] DEFAULT '{}',
                total_price INT NOT NULL DEFAULT 0,
                appointment_date DATE NOT NULL,
                appointment_time TIME WITHOUT TIME ZONE NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                client_name VARCHAR(255),
                client_phone VARCHAR(50),
                client_username VARCHAR(255),
                cancellation_reason TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS total_price INT DEFAULT 0;")
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS service_ids INT[] DEFAULT '{}';")
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS client_name VARCHAR(255);")
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS client_phone VARCHAR(50);")
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS client_username VARCHAR(255);")
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS cancellation_reason TEXT;")

        # Unikal faol bron indeksi (bir sartarosh bir vaqtda faqat bitta faol mijozga xizmat qiladi)
        await conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_booking 
            ON appointments (barber_id, appointment_date, appointment_time) 
            WHERE status != 'cancelled';
        """)

        # Boshlang'ich ustalar mavjudligini tekshirish
        default_barbers = [
            ("Jasur", "PRO", 3, 4.8),
            ("Sardor", "PRO", 4, 4.9),
            ("Abduvali", "TOP", 5, 5.0),
            ("Aziz", "TOP", 6, 4.9),
            ("Niyozali", "VIP", 8, 5.0),
            ("Bekzod", "VIP", 10, 4.9),
            ("Jamshid (Brand Master)", "BRAND", 12, 5.0)
        ]
        b_count = await conn.fetchval("SELECT COUNT(*) FROM barbers;")
        if b_count == 0:
            for b_name, b_cat, b_exp, b_rat in default_barbers:
                await conn.execute("""
                    INSERT INTO barbers (name, category, experience_years, rating, is_active)
                    VALUES ($1, $2, $3, $4, TRUE);
                """, b_name, b_cat, b_exp, b_rat)

        # Boshlang'ich xizmatlar mavjudligini tekshirish
        default_services = [
            ("Soch kesish (Classic Haircut)", "main", 45, 80000, 120000, 180000, 250000),
            ("Soqol tekislash va shakl berish (Beard Trim)", "beard", 30, 50000, 75000, 110000, 150000),
            ("Soch va Soqol kompleksi (Combo)", "complex", 60, 120000, 180000, 250000, 350000),
            ("VIP Spa muolajasi va parvarish", "spa", 40, 70000, 100000, 150000, 200000),
            ("Bolalar sochini kesish (Kids)", "kids", 35, 50000, 70000, 100000, 140000),
            ("Soch yuvish va styling", "styling", 25, 40000, 60000, 80000, 120000)
        ]
        s_count = await conn.fetchval("SELECT COUNT(*) FROM services;")
        if s_count == 0:
            for s_name, s_type, s_dur, p_pro, p_top, p_vip, p_brand in default_services:
                await conn.execute("""
                    INSERT INTO services (name, type, duration_min, price_pro, price_top, price_vip, price_brand, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, TRUE);
                """, s_name, s_type, s_dur, p_pro, p_top, p_vip, p_brand)

    logger.info("Ma'lumotlar bazasi jadvallari tayyor.")


# ================== CLIENT FUNCTIONS ==================

async def get_or_create_client(telegram_id: int, full_name: Optional[str] = None, username: Optional[str] = None, phone_number: Optional[str] = None) -> Dict[str, Any]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO clients (telegram_id, full_name, username, phone_number)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (telegram_id) DO UPDATE 
            SET full_name = COALESCE(EXCLUDED.full_name, clients.full_name),
                username = COALESCE(EXCLUDED.username, clients.username),
                phone_number = COALESCE(EXCLUDED.phone_number, clients.phone_number)
            RETURNING *;
        """, telegram_id, full_name, username, phone_number)
        return dict(row)


async def get_client_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM clients WHERE telegram_id = $1;", telegram_id)
        return dict(row) if row else None


# ================== BARBER FUNCTIONS ==================

async def get_barbers(category: Optional[str] = None, active_only: bool = True) -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        query = "SELECT * FROM barbers WHERE 1=1"
        params = []
        if active_only:
            query += " AND is_active = TRUE"
        if category:
            params.append(category.upper())
            query += f" AND category = ${len(params)}"
        query += " ORDER BY id ASC;"
        rows = await conn.fetch(query, *params)
        return [dict(r) for r in rows]


async def get_barber_by_id(barber_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM barbers WHERE id = $1;", barber_id)
        return dict(row) if row else None


async def get_barber_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM barbers WHERE telegram_id = $1;", telegram_id)
        return dict(row) if row else None


async def link_barber_telegram(barber_id: int, telegram_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Avval bu telegram_id boshqa ustada bo'lsa tozalaymiz
        await conn.execute("UPDATE barbers SET telegram_id = NULL WHERE telegram_id = $1;", telegram_id)
        res = await conn.execute("UPDATE barbers SET telegram_id = $1 WHERE id = $2;", telegram_id, barber_id)
        return "UPDATE 1" in res


async def unlink_barber_telegram(barber_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        res = await conn.execute("UPDATE barbers SET telegram_id = NULL WHERE id = $1;", barber_id)
        return "UPDATE 1" in res


async def get_unlinked_barbers() -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM barbers WHERE telegram_id IS NULL AND is_active = TRUE ORDER BY category, id;")
        return [dict(r) for r in rows]


# ================== SERVICE FUNCTIONS ==================

async def get_services(active_only: bool = True) -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        query = "SELECT * FROM services"
        if active_only:
            query += " WHERE is_active = TRUE"
        query += " ORDER BY id ASC;"
        rows = await conn.fetch(query)
        return [dict(r) for r in rows]


async def get_service_by_id(service_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM services WHERE id = $1;", service_id)
        return dict(row) if row else None


async def get_services_by_ids(service_ids: List[int]) -> List[Dict[str, Any]]:
    if not service_ids:
        return []
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM services WHERE id = ANY($1::int[]) ORDER BY id ASC;", service_ids)
        return [dict(r) for r in rows]


# ================== APPOINTMENT & SLOT FUNCTIONS ==================

async def get_available_slots(barber_id: int, target_date: date) -> List[str]:
    """
    Berilgan sana va usta uchun bo'sh vaqt slotlarini qaytaradi.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Band qilingan vaqtlarni olish
        rows = await conn.fetch("""
            SELECT appointment_time 
            FROM appointments 
            WHERE barber_id = $1 
              AND appointment_date = $2 
              AND status != 'cancelled';
        """, barber_id, target_date)
        
        booked_times = {r['appointment_time'].strftime("%H:%M") for r in rows}
        
        # Bugungi kun bo'lsa, o'tib ketgan vaqtlarni chiqarib tashlash
        now = datetime.now()
        is_today = (target_date == now.date())
        current_time_str = now.strftime("%H:%M")

        available = []
        for slot in config.WORK_HOURS:
            if slot in booked_times:
                continue
            if is_today and slot <= current_time_str:
                continue
            available.append(slot)
            
        return available


async def is_slot_available(barber_id: int, target_date: date, target_time: time) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        count = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM appointments 
            WHERE barber_id = $1 
              AND appointment_date = $2 
              AND appointment_time = $3 
              AND status != 'cancelled';
        """, barber_id, target_date, target_time)
        return count == 0


async def create_appointment(
    client_id: int,
    barber_id: int,
    service_id: Optional[int],
    appointment_date: date,
    appointment_time: time,
    total_price: int,
    client_name: str,
    client_phone: str,
    client_username: Optional[str] = None,
    service_ids: Optional[List[int]] = None
) -> Dict[str, Any]:
    pool = await get_pool()
    if service_ids is None:
        service_ids = [service_id] if service_id else []

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO appointments (
                client_id, barber_id, service_id, service_ids, total_price,
                appointment_date, appointment_time, status,
                client_name, client_phone, client_username
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending', $8, $9, $10)
            RETURNING *;
        """, client_id, barber_id, service_id, service_ids, total_price,
           appointment_date, appointment_time, client_name, client_phone, client_username)
        return dict(row)


async def get_appointment_by_id(appointment_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT a.*, 
                   b.name as barber_name, b.category as barber_category, b.telegram_id as barber_telegram_id,
                   s.name as service_name,
                   c.telegram_id as client_telegram_id
            FROM appointments a
            LEFT JOIN barbers b ON a.barber_id = b.id
            LEFT JOIN services s ON a.service_id = s.id
            LEFT JOIN clients c ON a.client_id = c.id
            WHERE a.id = $1;
        """, appointment_id)
        return dict(row) if row else None


async def get_client_appointments(telegram_id: int, limit: int = 15) -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT a.*, 
                   b.name as barber_name, b.category as barber_category,
                   s.name as service_name
            FROM appointments a
            JOIN clients c ON a.client_id = c.id
            LEFT JOIN barbers b ON a.barber_id = b.id
            LEFT JOIN services s ON a.service_id = s.id
            WHERE c.telegram_id = $1
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
            LIMIT $2;
        """, telegram_id, limit)
        return [dict(r) for r in rows]


async def get_barber_appointments(barber_id: int, target_date: Optional[date] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        query = """
            SELECT a.*, s.name as service_name
            FROM appointments a
            LEFT JOIN services s ON a.service_id = s.id
            WHERE a.barber_id = $1
        """
        params = [barber_id]
        if target_date:
            params.append(target_date)
            query += f" AND a.appointment_date = ${len(params)}"
        if status:
            params.append(status)
            query += f" AND a.status = ${len(params)}"
        query += " ORDER BY a.appointment_date ASC, a.appointment_time ASC;"
        rows = await conn.fetch(query, *params)
        return [dict(r) for r in rows]


async def update_appointment_status(appointment_id: int, new_status: str, reason: Optional[str] = None) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        res = await conn.execute("""
            UPDATE appointments 
            SET status = $1, cancellation_reason = COALESCE($2, cancellation_reason)
            WHERE id = $3;
        """, new_status, reason, appointment_id)
        return "UPDATE 1" in res


async def get_barber_stats(barber_id: int) -> Dict[str, Any]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        today = date.today()
        today_clients = await conn.fetchval("""
            SELECT COUNT(*) FROM appointments 
            WHERE barber_id = $1 AND appointment_date = $2 AND status = 'completed';
        """, barber_id, today)
        
        today_income = await conn.fetchval("""
            SELECT COALESCE(SUM(total_price), 0) FROM appointments 
            WHERE barber_id = $1 AND appointment_date = $2 AND status = 'completed';
        """, barber_id, today)

        total_completed = await conn.fetchval("""
            SELECT COUNT(*) FROM appointments 
            WHERE barber_id = $1 AND status = 'completed';
        """, barber_id)

        pending_count = await conn.fetchval("""
            SELECT COUNT(*) FROM appointments 
            WHERE barber_id = $1 AND appointment_date >= $2 AND status IN ('pending', 'confirmed');
        """, barber_id, today)

        return {
            "today_clients": today_clients or 0,
            "today_income": today_income or 0,
            "total_completed": total_completed or 0,
            "pending_count": pending_count or 0
        }
