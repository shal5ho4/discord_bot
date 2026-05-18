import discord
from discord.ext import commands
from datetime import datetime

class DiscordLogger:
    def __init__(self, bot: commands.Bot, channel_id: int):
        self.bot = bot
        self.channel_id = channel_id
        print(f'self.bot: {self.bot}')
        print(f'self.channel_id: {self.channel_id}')

    @property
    def channel(self):
        return self.bot.get_channel(self.channel_id)

    def _format(self, level: str, message: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        icons = {
            "INFO": "🟢",
            "ERROR": "🔴"
        }

        icon = icons.get(level, "⚪")

        return f"{icon} [{level}] {now}\n```{message}```"

    async def info(self, message):
        await self.channel.send(
            self._format("INFO", str(message)),
            silent=True
        )

    async def error(self, message):
        await self.channel.send(
            self._format("ERROR", str(message)),
            silent=True
        )
