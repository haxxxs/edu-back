import asyncio
from tortoise import Tortoise
from app.core.security import get_password_hash
from app.core.config import TORTOISE_ORM
from app.models.user import User, UserRole

# Настройки админского аккаунта
ADMIN_EMAIL = "admin@admin.ru"
ADMIN_PASSWORD = "ghjhjr11"
ADMIN_NAME = "Администратор"

async def create_admin_user():
    """Создает или обновляет админского пользователя"""
    print("Подключаемся к базе данных...")
    await Tortoise.init(config=TORTOISE_ORM)
    
    # Проверяем, существует ли уже админ с этим email
    admin = await User.get_or_none(email=ADMIN_EMAIL)
    
    if admin:
        # Если админ существует, проверяем флаг is_admin
        if not admin.is_admin:
            admin.is_admin = True
            admin.role = UserRole.ADMIN
            await admin.save()
            print(f"Пользователь {ADMIN_EMAIL} обновлен до администратора")
        else:
            print(f"Пользователь {ADMIN_EMAIL} уже является администратором")
    else:
        # Создаем нового админа
        hashed_password = get_password_hash(ADMIN_PASSWORD)
        admin = await User.create(
            email=ADMIN_EMAIL,
            name=ADMIN_NAME,
            hashed_password=hashed_password,
            is_admin=True,
            role=UserRole.ADMIN
        )
        print(f"Создан новый администратор с email {ADMIN_EMAIL}")
    
    print("Операция завершена успешно")
    await Tortoise.close_connections()

if __name__ == "__main__":
    print("Запускаем создание/обновление админского аккаунта...")
    asyncio.run(create_admin_user())
    print("Готово!") 