import os
import discord
from discord.ext import commands
from datetime import datetime

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))

async def send_realtime_log(bot, embed: discord.Embed):
    if not LOG_CHANNEL_ID: return

    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        try: channel = await bot.fetch_channel(LOG_CHANNEL_ID)
        except Exception: return

    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"[REALTIME LOGGER ERROR] {e}")


class LoggerCog(commands.Cog, name="Sistem Log Realtime"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.modal_submit: return

        data = interaction.data or {}
        title = data.get("title", "")

        values = []
        if "components" in data:
            for row in data["components"]:
                for comp in row.get("components", []):
                    values.append(comp.get("value", "").strip())

        # Log Giveaway
        if "Buat Giveaway" in title and len(values) >= 4:
            prize, winners, duration, target_channel = values[0], values[1], values[2], values[3]
            embed = discord.Embed(
                title="🎁 EVENT GIVEAWAY DIMULAI",
                description=(
                    f"> **Penyelenggara:** {interaction.user.mention}\n"
                    f"> **Hadiah:** `{prize}`\n"
                    f"> **Jumlah Pemenang:** `{winners}` orang\n"
                    f"> **Durasi:** `{duration}`\n"
                    f"> **Channel Target:** `{target_channel}`"
                ),
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text="Log Realtime Resmi • Event Bot Yunan")
            await send_realtime_log(self.bot, embed)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.author.bot: return
        cmd_name = ctx.command.qualified_name if ctx.command else ""

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
            embed.set_footer(text="Log Realtime Resmi • Event Bot Yunan")
            await send_realtime_log(self.bot, embed)

        elif cmd_name == "sajam end":
            embed = discord.Embed(
                title="🏁 SESI SAJAM SELESAI",
                description=f"> **Diakhiri Oleh:** {ctx.author.mention}\n> **Channel:** {ctx.channel.mention}",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text="Log Realtime Resmi • Event Bot Yunan")
            await send_realtime_log(self.bot, embed)

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
            embed.set_footer(text="Log Realtime Resmi • Event Bot Yunan")
            await send_realtime_log(self.bot, embed)

        elif cmd_name == "db backup":
            embed = discord.Embed(
                title="💾 BACKUP DATABASE MANUAL",
                description=f"> **Mod/Admin:** {ctx.author.mention}\n> **Status:** Berhasil membuat cadangan SQLite.",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text="Log Realtime Resmi • Event Bot Yunan")
            await send_realtime_log(self.bot, embed)

        elif cmd_name == "db restore":
            filename = ctx.kwargs.get("filename") or (ctx.args[1] if len(ctx.args) > 1 else "Unspecified")
            embed = discord.Embed(
                title="🔄 RESTORE DATABASE",
                description=f"> **Mod/Admin:** {ctx.author.mention}\n> **File Dipulihkan:** `{filename}`",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text="Log Realtime Resmi • Event Bot Yunan")
            await send_realtime_log(self.bot, embed)


async def setup(bot):
    await bot.add_cog(LoggerCog(bot))