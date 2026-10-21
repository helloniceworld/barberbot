import logging
from datetime import datetime, date, time
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

import config
import database
import services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


# ================== PYDANTIC MODELLARI ==================

class BookingRequest(BaseModel):
    telegram_id: Optional[int] = None
    client_name: str
    client_phone: str
    client_username: Optional[str] = None
    barber_id: int
    service_ids: List[int]
    appointment_date: str  # YYYY-MM-DD
    appointment_time: str  # HH:MM


class CancelRequest(BaseModel):
    appointment_id: int
    telegram_id: Optional[int] = None


# ================== ENDPOINTLAR ==================

@router.get("/categories")
async def get_categories():
    """
    Master toifalari (Figma 'Choose your level of craft' dizayni)
    """
    return list(config.CATEGORIES.values())


@router.get("/barbers")
async def get_barbers(category: Optional[str] = Query(None)):
    """
    Ustalar ro'yxati (toifa bo'yicha filtrlash mumkin)
    """
    barbers = await database.get_barbers(category=category, active_only=True)
    return barbers


@router.get("/services")
async def get_services():
    """
    Xizmatlar ro'yxati va ularning toifalar bo'yicha narxlari
    """
    services_list = await database.get_services(active_only=True)
    return services_list


@router.get("/slots")
async def get_slots(
    barber_id: int = Query(...),
    date_str: str = Query(..., alias="date")
):
    """
    Tanlangan usta va sana uchun bo'sh vaqt slotlarini qaytaradi.
    """
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Noto'g'ri sana formati. Kerakli format: YYYY-MM-DD")

    slots = await database.get_available_slots(barber_id=barber_id, target_date=target_date)
    return {
        "barber_id": barber_id,
        "date": date_str,
        "available_slots": slots,
        "all_work_hours": config.WORK_HOURS
    }


@router.post("/book")
async def book_appointment(data: BookingRequest):
    """
    Mijoz tomonidan yangi bron qilish.
    Muvaffaqiyatli saqlangach, ustaga @culturestaffbot orqali xabar boradi!
    """
    # 1. Sanani tekshirish
    try:
        app_date = datetime.strptime(data.appointment_date, "%Y-%m-%d").date()
        app_time = datetime.strptime(data.appointment_time, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Sana yoki vaqt formati xato.")

    if app_date < date.today():
        raise HTTPException(status_code=400, detail="O'tib ketgan sanaga bron qilib bo'lmaydi.")

    # 2. Usta mavjudligini tekshirish
    barber = await database.get_barber_by_id(data.barber_id)
    if not barber or not barber['is_active']:
        raise HTTPException(status_code=404, detail="Tanlangan usta topilmadi yoki nofaol.")

    # 3. Vaqt bo'shligini tekshirish
    is_free = await database.is_slot_available(data.barber_id, app_date, app_time)
    if not is_free:
        raise HTTPException(status_code=409, detail="Kechirasiz, tanlangan vaqt allaqachon band qilingan. Boshqa vaqtni tanlang.")

    # 4. Xizmatlarni tekshirish va narxni hisoblash
    if not data.service_ids:
        raise HTTPException(status_code=400, detail="Kamida bitta xizmat tanlanishi kerak.")

    services_list = await database.get_services_by_ids(data.service_ids)
    if not services_list:
        raise HTTPException(status_code=404, detail="Tanlangan xizmatlar topilmadi.")

    cat_col = f"price_{barber['category'].lower()}"
    total_price = 0
    for srv in services_list:
        price = srv.get(cat_col) or srv.get("price_pro") or 80000
        total_price += price

    # 5. Mijozni ro'yxatga olish / yangilash
    client_id = None
    if data.telegram_id:
        client = await database.get_or_create_client(
            telegram_id=data.telegram_id,
            full_name=data.client_name,
            username=data.client_username,
            phone_number=data.client_phone
        )
        client_id = client['id']

    # 6. Appointments jadvaliga yozish
    appointment = await database.create_appointment(
        client_id=client_id,
        barber_id=data.barber_id,
        service_id=data.service_ids[0] if data.service_ids else None,
        appointment_date=app_date,
        appointment_time=app_time,
        total_price=total_price,
        client_name=data.client_name,
        client_phone=data.client_phone,
        client_username=data.client_username,
        service_ids=data.service_ids
    )

    app_id = appointment['id']
    logger.info(f"Yangi bron yaratildi: #{app_id} | Usta: {barber['name']} | Mijoz: {data.client_name}")

    # 7. Ustaga @culturestaffbot orqali xabar yuborish
    try:
        await services.notify_barber_new_booking(app_id)
    except Exception as e:
        logger.error(f"Ustaga xabar yuborishda xato: {e}")

    # 8. Mijozga @culturebarbersbot orqali kvitansiya yuborish
    try:
        await services.notify_client_new_booking(app_id)
    except Exception as e:
        logger.error(f"Mijozga kvitansiya yuborishda xato: {e}")

    return {
        "success": True,
        "message": "Bron muvaffaqiyatli qabul qilindi!",
        "appointment_id": app_id,
        "barber": barber['name'],
        "category": barber['category'],
        "date": data.appointment_date,
        "time": data.appointment_time,
        "total_price": total_price
    }


@router.get("/my-bookings")
async def get_my_bookings(telegram_id: int = Query(...)):
    """
    Mijozning o'z bronlarini olish
    """
    apps = await database.get_client_appointments(telegram_id)
    result = []
    for a in apps:
        result.append({
            "id": a['id'],
            "barber_name": a.get('barber_name'),
            "barber_category": a.get('barber_category'),
            "service_name": a.get('service_name'),
            "appointment_date": a['appointment_date'].strftime("%Y-%m-%d"),
            "appointment_time": a['appointment_time'].strftime("%H:%M"),
            "total_price": a['total_price'],
            "status": a['status']
        })
    return result


@router.post("/cancel-booking")
async def cancel_booking(data: CancelRequest):
    """
    Mijoz tomonidan bronni bekor qilish
    """
    app = await database.get_appointment_by_id(data.appointment_id)
    if not app:
        raise HTTPException(status_code=404, detail="Bron topilmadi.")

    if data.telegram_id and app.get('client_telegram_id') and app['client_telegram_id'] != data.telegram_id:
        raise HTTPException(status_code=403, detail="Siz bu bronni bekor qila olmaysiz.")

    if app['status'] == 'cancelled':
        return {"success": True, "message": "Bron allaqachon bekor qilingan."}

    await database.update_appointment_status(data.appointment_id, "cancelled", "Mijoz tomonidan bekor qilindi")

    # Ustaga bekor qilingani haqida @culturestaffbot orqali xabar berish
    try:
        await services.notify_barber_client_cancelled(data.appointment_id)
    except Exception as e:
        logger.error(f"Ustaga bekor qilish haqida xabar berishda xato: {e}")

    return {"success": True, "message": "Bron muvaffaqiyatli bekor qilindi."}
