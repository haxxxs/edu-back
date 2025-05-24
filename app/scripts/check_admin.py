import asyncio
from tortoise import Tortoise
from app.core.config import TORTOISE_ORM
from app.models.user import User

async def check_admin():
    """Проверяет, существует ли админ в базе данных"""
    print("Подключаемся к базе данных...")
    await Tortoise.init(config=TORTOISE_ORM)
    
    # Ищем админа
    admin = await User.get_or_none(email="admin@admin.ru")
    
    if admin:
        print(f"✅ Админ найден:")
        print(f"   ID: {admin.id}")
        print(f"   Email: {admin.email}")
        print(f"   Name: {admin.name}")
        print(f"   Is Admin: {admin.is_admin}")
        print(f"   Is Active: {admin.is_active}")
        print(f"   Role: {admin.role}")
        print(f"   Telegram ID: {admin.telegram_id}")
        print(f"   Created: {admin.created_at}")
    else:
        print("❌ Админ НЕ найден в базе данных!")
    
    # Проверим всех пользователей
    all_users = await User.all()
    print(f"\n📊 Всего пользователей в базе: {len(all_users)}")
    
    for user in all_users:
        print(f"   - {user.email} (Admin: {user.is_admin})")
    
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(check_admin()) 