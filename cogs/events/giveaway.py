import os
import discord
from discord.ext import commands
import asyncio
import random
import re
from datetime import datetime, timedelta
from core.database import database

def is_mod_or_admin(ctx):
    return ctx.author.guild_permissions.manage_guild

def parse_duration(duration: str) -> int:
    match = re.match(r"(\d+)([smhd])", duration.lower())
    if not match:
        raise ValueError("Format waktunya salah. Pakai 's', 'm', 'h', atau 'd'.")
    value, unit = match.groups()
    value = int(value)
    if unit == "s": return value
    if unit == "m": return value * 60
    if unit == "h": return value * 3600
    if unit == "d": return value * 86400
    raise ValueError("Unit waktu salah.")


class GiveawayJoinButton(discord.ui.Button):
    def __init__(self, message_id: int):
        super().__init__(label="Ikutan Giveaway", emoji="🎁", style=discord.ButtonStyle.blurple, custom_id=f"gw_join:{message_id}")
        self.message_id = message_id
        self._lock = asyncio.Lock()

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        if member.bot:
            return

        async with self._lock:
            participants = await database.get_giveaway_participants(self.message_id)
            if member.id in participants:
                await interaction.response.send_message("⚠️ Kamu sudah ikutan giveaway ini, tidak perlu klik lagi!", ephemeral=True)
                return

            await database.add_giveaway_participant(self.message_id, member.id)

            try:
                new_participants = await database.get_giveaway_participants(self.message_id)
                embed = interaction.message.embeds[0]
                embed.set_field_at(2, name="👥 Total Peserta", value=f"**{len(new_participants)}** orang", inline=True)
                await interaction.message.edit(embed=embed)
            except Exception:
                pass

        await interaction.response.send_message("✅ Pendaftaran sukses! Semoga beruntung di Giveaway ini!", ephemeral=True)


class GiveawaySetupModal(discord.ui.Modal, title="Buat Giveaway Baru"):
    prize_input = discord.ui.TextInput(label="Hadiah / Prize", placeholder="Contoh: Discord Nitro, Voucher, dll.", required=True)
    winners_input = discord.ui.TextInput(label="Jumlah Pemenang", placeholder="Contoh: 1 atau 3", required=True)
    duration_input = discord.ui.TextInput(label="Durasi (Waktu)", placeholder="Contoh: 30s, 10m, 2h", required=True)
    channel_input = discord.ui.TextInput(label="Channel Target (Mention atau ID)", placeholder="Contoh: #chat-room atau ID Channel", required=True)

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        prize = self.prize_input.value.strip()
        winners_raw = self.winners_input.value.strip()
        duration_raw = self.duration_input.value.strip()
        channel_raw = self.channel_input.value.strip()

        if not winners_raw.isdigit():
            await interaction.response.send_message("❌ Jumlah pemenang harus berupa angka bulat!", ephemeral=True)
            return
        winners_count = int(winners_raw)

        try:
            duration_seconds = parse_duration(duration_raw)
        except ValueError as e:
            await interaction.response.send_message(f"❌ {str(e)}", ephemeral=True)
            return

        clean_channel_id = re.sub(r"[<#>]", "", channel_raw)
        if not clean_channel_id.isdigit():
            await interaction.response.send_message("❌ Format channel salah!", ephemeral=True)
            return
        
        target_channel = interaction.guild.get_channel(int(clean_channel_id))
        if not target_channel or not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message("❌ Channel tidak ditemukan!", ephemeral=True)
            return

        await interaction.response.send_message(f"✅ Giveaway diproses ke {target_channel.mention}!", ephemeral=True)
        self.cog.bot.loop.create_task(self.cog.run_giveaway(target_channel, prize, winners_count, duration_seconds))


class GiveawaySetupView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=120.0)
        self.cog = cog

    @discord.ui.button(label="Buat Giveaway 🎁", style=discord.ButtonStyle.primary)
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Hanya staf/admin yang diperbolehkan membuat giveaway!", ephemeral=True)
            return
        await interaction.response.send_modal(GiveawaySetupModal(self.cog))


class GiveawayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.restore_persisted_giveaways())

    async def cog_check(self, ctx):
        """Memastikan perintah dapat dijalankan di channel terdaftar atau Voice Channel."""
        if isinstance(ctx.channel, (discord.VoiceChannel, discord.StageChannel)):
            return True
            
        allowed_env = os.getenv("ALLOWED_CHANNELS", "")
        if not allowed_env:
            return True

        ALLOWED_CHANNEL_IDS = {int(cid.strip()) for cid in allowed_env.split(",") if cid.strip().isdigit()}
        
        if ctx.channel.id not in ALLOWED_CHANNEL_IDS:
            allowed_mentions = " atau ".join([f"<#{cid}>" for cid in ALLOWED_CHANNEL_IDS])
            await ctx.send(
                f"⚠️ Maaf {ctx.author.mention}, perintah bot ini hanya dapat digunakan di {allowed_mentions}.", 
                delete_after=5
            )
            return False
        return True

    async def restore_persisted_giveaways(self):
        """Melanjutkan timer giveaway yang terputus saat bot restart."""
        await self.bot.wait_until_ready()
        active_gws = await database.get_active_giveaways()
        now = datetime.now()

        for msg_id, chan_id, prize, winners_count, end_time_str in active_gws:
            end_time = datetime.fromisoformat(end_time_str)
            channel = self.bot.get_channel(chan_id)
            if not channel:
                continue

            view = discord.ui.View(timeout=None)
            view.add_item(GiveawayJoinButton(msg_id))
            self.bot.add_view(view, message_id=msg_id)

            remaining = (end_time - now).total_seconds()
            self.bot.loop.create_task(self.handle_giveaway_timer(msg_id, channel, prize, winners_count, max(0, remaining), view))

        if active_gws:
            print(f"📡 [Giveaway Persistence] Memulihkan {len(active_gws)} event giveaway aktif.")

    @commands.command(name="giveaway")
    @commands.check(is_mod_or_admin)
    async def setup_giveaway(self, ctx):
        embed = discord.Embed(
            title="🎁 Pembuat Giveaway Interaktif 🎁",
            description="Klik tombol di bawah untuk membuka form pembuatan Giveaway baru.",
            color=discord.Color.from_rgb(224, 170, 170)
        )
        await ctx.send(embed=embed, view=GiveawaySetupView(self))

    async def run_giveaway(self, target_channel: discord.TextChannel, prize: str, winners_count: int, duration_seconds: int):
        end_time = datetime.now() + timedelta(seconds=duration_seconds)
        
        embed = discord.Embed(
            title="🎉 EVENT GIVEAWAY DIMULAI! 🎉",
            description=f"Tekan tombol **Ikutan Giveaway** di bawah ini untuk berpartisipasi!\n\nDitutup <t:{int(end_time.timestamp())}:R>",
            color=discord.Color.from_rgb(224, 170, 170)
        )
        embed.add_field(name="🎁 Hadiah", value=f"**{prize}**", inline=True)
        embed.add_field(name="🏆 Pemenang", value=f"**{winners_count}** orang", inline=True)
        embed.add_field(name="👥 Total Peserta", value="**0** orang", inline=True)
        embed.set_footer(text="Semoga beruntung!")

        placeholder_view = discord.ui.View(timeout=None)
        giveaway_msg = await target_channel.send(embed=embed, view=placeholder_view)

        await database.save_giveaway(giveaway_msg.id, target_channel.id, prize, winners_count, end_time.isoformat())

        view = discord.ui.View(timeout=None)
        join_button = GiveawayJoinButton(giveaway_msg.id)
        view.add_item(join_button)
        await giveaway_msg.edit(view=view)

        self.bot.dispatch(
            "realtime_activity",
            "🎁 EVENT GIVEAWAY DIMULAI",
            f"> **Channel Target:** {target_channel.mention}\n"
            f"> **Hadiah:** `{prize}`\n"
            f"> **Jumlah Pemenang:** `{winners_count}` Orang\n"
            f"> **Durasi:** `{duration_seconds} detik`",
            discord.Color.gold()
        )

        self.bot.loop.create_task(self.handle_giveaway_timer(giveaway_msg.id, target_channel, prize, winners_count, float(duration_seconds), view))

    async def handle_giveaway_timer(self, msg_id: int, channel: discord.TextChannel, prize: str, winners_count: int, duration_seconds: float, view: discord.ui.View):
        if duration_seconds > 0:
            await asyncio.sleep(duration_seconds)

        await database.end_giveaway_db(msg_id)

        for item in view.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
                item.label = "Giveaway Selesai"
                item.style = discord.ButtonStyle.grey

        try:
            msg = await channel.fetch_message(msg_id)
            p_ids = await database.get_giveaway_participants(msg_id)
            embed = msg.embeds[0]
            embed.set_field_at(2, name="👥 Total Peserta", value=f"**{len(p_ids)}** orang (Selesai)", inline=True)
            await msg.edit(embed=embed, view=view)
        except Exception:
            p_ids = await database.get_giveaway_participants(msg_id)

        eligible_users = []
        for uid in p_ids:
            m = channel.guild.get_member(uid)
            if not m:
                try: m = await channel.guild.fetch_member(uid)
                except Exception: continue
            if m: eligible_users.append(m)

        if not eligible_users:
            await channel.send(f"😭 Giveaway **{prize}** telah selesai, tetapi tidak ada peserta yang terdaftar.")
            return

        winners = random.sample(eligible_users, min(winners_count, len(eligible_users)))
        winner_mentions = ", ".join([w.mention for w in winners])

        announce_embed = discord.Embed(
            title="🎊 PEMENANG GIVEAWAY 🎊",
            description=f"Selamat buat para pemenang giveaway **{prize}**! 🎉\n\n**Daftar Pemenang:**\n{winner_mentions}",
            color=discord.Color.from_rgb(173, 204, 173)
        )
        await channel.send(content=f"📢 Selamat {winner_mentions} Telah memenangkan Giveaway!", embed=announce_embed)


async def setup(bot):
    await bot.add_cog(GiveawayCog(bot))