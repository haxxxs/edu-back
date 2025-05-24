import asyncio
import logging
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from app.core.config import settings

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        """Initialize Telegram service with bot token"""
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
    async def send_message(self, telegram_id: str, message: str) -> bool:
        """
        Send a generic message to a Telegram user
        
        Args:
            telegram_id: User's Telegram ID (username with @ or numeric ID)
            message: Message text to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            # Remove @ symbol if present
            clean_id = telegram_id.lstrip('@')
            
            # Try to convert to int if it's numeric, otherwise use as username
            try:
                chat_id = int(clean_id)
            except ValueError:
                chat_id = f"@{clean_id}"
            
            await self.bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"Message sent successfully to {telegram_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to send message to {telegram_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message to {telegram_id}: {e}")
            return False
    
    async def send_calendar_notification(
        self, 
        telegram_id: str, 
        note_title: str, 
        note_date: str, 
        note_description: Optional[str] = None,
        notification_type: str = "created"
    ) -> bool:
        """
        Send a calendar note notification
        
        Args:
            telegram_id: User's Telegram ID
            note_title: Title of the calendar note
            note_date: Date/time of the note
            note_description: Optional description
            notification_type: Type of notification (created, updated, deleted, reminder)
            
        Returns:
            bool: True if notification was sent successfully
        """
        try:
            # Determine emoji and action text based on notification type
            notification_configs = {
                "created": {"emoji": "📅", "action": "создана", "color": "✅"},
                "updated": {"emoji": "✏️", "action": "обновлена", "color": "🔄"},
                "deleted": {"emoji": "🗑️", "action": "удалена", "color": "❌"},
                "reminder": {"emoji": "⏰", "action": "напоминание", "color": "🔔"},
                "upcoming": {"emoji": "⏰", "action": "скоро начнется", "color": "🔔"}
            }
            
            config = notification_configs.get(notification_type, notification_configs["created"])
            
            # Create formatted message
            message_parts = [
                f"{config['color']} {config['emoji']} Заметка календаря {config['action']}!",
                "",
                f"📋 **{note_title}**",
                f"📆 {note_date}"
            ]
            
            if note_description:
                message_parts.extend([
                    "",
                    f"📝 {note_description}"
                ])
            
            # Add footer based on notification type
            if notification_type == "reminder":
                message_parts.extend([
                    "",
                    "⏰ Не забудьте про это событие!"
                ])
            elif notification_type == "upcoming":
                message_parts.extend([
                    "",
                    "🎯 Событие скоро начнется!"
                ])
            elif notification_type == "created":
                message_parts.extend([
                    "",
                    "✨ Новая заметка успешно добавлена в ваш календарь!"
                ])
            
            message = "\n".join(message_parts)
            
            return await self.send_message(telegram_id, message)
            
        except Exception as e:
            logger.error(f"Failed to send calendar notification to {telegram_id}: {e}")
            return False
    
    async def send_daily_reminder(self, telegram_id: str, notes_count: int, upcoming_notes: list) -> bool:
        """
        Send daily reminder with upcoming notes
        
        Args:
            telegram_id: User's Telegram ID
            notes_count: Number of notes for today
            upcoming_notes: List of upcoming notes
            
        Returns:
            bool: True if reminder was sent successfully
        """
        try:
            if notes_count == 0:
                message = "🌅 Доброе утро!\n\nУ вас нет запланированных событий на сегодня. Хорошего дня! 😊"
            else:
                message_parts = [
                    "🌅 Доброе утро!",
                    "",
                    f"📅 У вас {notes_count} событий на сегодня:",
                    ""
                ]
                
                for i, note in enumerate(upcoming_notes[:5], 1):  # Show max 5 notes
                    time_str = note.get('time', 'Время не указано')
                    message_parts.append(f"{i}. {note['title']} - {time_str}")
                
                if len(upcoming_notes) > 5:
                    message_parts.append(f"... и еще {len(upcoming_notes) - 5} событий")
                
                message_parts.extend([
                    "",
                    "✨ Желаем продуктивного дня!"
                ])
                
                message = "\n".join(message_parts)
            
            return await self.send_message(telegram_id, message)
            
        except Exception as e:
            logger.error(f"Failed to send daily reminder to {telegram_id}: {e}")
            return False
    
    async def send_note_reminder(self, telegram_id: str, note_title: str, note_date: str, minutes_before: int = 30) -> bool:
        """
        Send reminder before note time
        
        Args:
            telegram_id: User's Telegram ID
            note_title: Title of the note
            note_date: Date/time of the note
            minutes_before: Minutes before the event
            
        Returns:
            bool: True if reminder was sent successfully
        """
        try:
            message = f"""⏰ Напоминание!

📋 **{note_title}**
📆 {note_date}

🔔 До события осталось {minutes_before} минут!
Подготовьтесь заранее. 😊"""
            
            return await self.send_message(telegram_id, message)
            
        except Exception as e:
            logger.error(f"Failed to send note reminder to {telegram_id}: {e}")
            return False

# Create a global instance
telegram_service = TelegramService() 