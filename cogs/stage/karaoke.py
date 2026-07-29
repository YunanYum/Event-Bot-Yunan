import discord
from discord.ext import commands
import math
import random
import traceback
from datetime import datetime
from core.database import database

THEME_COLOR = discord.Color.from_rgb(214, 204, 224)

def get_random_thanks(member_mention: str) -> str:
    phrases = [
        f"Gokil parah, suaranya mantap banget {member_mention}! 🔥 You nailed it!",
        f"Makasih banyak {member_mention} udah nyumbang suara indahnya hari ini! ✨",
        f"Sumpah {member_mention}, merinding denger suaranya! Keren abis! 👏",
        f"Otsukaresama desu {member_mention}! Suaramu sugoi banget! 🎶",
        f"Kasih tepuk tangan yang paling meriah dulu buat {member_mention}! 👏🔥"
    ]
    return random.choice(phrases)


# --- CLASS MODEL SESI KARAOKE PER CHANNEL ---

class KaraokeSession:
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.current_performer = None
        self.queue = []
        self.active_message = None
        self.skip_votes = set()
        self.stage_start_time = None  # Waktu mulai tampil penyanyi aktif


# --- TOMBOL INTERAKTIF KARAOKE ---

class KaraokeView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Join Antrian", emoji="🎟️", style=discord.ButtonStyle.green, row=0)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        channel_id = interaction.channel_id
        success, msg = await self.cog.add_to_queue(channel_id, member)
        await interaction.response.send_message(msg, ephemeral=True)
        if success:
            await self.cog.refresh_panel(channel_id)

    @discord.ui.button(label="Keluar Antrian", emoji="🚪", style=discord.ButtonStyle.red, row=0)
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        channel_id = interaction.channel_id
        success, msg = await self.cog.remove_from_queue(channel_id, member)
        await interaction.response.send_message(msg, ephemeral=True)
        if success:
            await self.cog.refresh_panel(channel_id)

    @discord.ui.button(label="Selesai Tampil", emoji="✅", style=discord.ButtonStyle.blurple, row=0)
    async def done_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        channel_id = interaction.channel_id
        session = self.cog.get_session(channel_id)

        if not session.current_performer or session.current_performer.id != member.id:
            await interaction.response.send_message("❌ Tombol ini hanya dapat ditekan oleh penyanyi yang **Sedang Tampil** di channel ini!", ephemeral=True)
            return

        thanks_msg, _ = await self.cog.finish_performance(channel_id, member)
        await interaction.response.send_message(f"🎉 {thanks_msg}", ephemeral=False)
        await self.cog.refresh_panel(channel_id)

    @discord.ui.button(label="LENGSERKAN DIA", emoji="⏩", style=discord.ButtonStyle.secondary, row=1)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        channel_id = interaction.channel_id
        success, msg, is_skipped = await self.cog.handle_skip_vote(channel_id, member)
        
        if is_skipped:
            await interaction.response.send_message(msg, ephemeral=False)
        else:
            await interaction.response.send_message(msg, ephemeral=True)

        if success:
            await self.cog.refresh_panel(channel_id)


# --- COG MAIN CLASS ---

class KaraokeCog(commands.Cog, name="Karaoke Santai"):
    def __init__(self, bot):
        self.bot = bot
        self.sessions = {}
        self.bot.loop.create_task(self.restore_persisted_state())

    def get_session(self, channel_id: int) -> KaraokeSession:
        if channel_id not in self.sessions:
            self.sessions[channel_id] = KaraokeSession(channel_id)
        return self.sessions[channel_id]

    async def persist_session(self, channel_id: int):
        session = self.get_session(channel_id)
        perf_id = session.current_performer.id if session.current_performer else None
        msg_id = session.active_message.id if session.active_message else None
        q_ids = [m.id for m in session.queue]

        await database.save_karaoke_session(channel_id, perf_id, msg_id, q_ids)

    async def restore_persisted_state(self):
        await self.bot.wait_until_ready()
        try:
            all_sessions = await database.load_all_karaoke_sessions()
            restored_rooms = 0

            for chan_id, data in all_sessions.items():
                channel = self.bot.get_channel(chan_id)
                if not channel:
                    try: channel = await self.bot.fetch_channel(chan_id)
                    except Exception: continue

                if not channel: continue

                session = self.get_session(chan_id)

                if data["msg_id"]:
                    try: session.active_message = await channel.fetch_message(data["msg_id"])
                    except Exception: session.active_message = None

                if data["performer_id"]:
                    try: 
                        session.current_performer = await self.bot.fetch_user(data["performer_id"])
                        session.stage_start_time = datetime.now()  # Inisialisasi timer panggung
                    except Exception: 
                        session.current_performer = None

                session.queue = []
                for uid in data["queue_ids"]:
                    try:
                        u = await self.bot.fetch_user(uid)
                        if u: session.queue.append(u)
                    except Exception: continue

                if session.current_performer or session.queue:
                    restored_rooms += 1

            if restored_rooms > 0:
                print(f"📡 [Karaoke Persistence] Memulihkan sesi karaoke di {restored_rooms} room/channel terpisah.")
        except Exception as e:
            print(f"❌ [Karaoke Persistence Error] Gagal memulihkan antrean: {e}")

    # --- HELPER PROTEKSI 1 MENIT STATISTIK KTP ---
    async def _check_and_record_stage_stat(self, session: KaraokeSession, member: discord.Member) -> bool:
        """Mengecek apakah penyanyi sudah di atas panggung minimal 60 detik (1 menit)."""
        if session.stage_start_time:
            duration = (datetime.now() - session.stage_start_time).total_seconds()
            if duration >= 60:
                await database.increment_event_stat(member.id, 'karaoke')
                return True
        return False

    # --- LOGIKA OPERASIONAL PER CHANNEL ---

    async def add_to_queue(self, channel_id: int, member: discord.Member) -> tuple[bool, str]:
        session = self.get_session(channel_id)

        if (session.current_performer and session.current_performer.id == member.id) or (member.id in [m.id for m in session.queue]):
            return False, "⚠️ Kamu sudah berada di dalam antrean atau sedang aktif tampil di channel ini!"

        if not session.current_performer:
            session.current_performer = member
            session.stage_start_time = datetime.now()  # Catat Waktu Mulai Tampil
            session.skip_votes.clear()
            await self.persist_session(channel_id)
            return True, "🎙️ Kamu langsung naik ke panggung utama di channel ini!"
        else:
            session.queue.append(member)
            await self.persist_session(channel_id)
            return True, f"✅ Berhasil bergabung ke antrean posisi ke-**{len(session.queue)}**!"

    async def remove_from_queue(self, channel_id: int, member: discord.Member) -> tuple[bool, str]:
        session = self.get_session(channel_id)

        if session.current_performer and session.current_performer.id == member.id:
            # Pengecekan Durasi 1 Menit
            counted = await self._check_and_record_stage_stat(session, member)
            
            session.current_performer = session.queue.pop(0) if session.queue else None
            session.stage_start_time = datetime.now() if session.current_performer else None
            session.skip_votes.clear()
            await self.persist_session(channel_id)
            
            msg = "🚪 Kamu memilih untuk turun dari panggung."
            if counted:
                msg += " *(Penampilan 1+ menit tercatat di KTP!)*"
            else:
                msg += " *(Tampil di bawah 1 menit tidak tercatat di KTP)*"
            return True, msg

        for m in session.queue:
            if m.id == member.id:
                session.queue.remove(m)
                await self.persist_session(channel_id)
                return True, "🚪 Berhasil keluar dari daftar antrean karaoke!"

        return False, "⚠️ Kamu sedang tidak ada di dalam antrean channel ini."

    async def finish_performance(self, channel_id: int, member: discord.Member) -> tuple[str, discord.Member]:
        session = self.get_session(channel_id)
        
        # Pengecekan Durasi 1 Menit
        counted = await self._check_and_record_stage_stat(session, member)
        thanks = get_random_thanks(member.mention)

        if not counted:
            thanks += "\n⚠️ *Catatan: Penampilan di bawah 1 menit tidak dihitung ke statistik KTP.*"

        session.current_performer = session.queue.pop(0) if session.queue else None
        session.stage_start_time = datetime.now() if session.current_performer else None
        session.skip_votes.clear()
        await self.persist_session(channel_id)
        
        if session.current_performer:
            msg = f"{thanks}\n👉 Giliran berikutnya: {session.current_performer.mention} naik panggung! 🎙️"
        else:
            msg = f"{thanks}\n💤 Panggung karaoke di channel ini saat ini kosong."
            
        return msg, session.current_performer

    async def handle_skip_vote(self, channel_id: int, member: discord.Member) -> tuple[bool, str, bool]:
        session = self.get_session(channel_id)

        if not session.current_performer:
            return False, "⚠️ Sedang tidak ada penyanyi di atas panggung.", False

        # 1. MODERATOR OVERRIDE
        if member.guild_permissions.manage_guild:
            old_performer = session.current_performer
            await self._check_and_record_stage_stat(session, old_performer)

            session.current_performer = session.queue.pop(0) if session.queue else None
            session.stage_start_time = datetime.now() if session.current_performer else None
            session.skip_votes.clear()
            await self.persist_session(channel_id)

            next_mention = session.current_performer.mention if session.current_performer else "Kosong"
            msg = (
                f"🚨 **Moderator Melengserkan Penyanyi!**\n"
                f"Moderator {member.mention} memaksa {old_performer.mention} turun panggung.\n"
                f"👉 **Giliran berikutnya:** {next_mention}! 🎙️"
            )
            return True, msg, True

        if member.id == session.current_performer.id:
            return False, "⚠️ Kamu adalah penyanyi aktif! Silakan tekan tombol 'Selesai Tampil' untuk turun.", False

        # 2. Hitung threshold ¼ dari warga VC
        vc = session.current_performer.voice.channel if (isinstance(session.current_performer, discord.Member) and session.current_performer.voice and session.current_performer.voice.channel) else None
        required_votes = max(1, math.ceil(len([m for m in vc.members if not m.bot]) * 0.25)) if vc else 1

        if member.id in session.skip_votes:
            return False, f"⚠️ Kamu sudah memberikan vote skip! ({len(session.skip_votes)}/{required_votes} vote)", False

        session.skip_votes.add(member.id)
        
        if len(session.skip_votes) >= required_votes:
            old_performer = session.current_performer
            await self._check_and_record_stage_stat(session, old_performer)

            session.current_performer = session.queue.pop(0) if session.queue else None
            session.stage_start_time = datetime.now() if session.current_performer else None
            session.skip_votes.clear()
            await self.persist_session(channel_id)

            next_mention = session.current_performer.mention if session.current_performer else "Kosong"
            msg = (
                f"⏩ **Penyanyi Dilengserkan!**\n"
                f"Atas vote ¼ warga VC ({required_votes} vote), {old_performer.mention} diturunkan dari panggung.\n"
                f"👉 **Giliran berikutnya:** {next_mention}! 🎙️"
            )
            return True, msg, True
        else:
            remaining = required_votes - len(session.skip_votes)
            msg = f"🗳️ **Vote Skip Dicatat!** ({len(session.skip_votes)}/{required_votes} vote dari ¼ warga VC).\nButuh **{remaining} vote lagi** untuk menurunkan {session.current_performer.mention}."
            return True, msg, False

    def build_embeds(self, session: KaraokeSession) -> list[discord.Embed]:
        embed_performer = discord.Embed(title="🎙️ Panggung Utama", color=THEME_COLOR)
        if session.current_performer:
            vc = session.current_performer.voice.channel if (isinstance(session.current_performer, discord.Member) and session.current_performer.voice and session.current_performer.voice.channel) else None
            req_votes = max(1, math.ceil(len([m for m in vc.members if not m.bot]) * 0.25)) if vc else 1

            vote_status = f"\n\n🗳️ *Vote Skip:* `{len(session.skip_votes)}/{req_votes} vote (¼ VC)`" if session.skip_votes else ""
            
            # Tampilan bersih tanpa indikator timer
            embed_performer.description = (
                f"🎶 **Penyanyi Aktif:**\n"
                f"👉 {session.current_performer.mention}\n\n"
                f"⭐ *Sedang menguasai panggung!*{vote_status}"
            )
            embed_performer.set_thumbnail(url=session.current_performer.display_avatar.url)
        else:
            embed_performer.description = "💤 *Panggung saat ini sedang kosong.*"
            embed_performer.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed_queue = discord.Embed(title="📋 Daftar Antrian Karaoke", color=THEME_COLOR)
        if session.queue:
            queue_text = "\n".join([f"**#{i+1}** 👥 {m.mention}" for i, m in enumerate(session.queue)])
            embed_queue.description = queue_text
        else:
            embed_queue.description = "*Belum ada antrean di bawah.*"

        embed_queue.set_footer(text="Gunakan tombol di bawah untuk mengelola giliranmu!")
        return [embed_performer, embed_queue]

    async def refresh_panel(self, channel_id: int):
        session = self.get_session(channel_id)
        if session.active_message:
            try:
                embeds = self.build_embeds(session)
                await session.active_message.edit(embeds=embeds, view=KaraokeView(self))
            except Exception:
                pass

    # --- PERINTAH TEKS ---

    @commands.command(name="q", aliases=["queue", "karaoke"])
    async def queue_command(self, ctx):
        session = self.get_session(ctx.channel.id)

        if session.active_message:
            try: await session.active_message.delete()
            except Exception: pass

        view = KaraokeView(self)
        embeds = self.build_embeds(session)
        msg = await ctx.send(embeds=embeds, view=view)
        session.active_message = msg
        await self.persist_session(ctx.channel.id)

    @commands.command(name="qj", aliases=["qjoin"])
    async def queue_join_command(self, ctx):
        channel_id = ctx.channel.id
        session = self.get_session(channel_id)
        success, msg = await self.add_to_queue(channel_id, ctx.author)
        await ctx.send(f"{ctx.author.mention} {msg}", delete_after=10)
        if success:
            if not session.active_message: await self.queue_command(ctx)
            else: await self.refresh_panel(channel_id)

    @commands.command(name="ql", aliases=["qleave"])
    async def queue_leave_command(self, ctx):
        channel_id = ctx.channel.id
        success, msg = await self.remove_from_queue(channel_id, ctx.author)
        await ctx.send(f"{ctx.author.mention} {msg}", delete_after=10)
        if success: await self.refresh_panel(channel_id)

    @commands.command(name="qd", aliases=["qdone"])
    async def queue_done_command(self, ctx):
        channel_id = ctx.channel.id
        session = self.get_session(channel_id)

        if not session.current_performer or session.current_performer.id != ctx.author.id:
            await ctx.send(f"⚠️ {ctx.author.mention}, hanya penyanyi yang **Sedang Tampil** yang bisa mengakhiri giliran!", delete_after=10)
            return

        thanks_msg, _ = await self.finish_performance(channel_id, ctx.author)
        await ctx.send(f"🎉 {thanks_msg}")
        await self.refresh_panel(channel_id)

    @commands.command(name="qskip", aliases=["qn", "qnext"])
    async def queue_skip_command(self, ctx):
        channel_id = ctx.channel.id
        success, msg, is_skipped = await self.handle_skip_vote(channel_id, ctx.author)
        if is_skipped: await ctx.send(msg)
        else: await ctx.send(f"{ctx.author.mention} {msg}", delete_after=10)
            
        if success: await self.refresh_panel(channel_id)

    @commands.command(name="qclear", aliases=["qreset"])
    @commands.has_permissions(manage_guild=True)
    async def queue_clear_command(self, ctx):
        channel_id = ctx.channel.id
        session = self.get_session(channel_id)
        session.current_performer = None
        session.queue = []
        session.skip_votes.clear()
        session.stage_start_time = None
        
        await database.clear_karaoke_session_db(channel_id)
        await ctx.send(f"🧹 Antrean karaoke di channel {ctx.channel.mention} berhasil dibersihkan oleh Moderator!")
        await self.refresh_panel(channel_id)


async def setup(bot):
    await bot.add_cog(KaraokeCog(bot))