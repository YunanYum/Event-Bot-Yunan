import os
import discord
from discord.ext import commands
from datetime import datetime

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))

async def send_realtime_log(bot, embed: discord.Embed):
    """Fungsi Helper Global untuk mengirimkan log realtime ke channel log."""
    if not LOG_CHANNEL_ID:
        print("[LOGGER WARNING] LOG_CHANNEL_ID belum diisi atau masih bernilai 0 di .env!")
        return

    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        try:
            channel = await bot.fetch_channel(LOG_CHANNEL_ID)
        except Exception as e:
            print(f"[LOGGER ERROR] Gagal mengambil channel dengan ID {LOG_CHANNEL_ID}: {e}")
            return

    try:
        await channel.send(embed=embed)
        print(f"✅ [LOGGER SUCCESS] Log '{embed.title}' berhasil dikirim ke #{channel.name}!")
    except Exception as e:
        print(f"❌ [LOGGER ERROR] Gagal mengirim log ke #{channel.name}: {e}")


class LoggerCog(commands.Cog, name="Sistem Log Realtime Khusus"):
    def __init__(self, bot):
        self.bot = bot

    # --- LISTENER EVENT REALTIME (KTP, GIVEAWAY, SAJAM, PPKM, DB) ---
    @commands.Cog.listener("on_realtime_activity")
    async def on_realtime_activity_listener(self, title: str, description: str, color: discord.Color, user: discord.User = None):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        if user:
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed.set_footer(text="Log Realtime Resmi • Kelurahan MAHA5")
        
        await send_realtime_log(self.bot, embed)

    # --- LISTENER COMMAND COMPLETION (SAJAM, PPKM, DB) ---
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.author.bot:
            return

        cmd_name = ctx.command.qualified_name if ctx.command else ""

        # 1. EVENT: Mulai Sajam (!!sajam start)
        if cmd_name == "sajam start":
            vc = ctx.author.voice.channel if ctx.author.voice else None
            vc_mention = vc.mention if vc else "Voice Channel"
            embed = discord.Embed(
                title="🎙️ SESI SAJAM DIMULAI",
                description=f"> **Host/Mod:** {ctx.author.mention}\n> **Lokasi VC:** {vc_mention}",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text="Log Realtime Resmi • Kelurahan MAHA5")
            await send_realtime_log(self.bot, embed)

        # 2. EVENT: Selesai Sajam (!!sajam end)
        elif cmd_name == "sajam end":
            embed = discord.Embed(
                title="🏁 SESI SAJAM SELESAI",
                description=f"> **Diakhiri Oleh:** {ctx.author.mention}\n> **Channel:** {ctx.channel.mention}",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text="Log Realtime Resmi • Kelurahan MAHA5")
            await send_realtime_log(self.bot, embed)

        # 3. EVENT: Memulai PPKM (!!ppkm)
        elif cmd_name == "ppkm":
            winners_count = ctx.kwargs.get("winners_count") or (ctx.args[1] if len(ctx.args) > 1 else "N/A")
            duration = ctx.kwargs.get("duration") or (ctx.args[2] if len(ctx.args) > 2 else "N/A")
            target = ctx.kwargs.get("target_channel") or ctx.channel
            
            embed = discord.Embed(
                title="🎲 EVENT PPKM DIMULAI",
                description=(
                    f"> **Penyelenggara:** {ctx.author.mention}\n"
                    f"> **Channel Target:** {target.mention}\n"
                    f"> **Jumlah Slot:** `{winners_count}` slot\n"
                    f"> **Durasi:** `{duration}`"
                ),
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text="Log Realtime Resmi • Kelurahan MAHA5")
            await send_realtime_log(self.bot, embed)

        # 4. EVENT: Backup Database (!!db backup)
        elif cmd_name == "db backup":
            embed = discord.Embed(
                title="💾 BACKUP DATABASE MANUAL",
                description=f"> **Mod/Admin:** {ctx.author.mention}\n> **Status:** Berhasil membuat cadangan SQLite.",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text="Log Realtime Resmi • Kelurahan MAHA5")
            await send_realtime_log(self.bot, embed)

        # 5. EVENT: Restore Database (!!db restore)
        elif cmd_name == "db restore":
            filename = ctx.kwargs.get("filename") or (ctx.args[1] if len(ctx.args) > 1 else "Unspecified")
            embed = discord.Embed(
                title="🔄 RESTORE DATABASE",
                description=f"> **Mod/Admin:** {ctx.author.mention}\n> **File Dipulihkan:** `{filename}`",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text="Log Realtime Resmi • Kelurahan MAHA5")
            await send_realtime_log(self.bot, embed)


async def setup(bot):
    await bot.add_cog(LoggerCog(bot))