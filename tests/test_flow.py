import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import datetime
import config
import database

async def run_tests():
    print("--- 1. Testing Database Initialization ---")
    await database.init_db(config.DATABASE_URL)
    print("DB initialized successfully.")

    print("\n--- 2. Testing Barbers Retrieval ---")
    barbers = await database.get_barbers()
    print(f"Total active barbers: {len(barbers)}")
    for b in barbers:
        print(f"  [{b['category']}] {b['name']} (rating: {b['rating']}, exp: {b['experience_years']}y, TG: {b['telegram_id']})")

    print("\n--- 3. Testing Services Retrieval ---")
    services = await database.get_services()
    print(f"Total services: {len(services)}")
    for s in services:
        print(f"  {s['name']}: PRO={s['price_pro']}, TOP={s['price_top']}, VIP={s['price_vip']}, BRAND={s.get('price_brand', 250000)}")

    print("\n--- 4. Testing Slots Availability ---")
    test_barber = barbers[0]
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    slots = await database.get_available_slots(test_barber['id'], tomorrow)
    print(f"Available slots tomorrow for {test_barber['name']}: {slots}")
    assert len(slots) > 0, "Slots should not be empty"

    print("\n--- 5. Testing Booking Creation ---")
    client = await database.get_or_create_client(
        telegram_id=999888777,
        full_name="Test Mijoz",
        username="test_mijoz",
        phone_number="+998901112233"
    )
    print("Client created/retrieved:", client['id'], client['full_name'])

    test_time = datetime.time(14, 0)
    app = await database.create_appointment(
        client_id=client['id'],
        barber_id=test_barber['id'],
        service_id=services[0]['id'],
        appointment_date=tomorrow,
        appointment_time=test_time,
        total_price=120000,
        client_name="Test Mijoz",
        client_phone="+998901112233",
        client_username="test_mijoz",
        service_ids=[services[0]['id']]
    )
    print(f"Created appointment #{app['id']}, status: {app['status']}")
    assert app['status'] == 'pending'

    print("\n--- 6. Verifying Slot is Now Busy ---")
    new_slots = await database.get_available_slots(test_barber['id'], tomorrow)
    print("14:00 should not be in available slots:", "14:00" not in new_slots)
    assert "14:00" not in new_slots

    print("\n--- 7. Testing Barber Accept Action ---")
    ok = await database.update_appointment_status(app['id'], 'confirmed')
    print("Status updated to confirmed:", ok)
    updated_app = await database.get_appointment_by_id(app['id'])
    assert updated_app['status'] == 'confirmed'

    print("\n--- 8. Testing Barber Complete Action ---")
    ok = await database.update_appointment_status(app['id'], 'completed')
    print("Status updated to completed:", ok)

    print("\n--- 9. Testing Barber Stats ---")
    stats = await database.get_barber_stats(test_barber['id'])
    print(f"Barber stats for {test_barber['name']}:", stats)

    print("\n--- 10. Cleaning Up Test Data ---")
    pool = await database.get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM appointments WHERE id = $1;", app['id'])
        await conn.execute("DELETE FROM clients WHERE telegram_id = 999888777;")
    print("Test appointment and client cleaned up.")

    await pool.close()
    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == '__main__':
    asyncio.run(run_tests())
