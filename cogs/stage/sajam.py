# sajam.py

import discord
from discord.ext import commands
import asyncio
import random
from datetime import datetime
from typing import Optional, Union
from core.database import database 

# Warna Tema Embed
THEME_COLOR = discord.Color.from_rgb(214, 204, 224)
SUCCESS_COLOR = discord.Color.from_rgb(173, 204, 173)

def is_mod_or_admin(ctx):
    return ctx.author.guild_permissions.manage_guild

def get_random_thanks(member_mention: str) -> str:
    """Fungsi pengacak ucapan terima kasih kasual setelah selesai tampil."""
    phrases = [
        f"Gila parah, panggungnya langsung pecah gara-gara {member_mention}! You absolutely killed it! 🔥",
        f"Sumpah {member_mention}, merinding banget denger suaranya! Makasih banyak ya udah tampil!",
        f"What a legendary performance, {member_mention}! Makasih udah bikin panggung jadi rame banget!",
        f"Speechless gua! Sheesh {member_mention}, gokil abis suaranya!",
        f"Kasih applause yang paling meriah dulu buat {member_mention}! Mantap abis!",
        f"Apresiasi penuh buat {member_mention} yang udah nyumbang suara indahnya hari ini ✨",
        f"Gokil {member_mention}! Suaramu bikin satu Discord langsung terpana saking indahnya!",
        f"Otsukaresama desu {member_mention}! Suaramu emang sugoi banget hari ini!",
        f"Arigatou gozaimasu {member_mention}! Keren parah penampilannya, no debat!",
        f"Sugoi {member_mention}! Makasih banyak ya udah mampir dan bernyanyi di panggung utama 🎶"
    ]
    return random.choice(phrases)

# --- UI COMPONENTS 1: Tombol Antrean (Member Actions) ---

class SajamJoinButton(discord.ui.Button):
    def __init__(self, cog):
        super().__init__(label="Join Antrian", emoji="🎟️", style=discord.ButtonStyle.green)
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        if not self.cog.is_active:
            await interaction.response.send_message("❌ Sesi Sajam sedang tidak aktif!", ephemeral=True)
            return

        if not self.cog.queue_open:
            await interaction.response.send_message("❌ Pendaftaran antrean sedang ditutup oleh moderator!", ephemeral=True)
            return

        member = interaction.user
        
        if member.id in [m.id for m in self.cog.queue] or (self.cog.current_performer and self.cog.current_performer.id == member.id):
            await interaction.response.send_message("⚠️ Kamu sudah berada di dalam antrian atau sedang aktif tampil!", ephemeral=True)
            return

        if not self.cog.current_performer:
            self.cog.current_performer = member
            await self.cog.persist_state()
            await self.cog.update_queue_embeds(interaction)
            await interaction.followup.send(
                f"🎙️ {member.mention} langsung naik ke panggung!", 
                delete_after=10
            )
        else:
            self.cog.queue.append(member)
            if len(self.cog.queue) > self.cog.peak_queue:
                self.cog.peak_queue = len(self.cog.queue)
            await self.cog.persist_state()
            await self.cog.update_queue_embeds(interaction)
            await interaction.response.send_message("✅ Berhasil bergabung ke dalam antrian!", ephemeral=True)


class SajamLeaveButton(discord.ui.Button):
    def __init__(self, cog):
        super().__init__(label="Keluar Antrian", emoji="🚪", style=discord.ButtonStyle.red)
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        if not self.cog.is_active:
            await interaction.response.send_message("❌ Sesi Sajam sedang tidak aktif!", ephemeral=True)
            return

        member = interaction.user

        if self.cog.current_performer and self.cog.current_performer.id == member.id:
            self.cog.current_performer = None
            if self.cog.queue:
                self.cog.current_performer = self.cog.queue.pop(0)
            await self.cog.persist_state()
            await self.cog.update_queue_embeds(interaction)
            await interaction.response.send_message("🚪 Kamu memilih untuk turun dari panggung.", ephemeral=True)
            return

        in_queue = False
        for m in self.cog.queue:
            if m.id == member.id:
                self.cog.queue.remove(m)
                in_queue = True
                break

        if in_queue:
            await self.cog.persist_state()
            await self.cog.update_queue_embeds(interaction)
            await interaction.response.send_message("🚪 Berhasil keluar dari daftar antrian!", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Kamu tidak terdaftar di dalam antrian saat ini.", ephemeral=True)


class SajamDoneButton(discord.ui.Button):
    def __init__(self, cog):
        super().__init__(label="Selesai Tampil", emoji="✅", style=discord.ButtonStyle.blurple)
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        if not self.cog.is_active:
            await interaction.response.send_message("❌ Sesi Sajam sedang tidak aktif!", ephemeral=True)
            return

        member = interaction.user

        if not self.cog.current_performer or self.cog.current_performer.id != member.id:
            await interaction.response.send_message("❌ Eits, tombol ini hanya dapat digunakan oleh orang yang **Sedang Tampil**!", ephemeral=True)
            return

        self.cog.sing_count[member.id] = self.cog.sing_count.get(member.id, 0) + 1

        self.cog.current_performer = None
        if self.cog.queue:
            self.cog.current_performer = self.cog.queue.pop(0)

        await self.cog.persist_state()
        await self.cog.update_queue_embeds(interaction)
        
        thanks_msg = get_random_thanks(member.mention)
        next_performer = self.cog.current_performer
        
        if next_performer:
            await interaction.followup.send(
                f"🎉 {thanks_msg}\n👉 Giliran {next_performer.mention} naik panggung! 🎙️",
                delete_after=10
            )
        else:
            await interaction.followup.send(
                f"🎉 {thanks_msg}\n💤 Saat ini panggung kosong.",
                delete_after=10
            )


# --- UI COMPONENTS 2: Dropdown Menu Host & Moderator ---

class SajamModSelect(discord.ui.Select):
    def __init__(self, cog):
        options = [
            discord.SelectOption(label="Paksa Turun Member", description="Turunkan penyanyi saat ini tanpa mencatat giliran.", emoji="🛑", value="force_remove"),
            discord.SelectOption(label="Paksa Lanjut Antrian", description="Selesaikan giliran saat ini dan panggil antrian berikutnya.", emoji="⏩", value="force_next"),
            discord.SelectOption(label="Tutup Pendaftaran", description="Kunci pendaftaran agar member baru tidak bisa bergabung.", emoji="🔒", value="close_registration"),
            discord.SelectOption(label="Buka Pendaftaran", description="Buka kembali pendaftaran agar member bisa bergabung.", emoji="🔓", value="open_registration"),
            discord.SelectOption(label="Selesai Sajam", description="Akhiri seluruh sesi Sajam dan tampilkan laporan statistik.", emoji="🏁", value="end_sajam")
        ]
        super().__init__(placeholder="⚙️ Menu Host & Moderator", min_values=1, max_values=1, options=options)
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Hanya Host & Moderator yang dapat menggunakan menu ini!", ephemeral=True)
            return

        value = self.values[0]

        if value == "force_remove":
            if not self.cog.current_performer:
                await interaction.response.send_message("⚠️ Sedang tidak ada member yang tampil saat ini.", ephemeral=True)
                return
            
            old_member = self.cog.current_performer
            self.cog.current_performer = None
            if self.cog.queue:
                self.cog.current_performer = self.cog.queue.pop(0)
            
            await self.cog.persist_state()
            await self.cog.update_queue_embeds(interaction)
            await interaction.followup.send(
                f"⚠️ Moderator memaksa {old_member.mention} turun panggung.",
                delete_after=10
            )

        elif value == "force_next":
            if not self.cog.current_performer:
                await interaction.response.send_message("⚠️ Sedang tidak ada member yang tampil saat ini.", ephemeral=True)
                return
            
            old_member = self.cog.current_performer
            self.cog.sing_count[old_member.id] = self.cog.sing_count.get(old_member.id, 0) + 1
            
            self.cog.current_performer = None
            if self.cog.queue:
                self.cog.current_performer = self.cog.queue.pop(0)
            
            await self.cog.persist_state()
            await self.cog.update_queue_embeds(interaction)
            
            thanks_msg = get_random_thanks(old_member.mention)
            next_mention = self.cog.current_performer.mention if self.cog.current_performer else "Kosong"
            
            await interaction.followup.send(
                f"⏩ {thanks_msg}\n👉 Giliran berikutnya: {next_mention}!",
                delete_after=10
            )

        elif value == "close_registration":
            if not self.cog.queue_open:
                await interaction.response.send_message("⚠️ Pendaftaran antrean memang sudah ditutup.", ephemeral=True)
                return
            
            self.cog.queue_open = False
            await self.cog.persist_state()
            await self.cog.update_queue_embeds(interaction)
            await interaction.followup.send(
                "🔒 **Pendaftaran antrean telah ditutup oleh moderator!** Member baru tidak bisa bergabung untuk sementara.",
                delete_after=10
            )

        elif value == "open_registration":
            if self.cog.queue_open:
                await interaction.response.send_message("⚠️ Pendaftaran antrean memang sudah terbuka.", ephemeral=True)
                return
            
            self.cog.queue_open = True
            await self.cog.persist_state()
            await self.cog.update_queue_embeds(interaction)
            await interaction.followup.send(
                "🔓 **Pendaftaran antrean telah dibuka kembali oleh moderator!** Silakan bergabung.",
                delete_after=10
            )

        elif value == "end_sajam":
            await interaction.response.defer()
            await self.cog.end_sajam_session(interaction)


# --- UI COMPONENTS 3: View Pembungkus Komponen ---

class SajamView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
        self.add_item(SajamJoinButton(cog))
        self.add_item(SajamLeaveButton(cog))
        self.add_item(SajamDoneButton(cog))
        self.add_item(SajamModSelect(cog))


# --- COG MAIN CLASS ---

class SajamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_active = False
        self.queue_open = True       
        self.voice_channel = None
        self.current_performer = None
        self.queue = []
        
        self.sing_count = {}         
        self.vc_participants = set()  
        self.peak_visitors = 0       
        self.peak_queue = 0          
        self.start_time = None
        self.active_message = None

        self.bot.loop.create_task(self.restore_persisted_state())

    async def restore_persisted_state(self):
        """Membaca SQLite untuk memulihkan sesi panggung aktif jika bot restart."""
        await self.bot.wait_until_ready()
        
        session = await database.load_sajam_session()
        if not session or not session[0]: 
            return
            
        self.is_active = True
        self.queue_open = bool(session[1])
        
        vc_id = session[2]
        if vc_id:
            self.voice_channel = self.bot.get_channel(vc_id)
            
        perf_id = session[3]
        if perf_id and self.voice_channel:
            guild = self.voice_channel.guild
            self.current_performer = guild.get_member(perf_id)
            if not self.current_performer:
                try:
                    self.current_performer = await guild.fetch_member(perf_id)
                except Exception:
                    pass
                    
        start_time_str = session[4]
        if start_time_str:
            self.start_time = datetime.fromisoformat(start_time_str)
        self.peak_visitors = session[5]
        self.peak_queue = session[6]
        msg_id = session[7]
        msg_chan_id = session[8]
        if msg_id and msg_chan_id:
            channel = self.bot.get_channel(msg_chan_id)
            if channel:
                try:
                    self.active_message = await channel.fetch_message(msg_id)
                except Exception:
                    pass

        queue_ids = await database.load_sajam_queue()
        self.queue = []
        if self.voice_channel:
            guild = self.voice_channel.guild
            for uid in queue_ids:
                member = guild.get_member(uid)
                if not member:
                    try:
                        member = await guild.fetch_member(uid)
                    except Exception:
                        continue
                if member:
                    self.queue.append(member)
                    
        self.sing_count = await database.load_sajam_sing_count()
        self.vc_participants = await database.load_sajam_vc_participants()
        
        print(f"📡 [Sajam Persistence] Sesi panggung aktif berhasil dipulihkan di {self.voice_channel} ({len(self.queue)} orang mengantre).")

    async def persist_state(self):
        """Helper untuk menyimpan seluruh status panggung aktif saat ini ke SQLite."""
        if not self.is_active:
            await database.clear_sajam_data()
            return
            
        vc_id = self.voice_channel.id if self.voice_channel else None
        perf_id = self.current_performer.id if self.current_performer else None
        st_str = self.start_time.isoformat() if self.start_time else None
        msg_id = self.active_message.id if self.active_message else None
        msg_chan_id = self.active_message.channel.id if self.active_message else None
        
        await database.save_sajam_session(
            is_active=self.is_active,
            queue_open=self.queue_open,
            voice_channel_id=vc_id,
            current_performer_id=perf_id,
            start_time=st_str,
            peak_visitors=self.peak_visitors,
            peak_queue=self.peak_queue,
            active_message_id=msg_id,
            active_message_channel_id=msg_chan_id
        )
        await database.save_sajam_queue([m.id for m in self.queue])
        await database.save_sajam_sing_count(self.sing_count)
        await database.save_sajam_vc_participants(self.vc_participants)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Memonitoring pergerakan peserta di Voice Channel secara real-time."""
        if not self.is_active or not self.voice_channel:
            return
        
        if after.channel == self.voice_channel:
            if not member.bot:
                self.vc_participants.add(member.id)
                current_vc_members = len([m for m in self.voice_channel.members if not m.bot])
                if current_vc_members > self.peak_visitors:
                    self.peak_visitors = current_vc_members
                await self.persist_state()

    async def build_sajam_embeds(self):
        """Membuat dua tampilan embed terpisah untuk Panggung Utama dan Daftar Antrian."""
        embed_performer = discord.Embed(
            title="🎙️ Panggung Utama",
            color=THEME_COLOR
        )
        if self.current_performer:
            embed_performer.description = (
                f"🎶 **Penyanyi Aktif:**\n"
                f"👉 {self.current_performer.mention}\n\n"
                f"😭 *OTSUKARE MAHA5*"
            )
            embed_performer.set_thumbnail(url=self.current_performer.display_avatar.url)
        else:
            embed_performer.description = "💤 *Panggung saat ini sedang kosong.*"
            embed_performer.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed_queue = discord.Embed(
            title="📋 Daftar Antrian Jamming",
            color=THEME_COLOR
        )
        if self.queue:
            queue_text = "\n".join([f"**#{i+1}** 👥 {m.mention}" for i, m in enumerate(self.queue)])
            embed_queue.description = queue_text
        else:
            embed_queue.description = "📋 *Belum ada antrean di bawah.*"
            
        status_text = "🔓 Pendaftaran: DIBUKA" if self.queue_open else "🔒 Pendaftaran: DITUTUP"
        embed_queue.set_footer(text=f"Gunakan tombol di bawah untuk mengelola giliranmu! • {status_text}")
        
        return [embed_performer, embed_queue]

    async def update_queue_embeds(self, interaction: discord.Interaction):
        """Memperbarui tampilan dua embed antrean secara bersamaan."""
        embeds = await self.build_sajam_embeds()
        try:
            await interaction.response.edit_message(embeds=embeds)
        except Exception:
            try:
                await interaction.message.edit(embeds=embeds)
            except Exception:
                pass

    @commands.group(invoke_without_command=True, aliases=["s"])
    async def sajam(self, ctx):
        """Menampilkan antrean Sajam yang sedang aktif saat ini."""
        if not self.is_active:
            await ctx.send(
                "❌ Sesi Sajam sedang tidak aktif saat ini. Moderator dapat mengetik `!!sajam start` untuk membuka panggung!",
                delete_after=5
            )
            return
        
        if self.active_message:
            try:
                await self.active_message.delete()
            except Exception:
                pass
        
        view = SajamView(self)
        embeds = await self.build_sajam_embeds()
        msg = await ctx.send(embeds=embeds, view=view)
        self.active_message = msg
        await self.persist_state()

    @sajam.command(name="start")
    @commands.check(is_mod_or_admin)
    async def sajam_start(self, ctx):
        """Memulai sesi Sajam baru."""
        if self.is_active:
            await ctx.send("⚠️ Sesi Sajam sudah berjalan saat ini!", delete_after=5)
            return
        
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(
                "❌ Silakan masuk ke dalam Voice Channel lokasi Sajam terlebih dahulu sebelum mengetik perintah `!!sajam start`!",
                delete_after=10
            )
            return
        
        target_channel = ctx.author.voice.channel
        
        self.is_active = True
        self.queue_open = True       
        self.voice_channel = target_channel
        self.start_time = datetime.now()
        self.current_performer = None
        self.queue = []
        self.sing_count = {}
        self.vc_participants = set()
        self.peak_queue = 0
        
        initial_members = [m for m in target_channel.members if not m.bot]
        self.peak_visitors = len(initial_members)
        for m in initial_members:
            self.vc_participants.add(m.id)
                
        if self.active_message:
            try:
                await self.active_message.delete()
            except Exception:
                pass

        view = SajamView(self)
        embeds = await self.build_sajam_embeds()
        msg = await ctx.send(embeds=embeds, view=view)
        self.active_message = msg
        
        await self.persist_state()
        
        await ctx.send(
            f"📢 **Sesi Sajam berhasil dimulai di channel {target_channel.mention}!** 🎉",
            delete_after=10
        )

    @sajam.command(name="end")
    @commands.check(is_mod_or_admin)
    async def sajam_end(self, ctx):
        """Mengakhiri sesi Sajam."""
        await self.end_sajam_session(ctx)

    async def end_sajam_session(self, ctx_or_interaction):
        """Mengakhiri sesi Sajam dan merekap data statistiknya."""
        if not self.is_active:
            if isinstance(ctx_or_interaction, discord.Interaction):
                await ctx_or_interaction.followup.send("❌ Sesi Sajam memang tidak aktif.", ephemeral=True)
            else:
                await ctx_or_interaction.send("❌ Sesi Sajam memang tidak aktif.", delete_after=5)
            return

        if self.active_message:
            try:
                msg = await self.active_message.channel.fetch_message(self.active_message.id)
                embeds = msg.embeds
                if len(embeds) >= 2:
                    embeds[1].title = "📋 Daftar Antrian (Selesai)"
                    embeds[1].description = "Sesi Sajam telah diakhiri."
                await msg.edit(embeds=embeds, view=None)
            except Exception:
                pass

        end_time = datetime.now()
        duration = end_time - self.start_time
        
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours} jam {minutes} menit {seconds} detik" if hours else f"{minutes} menit {seconds} detik"

        performer_stats = []
        for mid, count in self.sing_count.items():
            member = self.voice_channel.guild.get_member(mid)
            mention = member.mention if member else f"<@{mid}>"
            performer_stats.append(f"• {mention} ({count}x Tampil)")
        performer_stats_text = "\n".join(performer_stats) if performer_stats else "Tidak ada yang tampil bernyanyi."

        total_visitors = len(self.vc_participants)

        embed_stats = discord.Embed(
            title="🏁 Sesi Sajam Selesai😭! 🏁",
            description=(
                "Terima kasih kepada seluruh peserta dan staf yang telah berpartisipasi di SAJAM:The Last Dance!\n"
                "Berikut laporan rekapitulasi data sesi jamming kali ini:\n\n"
                f"🔊 **Lokasi VC:** {self.voice_channel.mention if self.voice_channel else 'Tidak Terdeteksi'}\n"
                f"⏱️ **Total Durasi:** {duration_str}\n"
                f"📈 **Peak Pengunjung VC:** {self.peak_visitors} orang\n"
                f"👥 **Total Pengunjung VC:** {total_visitors} orang\n"
                f"📋 **Peak Panjang Antrian:** {self.peak_queue} orang"
            ),
            color=SUCCESS_COLOR
        )
        
        embed_stats.add_field(name="🎙️ Detail Penyanyi (Singers)", value=performer_stats_text, inline=False)
        embed_stats.set_footer(text=f"Sesi dimulai pada {self.start_time.strftime('%H:%M:%S')} - Berakhir pada {end_time.strftime('%H:%M:%S')}")

        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.followup.send(embed=embed_stats)
        else:
            await ctx_or_interaction.send(embed=embed_stats)

        self.is_active = False
        self.queue_open = True
        self.voice_channel = None
        self.current_performer = None
        self.queue = []
        self.sing_count = {}
        self.vc_participants = set()
        self.peak_visitors = 0
        self.peak_queue = 0
        self.start_time = None
        self.active_message = None

        await database.clear_sajam_data()


async def setup(bot):
    await bot.add_cog(SajamCog(bot))