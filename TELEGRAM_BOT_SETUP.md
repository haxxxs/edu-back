# Настройка Telegram Бота

## Шаг 1: Создание бота в Telegram

1. Найдите в Telegram бота [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Введите название для вашего бота (например: "Edu Platform Notifications")
4. Введите username для бота (должен заканчиваться на "bot", например: "edu_platform_notifications_bot")
5. BotFather пришлет вам токен бота - сохраните его!

## Шаг 2: Настройка переменных окружения

Добавьте в ваш `.env` файл:

```env
# Telegram settings
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username
```

Замените `your_bot_token_here` на токен, полученный от BotFather.

## Шаг 3: Настройка команд бота (опционально)

Вы можете настроить команды для бота через BotFather:

1. Отправьте `/setcommands` BotFather'у
2. Выберите ваш бот
3. Отправьте список команд:

```
start - Начать работу с ботом
help - Получить справку
```

## Шаг 4: Получение своего Telegram ID

Для тестирования вам нужно знать ваш Telegram ID. Есть несколько способов:

### Способ 1: Через username

Если у вас есть username (например, @yourusername), используйте его при регистрации.

### Способ 2: Через бота

1. Найдите бота [@userinfobot](https://t.me/userinfobot)
2. Отправьте ему команду `/start`
3. Он пришлет ваш числовой ID

## Шаг 5: Тестирование

1. Запустите ваш сервер
2. Зарегистрируйтесь на платформе, указав ваш Telegram ID или username
3. Создайте календарную заметку
4. Проверьте, что уведомление пришло в Telegram

## Примеры Telegram ID

- Username: `@yourusername`
- Числовой ID: `123456789`

## Возможные проблемы

1. **"Chat not found"** - пользователь должен сначала написать боту (команда `/start`)
2. **"Unauthorized"** - проверьте токен бота
3. **"Bad Request"** - проверьте формат Telegram ID

## Полезные команды для тестирования

Вы можете добавить эти эндпоинты для тестирования:

```python
@router.post("/test-telegram")
async def test_telegram_notification(
    telegram_id: str,
    message: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Test sending Telegram notification (admin only)"""
    success = await telegram_service.send_message(telegram_id, message)
    return {"success": success}
```
