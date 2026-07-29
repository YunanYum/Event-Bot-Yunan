import os
import discord
from discord.ext import commands
import random
import asyncio
import re
from datetime import datetime, timedelta
from core.database import database
from typing import Union, Optional, Set

THEME_COLOR = discord.Color.from_rgb(214, 204, 224)
SUCCESS_COLOR = discord.Color.from_rgb(173, 204, 173)
ERROR_COLOR = discord.Color.from_rgb(224, 170, 170)

EXCLUDED_ROLE_ID = int(os.getenv("EXCLUDED_ROLE_ID", "0"))

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

def create_bot_embed(title: str, description: str, color: discord.Color):
    return discord.Embed(title=title, description=description, color=color)

async def send_error(ctx, message):
    embed = create_bot_embed("Yah, Gagal 😥", message, ERROR_COLOR)
    await ctx.send(f"{ctx.author.mention}", embed=embed, delete_after=15)

async def send_confirmation(ctx, message, title="Sip, Berhasil! 👍", view=None):
    embed = create_bot_embed(title, message, SUCCESS_COLOR)
    await ctx.send(embed=embed, delete_after=60 if view else 10, view=view)


# --- UI COMPONENTS 1: Sistem Tombol Gacha ---

class GachaButton(discord.ui.Button):
    def __init__(self, target_channel, cog):
        super().__init__(label="Ikutan Gacha", emoji="🎟️", style=discord.ButtonStyle.green)
        self.target_channel = target_channel
        self.cog = cog
        self.participants = set()  
        self.members_map = {}   
        self._lock = asyncio.Lock() 

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        if member.bot:
            return

        async with self._lock:
            if member.id in self.cog.BLACKLISTED_USERS:
                await interaction.response.send_message(
                    "❌ Maaf, kamu tidak bisa ikut gacha karena akunmu masuk dalam daftar cekal (user blacklist).", 
                    ephemeral=True
                )
                return

            user_role_ids = {role.id for role in member.roles}
            if EXCLUDED_ROLE_ID in user_role_ids:
                await interaction.response.send_message(
                    "❌ Maaf, peran (role) kamu saat ini dikecualikan dari sistem gacha.", 
                    ephemeral=True
                )
                return

            if self.cog.WHITELISTED_ROLES:
                if not (user_role_ids & self.cog.WHITELISTED_ROLES):
                    await interaction.response.send_message(
                        "❌ Maaf, gacha ini hanya khusus bagi pemilik peran (role) tertentu saja.", 
                        ephemeral=True
                    )
                    return
            elif self.cog.BLACKLISTED_ROLES:
                if user_role_ids & self.cog.BLACKLISTED_ROLES:
                    await interaction.response.send_message(
                        "❌ Maaf, peran (role) kamu dilarang mengikuti gacha ini.", 
                        ephemeral=True
                    )
                    return

            if member.id in self.participants:
                await interaction.response.send_message(
                    "⚠️ Tenang, kamu sudah terdaftar di gacha ini. Tidak perlu menekan tombol lagi!", 
                    ephemeral=True
                )
                return

            self.participants.add(member.id)
            self.members_map[member.id] = member
            await database.increment_event_stat(member.id, 'ppkm')            

            # --- UPDATE EMBED SECARA REAL-TIME ---
            try:
                embed = interaction.message.embeds[0]
                embed.set_field_at(1, name="👥 Total Peserta", value=f"**{len(self.participants)}** orang", inline=True)
                await interaction.message.edit(embed=embed)
            except Exception:
                pass

        success_msg = "✅ Kamu berhasil terdaftar dalam gacha ini!"
        if isinstance(self.target_channel, (discord.VoiceChannel, discord.StageChannel)):
            success_msg += f"\n⚠️ **Catatan Penting:** Kamu wajib terhubung ke Voice/Stage Channel {self.target_channel.mention} saat waktu gacha habis agar bisa menang!"

        await interaction.response.send_message(success_msg, ephemeral=True)
        


class GachaView(discord.ui.View):
    def __init__(self, target_channel, cog, timeout: float):
        super().__init__(timeout=timeout)
        self.gacha_button = GachaButton(target_channel, cog)
        self.add_item(self.gacha_button)


# --- UI COMPONENTS 2: Modals Formulir & Panel Konfigurasi ---

class ConfigUserModal(discord.ui.Modal, title="Kelola Blacklist User"):
    user_input = discord.ui.TextInput(
        label="User ID", 
        placeholder="Ketik 18-19 digit ID User...",
        min_length=15,
        max_length=22,
        required=True
    )
    
    def __init__(self, cog, config_message):
        super().__init__()
        self.cog = cog
        self.config_message = config_message

    async def on_submit(self, interaction: discord.Interaction):
        val = self.user_input.value.strip()
        if not val.isdigit():
            await interaction.response.send_message("❌ ID User harus berupa angka!", ephemeral=True)
            return
        
        user_id = int(val)
        if user_id in self.cog.BLACKLISTED_USERS:
            self.cog.BLACKLISTED_USERS.discard(user_id)
            action = "dihapus dari"
        else:
            self.cog.BLACKLISTED_USERS.add(user_id)
            action = "ditambahkan ke"
        
        await self.cog._save_all_configs()
        await self.cog.update_config_embed(self.config_message)
        await interaction.response.send_message(f"✅ User ID `{user_id}` berhasil {action} blacklist!", ephemeral=True)


class ConfigRoleBlacklistModal(discord.ui.Modal, title="Kelola Blacklist Role"):
    role_input = discord.ui.TextInput(
        label="Role ID", 
        placeholder="Ketik 18-19 digit ID Role...",
        min_length=15,
        max_length=22,
        required=True
    )
    
    def __init__(self, cog, config_message):
        super().__init__()
        self.cog = cog
        self.config_message = config_message

    async def on_submit(self, interaction: discord.Interaction):
        val = self.role_input.value.strip()
        if not val.isdigit():
            await interaction.response.send_message("❌ ID Role harus berupa angka!", ephemeral=True)
            return
        
        role_id = int(val)
        if role_id in self.cog.BLACKLISTED_ROLES:
            self.cog.BLACKLISTED_ROLES.discard(role_id)
            action = "dihapus dari"
        else:
            self.cog.BLACKLISTED_ROLES.add(role_id)
            action = "ditambahkan ke"
        
        await self.cog._save_all_configs()
        await self.cog.update_config_embed(self.config_message)
        await interaction.response.send_message(f"✅ Role ID `{role_id}` berhasil {action} blacklist!", ephemeral=True)


class ConfigRoleWhitelistModal(discord.ui.Modal, title="Kelola Whitelist Role"):
    role_input = discord.ui.TextInput(
        label="Role ID", 
        placeholder="Ketik 18-19 digit ID Role...",
        min_length=15,
        max_length=22,
        required=True
    )
    
    def __init__(self, cog, config_message):
        super().__init__()
        self.cog = cog
        self.config_message = config_message

    async def on_submit(self, interaction: discord.Interaction):
        val = self.role_input.value.strip()
        if not val.isdigit():
            await interaction.response.send_message("❌ ID Role harus berupa angka!", ephemeral=True)
            return
        
        role_id = int(val)
        if role_id in self.cog.WHITELISTED_ROLES:
            self.cog.WHITELISTED_ROLES.discard(role_id)
            action = "dihapus dari"
        else:
            self.cog.WHITELISTED_ROLES.add(role_id)
            action = "ditambahkan ke"
        
        await self.cog._save_all_configs()
        await self.cog.update_config_embed(self.config_message)
        await interaction.response.send_message(f"✅ Role ID `{role_id}` berhasil {action} whitelist!", ephemeral=True)


class ConfigView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=180.0)
        self.cog = cog
        self.message = None

    @discord.ui.button(label="Kelola User Blacklist", emoji="👤", style=discord.ButtonStyle.secondary)
    async def manage_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ConfigUserModal(self.cog, self.message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Kelola Role Blacklist", emoji="🚫", style=discord.ButtonStyle.secondary)
    async def manage_role_blacklist(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ConfigRoleBlacklistModal(self.cog, self.message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Kelola Role Whitelist", emoji="✅", style=discord.ButtonStyle.secondary)
    async def manage_role_whitelist(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ConfigRoleWhitelistModal(self.cog, self.message)
        await interaction.response.send_modal(modal)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except Exception:
            pass


# --- COG MAIN CLASS ---

class PPKMCog(commands.Cog, name="Manajemen Event PPKM"):
    def __init__(self, bot):
        self.bot = bot
        self.BLACKLISTED_ROLES = set()
        self.WHITELISTED_ROLES = set()
        self.BLACKLISTED_USERS = set()
        
        self.last_pool = [] 
        self.last_winners = [] 
        self.last_target_channel = None

    async def cog_check(self, ctx):
        """Memastikan semua perintah di Cog ini hanya bisa dijalankan di channel terdaftar."""
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

    async def cog_load(self):
        """Setup asinkron saat cog dimuat."""
        await self.load_data()

    async def load_data(self):
        """Memuat role dan user blacklist dari database SQLite terpusat."""
        self.BLACKLISTED_ROLES, self.WHITELISTED_ROLES = await database.load_roles_config()
        self.BLACKLISTED_USERS = await database.load_user_blacklist()

    async def _save_all_configs(self):
        """Menyimpan semua konfigurasi ke database SQLite terpusat."""
        await database.save_roles_config(self.BLACKLISTED_ROLES, self.WHITELISTED_ROLES)
        await database.save_user_blacklist(self.BLACKLISTED_USERS)

    async def update_config_embed(self, message: discord.Message):
        """Fungsi khusus untuk merefresh isi embed konfigurasi di Discord secara real-time."""
        b_roles = ", ".join([f"<@&{r}>" for r in self.BLACKLISTED_ROLES]) or "Kosong"
        w_roles = ", ".join([f"<@&{r}>" for r in self.WHITELISTED_ROLES]) or "Kosong"
        b_users = ", ".join([f"<@{u}>" for u in self.BLACKLISTED_USERS]) or "Kosong"

        embed = create_bot_embed(
            "⚙️ Konfigurasi PPKM", 
            "Berikut daftar filter aktif saat ini.\nAdmin dapat klik tombol di bawah untuk mengelola data via popup formulir.", 
            THEME_COLOR
        )
        embed.add_field(name="🚫 Blacklisted Roles", value=b_roles, inline=True)
        embed.add_field(name="✅ Whitelisted Roles", value=w_roles, inline=True)
        embed.add_field(name="👤 Blacklisted Users", value=b_users, inline=False)
        embed.add_field(name="⚠️ Global Excluded Role (Sistem)", value=f"<@&{EXCLUDED_ROLE_ID}>", inline=False)
        
        try:
            await message.edit(embed=embed)
        except Exception:
            pass

    async def _process_and_announce_winners(self, ctx: commands.Context, winners: list, target_channel: discord.abc.GuildChannel, is_reroll=False):
        """Fungsi terpusat untuk mengumumkan pemenang."""
        title = "🔄 Reroll Pemenang PPKM 🔄" if is_reroll else "🌟 Pemenang Gacha PPKM 🌟"
        winner_mentions = "\n".join([f"🏆 {winner.mention}" for winner in winners])
        
        description = (
            f"Selamat buat para pemenang {'baru ' if is_reroll else ''}yang dapet slot event! 🎉\n\n"
            "**Pemenang:**\n"
            f"{winner_mentions}"
        )
        
        final_embed = create_bot_embed(title, description, SUCCESS_COLOR)
        
        pings = " ".join([winner.mention for winner in winners])
        announcement_text = f"📢 {pings} Selamat! Kamu memenangkan slot PPKM! 🎉"
        
        await target_channel.send(content=announcement_text, embed=final_embed)

        talent_cog = self.bot.get_cog("Manajemen Golden Buzzer")
        talent_status_message = ""
        if talent_cog:
            talent_cog.setup_session(winners, target_channel)
            talent_status_message = f"\n\n✅ Sesi Golden Buzzer diupdate!"

        winner_list_admin = "\n".join([f"• {winner.mention} (`{winner.name}`)" for winner in winners])
        report_title = "👑 Laporan Reroll PPKM 👑" if is_reroll else "👑 Laporan Pemenang Gacha PPKM 👑"
        final_embed_admin = create_bot_embed(report_title, f"Daftar pemenang terbaru.{talent_status_message}", SUCCESS_COLOR)
        final_embed_admin.add_field(name="Pemenang Aktif", value=winner_list_admin, inline=False)
        await ctx.send(embed=final_embed_admin)

    @commands.command()
    @commands.check(is_mod_or_admin)
    async def ppkm(self, ctx, winners_count: int, duration: str, *, target_channel: Optional[Union[discord.TextChannel, discord.VoiceChannel, discord.StageChannel]] = None):
        """Mulai gacha slot buat event PPKM."""
        await self.load_data()
        target_channel = target_channel or ctx.channel
        
        async with ctx.typing():
            try:
                duration_in_seconds = parse_duration(duration)
            except ValueError as e:
                return await send_error(ctx, str(e))
        
        end_time = datetime.now() + timedelta(seconds=duration_in_seconds)
        embed = create_bot_embed(
            "🎲 Yuk, Ikutan Gacha Slot Event PPKM! 🎲",
            f"Gas, tekan tombol **Ikutan Gacha** di bawah untuk berpartisipasi!\n\nUndian ditutup <t:{int(end_time.timestamp())}:R>",
            THEME_COLOR
        )
        
        embed.add_field(name="🏆 Slot Tersedia", value=f"**{winners_count}** slot", inline=True)
        embed.add_field(name="👥 Total Peserta", value="**0** orang", inline=True)
        
        view = GachaView(target_channel, self, timeout=float(duration_in_seconds))
        
        try:
            gacha_message = await target_channel.send(embed=embed, view=view)
        except discord.Forbidden:
            return await send_error(ctx, "Bot tidak punya izin di channel tersebut.")
        
        await send_confirmation(ctx, f"Gacha dimulai di {target_channel.mention}.")
        
        await asyncio.sleep(duration_in_seconds)

        view.stop()
        for item in view.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
                item.label = "Gacha Selesai"
                item.style = discord.ButtonStyle.grey
        
        participants_ids = view.gacha_button.participants
        
        try:
            embed = gacha_message.embeds[0]
            embed.set_field_at(1, name="👥 Total Peserta", value=f"**{len(participants_ids)}** orang (Selesai)", inline=True)
            await gacha_message.edit(embed=embed, view=view)
        except Exception:
            pass

        eligible_users = []

        for uid in participants_ids:
            member = view.gacha_button.members_map.get(uid)
            if not member:
                member = ctx.guild.get_member(uid)
            if not member: 
                continue

            if isinstance(target_channel, (discord.VoiceChannel, discord.StageChannel)):
                if not member.voice or member.voice.channel != target_channel:
                    continue

            eligible_users.append(member)
        
        if not eligible_users:
            return await target_channel.send("Gacha selesai, tapi tidak ada peserta yang memenuhi syarat.")

        winners = random.sample(eligible_users, min(winners_count, len(eligible_users)))
        
        self.last_pool = eligible_users
        self.last_winners = winners
        self.last_target_channel = target_channel

        await self._process_and_announce_winners(ctx, winners, target_channel)

    @commands.command()
    @commands.check(is_mod_or_admin)
    async def reroll(self, ctx, members: commands.Greedy[discord.Member] = None):
        """Reroll satu atau semua pemenang dari gacha terakhir."""
        await self.load_data()
        if not self.last_pool:
            return await send_error(ctx, "Data gacha terakhir kosong.")

        valid_pool = [
            m for m in self.last_pool 
            if m.id not in self.BLACKLISTED_USERS and EXCLUDED_ROLE_ID not in {role.id for role in m.roles}
        ]

        if not members:
            self.last_winners = random.sample(valid_pool, min(len(self.last_winners), len(valid_pool)))
            await ctx.send("🔄 Melakukan reroll untuk semua pemenang...")
        else:
            new_winners = list(self.last_winners)
            for target in members:
                if target in new_winners:
                    potential = [m for m in valid_pool if m not in new_winners]
                    if potential:
                        replacement = random.choice(potential)
                        new_winners.remove(target)
                        new_winners.append(replacement)
            self.last_winners = new_winners

        await self._process_and_announce_winners(ctx, self.last_winners, self.last_target_channel, is_reroll=True)

    # --- Manajemen Blacklist User (Teks Command Alternatif) ---
    @commands.command()
    @commands.check(is_mod_or_admin)
    async def userblacklist(self, ctx, user: discord.User):
        """Blokir user agar tidak bisa ikut/menang gacha."""
        self.BLACKLISTED_USERS.add(user.id)
        await self._save_all_configs()
        await send_confirmation(ctx, f"User {user.mention} berhasil di-blacklist.")

    @commands.command()
    @commands.check(is_mod_or_admin)
    async def userunblacklist(self, ctx, user: discord.User):
        """Hapus user dari daftar blacklist."""
        self.BLACKLISTED_USERS.discard(user.id)
        await self._save_all_configs()
        await send_confirmation(ctx, f"User {user.mention} telah dihapus dari blacklist.")

    # --- Manajemen Role (Blacklist/Whitelist Teks Command Alternatif) ---
    @commands.command()
    @commands.check(is_mod_or_admin)
    async def blacklist(self, ctx, role: discord.Role):
        self.BLACKLISTED_ROLES.add(role.id)
        await self._save_all_configs()
        await send_confirmation(ctx, f"Role {role.mention} di-blacklist.")

    @commands.command()
    @commands.check(is_mod_or_admin)
    async def unblacklist(self, ctx, role: discord.Role):
        self.BLACKLISTED_ROLES.discard(role.id)
        await self._save_all_configs()
        await send_confirmation(ctx, f"Role {role.mention} dihapus dari blacklist.")

    @commands.command()
    @commands.check(is_mod_or_admin)
    async def whitelist(self, ctx, role: discord.Role):
        self.WHITELISTED_ROLES.add(role.id)
        await self._save_all_configs()
        await send_confirmation(ctx, f"Role {role.mention} di-whitelist.")

    @commands.command()
    @commands.check(is_mod_or_admin)
    async def unwhitelist(self, ctx, role: discord.Role):
        self.WHITELISTED_ROLES.discard(role.id)
        await self._save_all_configs()
        await send_confirmation(ctx, f"Role {role.mention} dihapus dari whitelist.")

    # --- Interactive Config Panel ---
    @commands.command(name="ppkmconfig")
    @commands.check(is_mod_or_admin)
    async def ppkm_config(self, ctx):
        """Melihat settingan gacha saat ini via panel interaktif."""
        b_roles = ", ".join([f"<@&{r}>" for r in self.BLACKLISTED_ROLES]) or "Kosong"
        w_roles = ", ".join([f"<@&{r}>" for r in self.WHITELISTED_ROLES]) or "Kosong"
        b_users = ", ".join([f"<@{u}>" for u in self.BLACKLISTED_USERS]) or "Kosong"

        embed = create_bot_embed(
            "⚙️ Konfigurasi PPKM", 
            "Berikut daftar filter aktif saat ini.\nAdmin dapat klik tombol di bawah untuk mengelola data via popup formulir.", 
            THEME_COLOR
        )
        embed.add_field(name="🚫 Blacklisted Roles", value=b_roles, inline=True)
        embed.add_field(name="✅ Whitelisted Roles", value=w_roles, inline=True)
        embed.add_field(name="👤 Blacklisted Users", value=b_users, inline=False)
        embed.add_field(name="⚠️ Global Excluded Role (Sistem)", value=f"<@&{EXCLUDED_ROLE_ID}>", inline=False)
        
        view = ConfigView(self)
        message = await ctx.send(embed=embed, view=view)
        view.message = message

async def setup(bot):
    await bot.add_cog(PPKMCog(bot))