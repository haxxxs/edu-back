import asyncio
from app.models.user import User
from app.core.security import get_password_hash
from tortoise import Tortoise
from app.core.config import TORTOISE_ORM

async def create_admin():
    # Initialize database
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    # Check if admin already exists
    admin_user = await User.get_or_none(email="admin@admin.ru")
    
    if admin_user:
        # Update existing admin with real telegram_id
        admin_user.telegram_id = "1887055490"  # Real telegram ID
        await admin_user.save()
        print(f"✅ Admin user updated! Email: admin@admin.ru, Telegram ID: {admin_user.telegram_id}")
    else:
        # Create new admin
        admin_user = await User.create(
            name="Administrator",
            email="admin@admin.ru",
            hashed_password=get_password_hash("ghjhjr11"),
            is_admin=True,
            is_active=True,
            telegram_id="1887055490"  # Real telegram ID
        )
        print(f"✅ Admin user created! Email: admin@admin.ru, Telegram ID: {admin_user.telegram_id}")

    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(create_admin()) 