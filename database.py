import logging
import random
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
                loyalty_points INT DEFAULT 15000,
                loyalty_tier VARCHAR(50) DEFAULT 'BRONZE',
                total_spent INT DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await conn.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS loyalty_points INT DEFAULT 15000;")
        await conn.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS loyalty_tier VARCHAR(50) DEFAULT 'BRONZE';")
        await conn.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS total_spent INT DEFAULT 0;")
        await conn.execute("UPDATE clients SET loyalty_points = 15000 WHERE loyalty_points IS NULL;")
        await conn.execute("UPDATE clients SET loyalty_tier = 'BRONZE' WHERE loyalty_tier IS NULL;")

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
                points_used INT DEFAULT 0,
                discount_amount INT DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS total_price INT DEFAULT 0;")
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS service_ids INT[] DEFAULT '{}';")
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS client_name VARCHAR(255);")
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS client_phone VARCHAR(50);")
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS client_username VARCHAR(255);")
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS cancellation_reason TEXT;")
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS points_used INT DEFAULT 0;")
        await conn.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS discount_amount INT DEFAULT 0;")

        # 5. loyalty_rewards jadvali (Vosk, moy, bepul muolajalar)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_rewards (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                points_cost INT NOT NULL,
                category VARCHAR(50) DEFAULT 'product',
                icon VARCHAR(50) DEFAULT '🎁',
                is_active BOOLEAN DEFAULT TRUE
            );
        """)

        # 6. loyalty_transactions jadvali (Ballar kirim-chiqim tarixi)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_transactions (
                id SERIAL PRIMARY KEY,
                client_id INT REFERENCES clients(id) ON DELETE CASCADE,
                points INT NOT NULL,
                type VARCHAR(50) NOT NULL,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 7. loyalty_redemptions jadvali (Mijoz olgan sovg'alar va promokodlar)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_redemptions (
                id SERIAL PRIMARY KEY,
                client_id INT REFERENCES clients(id) ON DELETE CASCADE,
                reward_id INT REFERENCES loyalty_rewards(id) ON DELETE SET NULL,
                reward_name VARCHAR(255) NOT NULL,
                points_spent INT NOT NULL,
                code VARCHAR(50) UNIQUE NOT NULL,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Unikal faol bron indeksi
        await conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_booking 
            ON appointments (barber_id, appointment_date, appointment_time) 
            WHERE status != 'cancelled';
        """)

        # Boshlang'ich ustalar
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

        # Boshlang'ich xizmatlar
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

        # Boshlang'ich sovg'alar (Vosk, moy, bepul xizmatlar)
        r_count = await conn.fetchval("SELECT COUNT(*) FROM loyalty_rewards;")
        if r_count == 0:
            default_rewards = [
                ("Premium Soch Voski (Hairstyle Matte Wax)", "Kuchli fiksatsiya va tabiiy mat effekt beruvchi original vosk", 25000, "product", "💈"),
                ("Hashamatli Soqol Moyi (Luxury Beard Oil)", "Soqolni yumshatuvchi va o'stiruvchi vitaminli tabiiy moy", 20000, "product", "🧴"),
                ("VIP Yuz Spa & Qora Maska muolajasi", "Yuz terisini chuqur tozalovchi qora maska va yuz massaji", 18000, "service", "🧖‍♂️"),
                ("Qosh va Quloq detallash (Waxing)", "Issiq mum bilan ortiqcha tuklarni tozalash va qosh shakllantirish", 12000, "service", "✂️"),
                ("Culture Brand Metall Taroq", "Maxsus g'ilofli, zanglamas po'latdan Culture VIP brend taroq", 10000, "accessory", "👑")
            ]
            for r_name, r_desc, r_cost, r_cat, r_icon in default_rewards:
                await conn.execute("""
                    INSERT INTO loyalty_rewards (name, description, points_cost, category, icon, is_active)
                    VALUES ($1, $2, $3, $4, $5, TRUE);
                """, r_name, r_desc, r_cost, r_cat, r_icon)

    logger.info("Ma'lumotlar bazasi jadvallari va Sodiqlik dasturi tayyor.")


# ================== CLIENT FUNCTIONS ==================

async def get_or_create_client(telegram_id: int, full_name: Optional[str] = None, username: Optional[str] = None, phone_number: Optional[str] = None) -> Dict[str, Any]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT * FROM clients WHERE telegram_id = $1;", telegram_id)
        if existing:
            row = await conn.fetchrow("""
                UPDATE clients
                SET full_name = COALESCE($2, full_name),
                    username = COALESCE($3, username),
                    phone_number = COALESCE($4, phone_number)
                WHERE telegram_id = $1
                RETURNING *;
            """, telegram_id, full_name, username, phone_number)
            return dict(row)
        else:
            # Yangi mijoz uchun 15 000 ball Welcome Bonusi
            row = await conn.fetchrow("""
                INSERT INTO clients (telegram_id, full_name, username, phone_number, loyalty_points, loyalty_tier)
                VALUES ($1, $2, $3, $4, 15000, 'BRONZE')
                RETURNING *;
            """, telegram_id, full_name, username, phone_number)
            client_dict = dict(row)
            # Welcome transaction
            await conn.execute("""
                INSERT INTO loyalty_transactions (client_id, points, type, description)
                VALUES ($1, 15000, 'welcome_bonus', 'Culture Club ga xush kelibsiz bonusi!');
            """, client_dict['id'])
            return client_dict


async def get_client_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM clients WHERE telegram_id = $1;", telegram_id)
        return dict(row) if row else None


# ================== SODIQLIK DASTURI (LOYALTY SYSTEM) ==================

async def get_loyalty_profile(telegram_id: int) -> Dict[str, Any]:
    """
    Mijozning sodiqlik klubi profili, ballari, statusi va tarixi
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        client = await conn.fetchrow("SELECT * FROM clients WHERE telegram_id = $1;", telegram_id)
        if not client:
            return {
                "points": 15000,
                "tier": "BRONZE",
                "tier_name": "Bronze Member",
                "cashback_rate": 5,
                "total_spent": 0,
                "transactions": [],
                "active_redemptions": []
            }

        client_id = client['id']
        points = client['loyalty_points'] or 0
        total_spent = client['total_spent'] or 0

        # Tier hisoblash
        if points >= 150000 or total_spent >= 2000000:
            tier = "GOLD"
            tier_name = "Gold VIP Member"
            cashback_rate = 10
        elif points >= 50000 or total_spent >= 800000:
            tier = "SILVER"
            tier_name = "Silver Member"
            cashback_rate = 7
        else:
            tier = "BRONZE"
            tier_name = "Bronze Member"
            cashback_rate = 5

        # Ballar tarixi
        tx_rows = await conn.fetch("""
            SELECT * FROM loyalty_transactions
            WHERE client_id = $1
            ORDER BY created_at DESC
            LIMIT 10;
        """, client_id)

        transactions = []
        for r in tx_rows:
            transactions.append({
                "id": r['id'],
                "points": r['points'],
                "type": r['type'],
                "description": r['description'],
                "created_at": r['created_at'].strftime("%d.%m.%Y %H:%M")
            })

        # Faol olingan sovg'alar
        red_rows = await conn.fetch("""
            SELECT * FROM loyalty_redemptions
            WHERE client_id = $1 AND status = 'active'
            ORDER BY created_at DESC;
        """, client_id)

        redemptions = []
        for r in red_rows:
            redemptions.append({
                "id": r['id'],
                "reward_name": r['reward_name'],
                "code": r['code'],
                "points_spent": r['points_spent'],
                "status": r['status'],
                "created_at": r['created_at'].strftime("%d.%m.%Y %H:%M")
            })

        return {
            "client_id": client_id,
            "full_name": client['full_name'],
            "points": points,
            "tier": tier,
            "tier_name": tier_name,
            "cashback_rate": cashback_rate,
            "total_spent": total_spent,
            "transactions": transactions,
            "active_redemptions": redemptions
        }


async def get_loyalty_rewards() -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM loyalty_rewards WHERE is_active = TRUE ORDER BY points_cost ASC;")
        return [dict(r) for r in rows]


async def redeem_reward(telegram_id: int, reward_id: int) -> Dict[str, Any]:
    """
    Ballarni sovg'aga (masalan: Vosk, moy) almashtirish
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        client = await conn.fetchrow("SELECT * FROM clients WHERE telegram_id = $1;", telegram_id)
        if not client:
            raise ValueError("Mijoz topilmadi.")

        reward = await conn.fetchrow("SELECT * FROM loyalty_rewards WHERE id = $1 AND is_active = TRUE;", reward_id)
        if not reward:
            raise ValueError("Bunday sovg'a mavjud emas.")

        cost = reward['points_cost']
        if (client['loyalty_points'] or 0) < cost:
            raise ValueError(f"Yetarli ball mavjud emas. Kerak: {cost:,} ball, sizda: {client['loyalty_points']:,} ball.")

        # Ballni ayirish
        new_points = client['loyalty_points'] - cost
        await conn.execute("UPDATE clients SET loyalty_points = $1 WHERE id = $2;", new_points, client['id'])

        # Promokod generatsiya (masalan: #GIFT-7492)
        code = f"GIFT-{random.randint(1000, 9999)}"

        # Redemptions ga qo'shish
        red = await conn.fetchrow("""
            INSERT INTO loyalty_redemptions (client_id, reward_id, reward_name, points_spent, code, status)
            VALUES ($1, $2, $3, $4, $5, 'active')
            RETURNING *;
        """, client['id'], reward_id, reward['name'], cost, code)

        # Tranzaksiya yozish
        await conn.execute("""
            INSERT INTO loyalty_transactions (client_id, points, type, description)
            VALUES ($1, $2, 'reward_redeemed', $3);
        """, client['id'], -cost, f"'{reward['name']}' sovg'asiga almashtirildi (Kod: {code})")

        return {
            "success": True,
            "code": code,
            "reward_name": reward['name'],
            "points_spent": cost,
            "remaining_points": new_points
        }


async def add_loyalty_points(client_id: int, points: int, tx_type: str, description: str) -> int:
    """
    Mijozga ball qo'shish (keshbek yoki bonus)
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        client = await conn.fetchrow("SELECT * FROM clients WHERE id = $1;", client_id)
        if not client:
            return 0
        new_balance = (client['loyalty_points'] or 0) + points
        await conn.execute("UPDATE clients SET loyalty_points = $1 WHERE id = $2;", new_balance, client_id)
        await conn.execute("""
            INSERT INTO loyalty_transactions (client_id, points, type, description)
            VALUES ($1, $2, $3, $4);
        """, client_id, points, tx_type, description)
        return new_balance


async def deduct_loyalty_points(client_id: int, points: int, tx_type: str, description: str) -> int:
    """
    Mijozdan ball ayirish (chegirma sifatida ishlatilganda)
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        client = await conn.fetchrow("SELECT * FROM clients WHERE id = $1;", client_id)
        if not client:
            return 0
        cur = client['loyalty_points'] or 0
        deduct_val = min(cur, points)
        new_balance = cur - deduct_val
        await conn.execute("UPDATE clients SET loyalty_points = $1 WHERE id = $2;", new_balance, client_id)
        await conn.execute("""
            INSERT INTO loyalty_transactions (client_id, points, type, description)
            VALUES ($1, $2, $3, $4);
        """, client_id, -deduct_val, tx_type, description)
        return new_balance


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
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT appointment_time 
            FROM appointments 
            WHERE barber_id = $1 
              AND appointment_date = $2 
              AND status != 'cancelled';
        """, barber_id, target_date)
        
        booked_times = {r['appointment_time'].strftime("%H:%M") for r in rows}
        
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
    service_ids: Optional[List[int]] = None,
    points_used: int = 0,
    discount_amount: int = 0
) -> Dict[str, Any]:
    pool = await get_pool()
    if service_ids is None:
        service_ids = [service_id] if service_id else []

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO appointments (
                client_id, barber_id, service_id, service_ids, total_price,
                appointment_date, appointment_time, status,
                client_name, client_phone, client_username,
                points_used, discount_amount
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending', $8, $9, $10, $11, $12)
            RETURNING *;
        """, client_id, barber_id, service_id, service_ids, total_price,
           appointment_date, appointment_time, client_name, client_phone, client_username,
           points_used, discount_amount)
        
        # Agar ball ishlatilgan bo'lsa, mijozdan ayirish
        if points_used > 0 and client_id:
            await deduct_loyalty_points(
                client_id=client_id,
                points=points_used,
                tx_type="discount_used",
                description=f"#{row['id']} bron uchun {points_used:,} ball chegirmaga ishlatildi"
            )

        return dict(row)


async def get_appointment_by_id(appointment_id: int) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT a.*, 
                   b.name as barber_name, b.category as barber_category, b.telegram_id as barber_telegram_id,
                   s.name as service_name,
                   c.telegram_id as client_telegram_id, c.loyalty_points as client_loyalty_points
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
        old_app = await conn.fetchrow("SELECT * FROM appointments WHERE id = $1;", appointment_id)
        if not old_app:
            return False

        res = await conn.execute("""
            UPDATE appointments 
            SET status = $1, cancellation_reason = COALESCE($2, cancellation_reason)
            WHERE id = $3;
        """, new_status, reason, appointment_id)

        # Xizmat ko'rsatib tugatilganda (completed) mijozga keshbek berish
        if new_status == 'completed' and old_app['status'] != 'completed' and old_app['client_id']:
            total = old_app['total_price'] or 0
            if total > 0:
                # 5% keshbek
                cashback = int(total * 0.05)
                if cashback > 0:
                    await add_loyalty_points(
                        client_id=old_app['client_id'],
                        points=cashback,
                        tx_type="cashback",
                        description=f"#{appointment_id} tashrif uchun 5% keshbek"
                    )
                    # total_spent yangilash
                    await conn.execute("""
                        UPDATE clients SET total_spent = COALESCE(total_spent, 0) + $1 WHERE id = $2;
                    """, total, old_app['client_id'])

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
