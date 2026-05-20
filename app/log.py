import os
import platform
import psutil
import shutil
from discord.ext import commands
from datetime import datetime

class DiscordLogger:
    def __init__(self, bot: commands.Bot, channel_id: int):
        self.bot = bot
        self.channel_id = channel_id

    @property
    def channel(self):
        return self.bot.get_channel(self.channel_id)

    def _format(self, level: str, message: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        icons = {
            "INFO": "🟢",
            "ERROR": "🔴",
            "SYSTEM": "🔵"
        }
        icon = icons.get(level, "⚪")

        if level == "ERROR":
            return f"<@840937804238422016>\n{icon} [{level}] {now}\n```{message}```"
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

    async def system(self):
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        disk = shutil.disk_usage("/")

        message = (
            f"OS: {platform.system()} {platform.release()}\n"
            f"CPU: {cpu}%\n"
            f"MEMORY: {mem.percent}% "
            f"({mem.used // 1024**2}MB / {mem.total // 1024**2}MB)\n"
            f"DISK: {disk.used // 1024**3}GB / "
            f"{disk.total // 1024**3}GB "
            f"({disk.used / disk.total * 100:.1f}%)\n"
            f"PID: {os.getpid()}"
        )

        await self.channel.send(
            self._format("SYSTEM", message),
            silent=True
        )
