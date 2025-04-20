import discord
import asyncio
import time

from settings import *


intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

    try:
        for guild in client.guilds:
            print(f"\n📚 Server: {guild.name}")
            for category in guild.categories:
                print(f"📁 {category.name}")
                for channel in category.channels:
                    if isinstance(channel, discord.VoiceChannel):
                        print(f"  🔊 {channel.name}")
                    else:
                        print(f"  📝 {channel.name}")
                    

                    overwrites = channel.overwrites
                    for target, perms in overwrites.items():
                        if isinstance(target, discord.Role):
                            name = f"@{target.name}"
                        elif isinstance(target, discord.Member):
                            name = target.name
                        else:
                            # fallback for unknown/deleted role/user
                            name = f"(unknown:{target.id})"

                        allowed = [p for p, v in perms if v is True]
                        denied = [p for p, v in perms if v is False]

                        if allowed:
                            print(f"    ✅ {name} allowed: {', '.join(allowed)}")
                        if denied:
                            print(f"    ❌ {name} denied: {', '.join(denied)}")
                    print()
                    time.sleep(0.5)
    except Exception as e:
        print(repr(e))
    finally:
        await client.close()

async def main():
    await client.start(BOT_TOKEN_CHANNEL_MANAGE)

asyncio.run(main())
