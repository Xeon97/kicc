
from telethon import events
from datetime import datetime, timedelta

from .. import loader, utils


@loader.tds
class KickInactiveMod(loader.Module):
    """Кикает пользователей, которые не писали в чат указанное количество дней"""

    strings = {"name": "KickInactive"}

    async def client_ready(self, client, db):
        self.client = client

    @loader.command()
    async def kikat(self, message):
        """Использование: %kikat <количество дней> [ID чата]"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("Укажите количество дней и опционально ID чата: %kikat <дней> [ID чата]")
            return

        args = args.split()
        if len(args) < 1 or not args[0].isdigit():
            await message.edit("Укажите корректное количество дней: %kikat <дней> [ID чата]")
            return

        days = int(args[0])
        chat_id = None

        if len(args) > 1:  # Если указан ID чата
            try:
                chat_id = int(args[1])
            except ValueError:
                await message.edit("ID чата должно быть числом.")
                return
        else:  # Если ID чата не указан, используем текущий чат
            chat = await message.get_chat()
            chat_id = chat.id

        await message.edit(f"Проверяю пользователей в чате {chat_id}, которые не писали {days} дней...")
        threshold_date = datetime.now() - timedelta(days=days)
        kicked = 0

        async for user in self.client.iter_participants(chat_id):
            if user.bot or user.deleted:
                continue

            async for msg in self.client.iter_messages(chat_id, from_user=user.id, limit=1):
                if msg.date and msg.date >= threshold_date:
                    break
            else:
                try:
                    await self.client.kick_participant(chat_id, user.id)
                    kicked += 1
                except Exception as e:
                    await message.reply(f"Не удалось кикнуть {user.id}: {e}")

        await message.edit(f"Кикнуто пользователей: {kicked}.")
