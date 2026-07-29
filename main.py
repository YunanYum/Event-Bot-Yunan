import discord
from discord.ext import commands, tasks
import asyncio
import os
import random
from datetime import datetime
from dotenv import load_dotenv
from core.safety import setup_error_logging, send_error_to_channel

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("DISCORD_PREFIX", "!!")

if not TOKEN:
    raise ValueError("ERROR: Token Bot tidak ditemukan di file .env!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

@tasks.loop(minutes=5)
async def change_status():
    status_list = [
        discord.Activity(type=discord.ActivityType.watching, name="Event PPKM Di MAHA5 Discord"),
        discord.Activity(type=discord.ActivityType.listening, name="!!help di Backstage"),
        discord.Activity(type=discord.ActivityType.playing, name="Kocok Slot Gacha")
    ]
    await bot.change_presence(activity=random.choice(status_list))

@bot.event
async def on_ready():
    change_status.start()
    if not hasattr(bot, 'start_time'):
        bot.start_time = datetime.now()

    print(f'=== BOT TELAH ONLINE ===')
    print(f'Username : {bot.user.name}')
    print(f'Prefix   : {PREFIX}')
    print(f'========================')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CheckFailure):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Kamu tidak memiliki izin untuk menggunakan perintah ini!", delete_after=5)
        return

    await send_error_to_channel(bot, error, ctx=ctx)
    print(f"[COMMAND ERROR in {ctx.command}] {error}")

@bot.event
async def on_error(event_name, *args, **kwargs):
    import sys
    error_type, error_val, error_tb = sys.exc_info()
    if error_val:
        await send_error_to_channel(bot, error_val, event_name=event_name)
    print(f"[EVENT ERROR in {event_name}] {error_val}")

async def load_extensions():
    try:
        # 1. Module Event & Undian (cogs/events)
        await bot.load_extension('cogs.events.ppkm')
        await bot.load_extension('cogs.events.giveaway')

        # 2. Module Panggung Musik & Voice (cogs/stage)
        await bot.load_extension('cogs.stage.sajam')
        await bot.load_extension('cogs.stage.karaoke')

        # 3. Module Warga, KTP & Ekonomi (cogs/citizen)
        await bot.load_extension('cogs.citizen.ktp')
        await bot.load_extension('cogs.citizen.misi')
        await bot.load_extension('cogs.citizen.economy')
        await bot.load_extension('cogs.citizen.job')

        # 4. Module Sistem & Admin (cogs/system)
        await bot.load_extension('cogs.system.admin')
        await bot.load_extension('cogs.system.help')
        await bot.load_extension('cogs.system.logger')

        print("✨ Seluruh ekstensi (Cogs) berhasil dimuat dengan struktur baru!")
    except Exception as e:
        print(f"❌ Gagal memuat ekstensi: {e}")

async def main():
    try:
        async with bot:
            await load_extensions()
            await bot.start(TOKEN)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    setup_error_logging()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot Sudah Dimatikan")