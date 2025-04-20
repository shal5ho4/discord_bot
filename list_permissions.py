import discord
import asyncio

from settings import *

intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

    for guild in client.guilds:
        print(f"\n📚 Server: {guild.name}")
        for category in guild.categories:
            print(f"📁 {category.name}")
            for channel in category.channels:
                print(f"  📝 {channel.name}")

                overwrites = channel.overwrites
                for target, perms in overwrites.items():
                    allowed = [name for name, value in perms if value is True]
                    denied = [name for name, value in perms if value is False]
                    name = f"@{target.name}" if isinstance(target, discord.Role) else target.name

                    if allowed:
                        print(f"    ✅ {name} allowed: {', '.join(allowed)}")
                    if denied:
                        print(f"    ❌ {name} denied: {', '.join(denied)}")
                print()

    await client.close()

async def main():
    await client.start(BOT_TOKEN_CHANNEL_MANAGE)

asyncio.run(main())