# cogs/system/admin.py

import discord
from discord.ext import commands
import os
import shutil
import psutil
import platform
from datetime import datetime
from core.database import database

def is_mod_or_admin(ctx):
    return ctx.author.guild_permissions.manage_guild

def create_bar(percent: float, length: int = 10) -> str:
    """Helper visual progress bar [■■■□□□□□□□]."""
    filled = int(round(length * percent / 100))
    return "■" * filled + "□" * (length - filled)

class ConfirmRestore(discord.ui.View):
    """View Tombol Konfirmasi untuk mencegah kecelakaan fatal saat restore."""
    def __init__(self, author):
        super().__init__(timeout=30.0)
        self.author = author
        self.value = None
    
    @discord.ui.button(label="Ya, Pulihkan Data", style=discord.ButtonStyle.red, emoji="⚠️")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Hanya pengirim perintah yang bisa menekan tombol ini!", ephemeral=True)
            return
        self.value = True
        self.stop()
        
    @discord.ui.button(label="Batal", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Hanya pengirim perintah yang bisa menekan tombol ini!", ephemeral=True)
            return
        self.value = False
        self.stop()


class AdminCog(commands.Cog, name="Sistem Admin & Monitoring"):
    def __init__(self, bot):
        self.bot = bot

    # --- PERINTAH MONITORING BOT & HOSTING ---
    @commands.command(name="bot", aliases=["botstatus", "stats", "system", "host"])
    @commands.check(is_mod_or_admin)
    async def status_command(self, ctx):
        """Menampilkan status lengkap performa bot dan sistem hosting (Khusus Dev/Mod)."""
        async with ctx.typing():
            # 1. Kalkulasi Uptime
            start_time = getattr(self.bot, 'start_time', datetime.now())
            uptime_delta = datetime.now() - start_time
            days, remainder = divmod(int(uptime_delta.total_seconds()), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"`{days}d {hours}h {minutes}m {seconds}s`" if days else f"`{hours}h {minutes}m {seconds}s`"

            # 2. Kalkulasi Resource Hosting
            cpu_usage = psutil.cpu_percent(interval=0.5)
            cpu_bar = create_bar(cpu_usage)

            mem = psutil.virtual_memory()
            mem_used_mb = mem.used / (1024 * 1024)
            mem_total_mb = mem.total / (1024 * 1024)
            mem_bar = create_bar(mem.percent)

            # RAM Khusus Proses Bot Python
            process = psutil.Process(os.getpid())
            bot_ram_mb = process.memory_info().rss / (1024 * 1024)

            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / (1024 ** 3)
            disk_total_gb = disk.total / (1024 ** 3)

            # 3. Kalkulasi Database & Warga
            db_path = database.db_path
            db_size_mb = os.path.getsize(db_path) / (1024 * 1024) if os.path.exists(db_path) else 0
            ktp_count = await database.get_ktp_count()

            # Latency / Ping
            ping_ms = round(self.bot.latency * 1000)

            # Status Warna Embed berdasarkan Beban CPU/RAM
            embed_color = discord.Color.green() if cpu_usage < 75 else (discord.Color.gold() if cpu_usage < 90 else discord.Color.red())

            embed = discord.Embed(
                title="🖥️ MONITORING SISTEM & HOSTING MAHA5 BOT",
                description="Laporan kondisi performa bot dan infrastruktur hosting realtime:\n",
                color=embed_color,
                timestamp=datetime.now()
            )

            # FIELD 1: KONDISI BOT
            embed.add_field(
                name="🤖 KONDISI BOT DISCORD",
                value=(
                    f"> **Koneksi Ping:** `{ping_ms} ms`\n"
                    f"> **Waktu Aktif (Uptime):** {uptime_str}\n"
                    f"> **Cogs Dimuat:** `{len(self.bot.cogs)}` Modul Aktif\n"
                    f"> **Jangkauan Server:** `{len(self.bot.guilds)}` Guild | `{len(self.bot.users):,}` Member"
                ),
                inline=False
            )

            # FIELD 2: HOSTING RESOURCE
            embed.add_field(
                name="💻 HOSTING & RESOURCE SYSTEM",
                value=(
                    f"> **OS Host:** `{platform.system()} {platform.release()}`\n"
                    f"> **Versi Runtime:** `Python {platform.python_version()}` | `discord.py {discord.__version__}`\n"
                    f"> **Beban CPU:** `{cpu_usage}%` `[{cpu_bar}]`\n"
                    f"> **RAM Hosting:** `{mem_used_mb:,.0f} MB` / `{mem_total_mb:,.0f} MB` ({mem.percent}%) `[{mem_bar}]`\n"
                    f"> **RAM Bot Process:** `{bot_ram_mb:,.2f} MB` *(Alokasi Khusus Skrip Bot)*\n"
                    f"> **Penyimpanan Disk:** `{disk_used_gb:,.2f} GB` / `{disk_total_gb:,.2f} GB` ({disk.percent}%)"
                ),
                inline=False
            )

            # FIELD 3: DATABASE & WARGA
            embed.add_field(
                name="💾 DATABASE & METRIK KELURAHAN",
                value=(
                    f"> **Ukuran File DB (`event_bot.db`):** `{db_size_mb:,.2f} MB`\n"
                    f"> **Mode SQLite:** `WAL (Write-Ahead Logging)` ✅\n"
                    f"> **Warga Terdaftar (KTP):** `{ktp_count:,}` Jiwa"
                ),
                inline=False
            )

            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_footer(text=f"Diakses oleh Dev: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.check(is_mod_or_admin)
    async def db(self, ctx):
        """Perintah induk untuk pengelolaan database."""
        embed = discord.Embed(
            title="💾 Panduan Perintah Database",
            description=(
                f"Gunakan sub-perintah berikut untuk mengelola database:\n\n"
                f"⚙️ **`{ctx.prefix}db backup`**\n"
                f"└ Membuat backup manual dari database aktif saat ini.\n\n"
                f"📋 **`{ctx.prefix}db list`**\n"
                f"└ Menampilkan daftar file backup DB (SQLite) yang tersedia.\n\n"
                f"🔄 **`{ctx.prefix}db restore <nama_file_backup>`**\n"
                f"└ Memulihkan database menggunakan file cadangan pilihan."
            ),
            color=discord.Color.from_rgb(214, 204, 224)
        )
        await ctx.send(embed=embed)

    @db.command(name="backup")
    @commands.check(is_mod_or_admin)
    async def db_backup(self, ctx):
        """Membuat backup database saat ini secara manual."""
        db_path = database.db_path
        if not os.path.exists(db_path):
            return await ctx.send("❌ Gagal: File database aktif tidak ditemukan!")
        
        dir_name = os.path.dirname(db_path) or "."
        backup_dir = os.path.join(dir_name, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_filename = f"db_backup_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            shutil.copy2(db_path, backup_path)
            await ctx.send(f"✅ Berhasil membuat backup manual: `{backup_filename}`")
        except Exception as e:
            await ctx.send(f"❌ Gagal membuat backup manual: {e}")

    @db.command(name="list")
    @commands.check(is_mod_or_admin)
    async def db_list(self, ctx):
        """Menampilkan daftar file backup yang tersedia."""
        db_path = database.db_path
        dir_name = os.path.dirname(db_path) or "."
        backup_dir = os.path.join(dir_name, "backups")
        
        if not os.path.exists(backup_dir):
            return await ctx.send("📋 Belum ada folder backup yang terbuat.")
        
        files = [f for f in os.listdir(backup_dir) if f.endswith(".db")]
        if not files:
            return await ctx.send("📋 Folder backup kosong, belum ada data cadangan.")
        
        files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)), reverse=True)
        
        show_limit = 10
        files_to_show = files[:show_limit]
        
        description = f"Menampilkan {len(files_to_show)} dari {len(files)} file backup terbaru:\n\n"
        for i, f in enumerate(files_to_show):
            filepath = os.path.join(backup_dir, f)
            mtime = os.path.getmtime(filepath)
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            size_kb = os.path.getsize(filepath) / 1024
            description += f"**{i+1}.** `{f}`\n📅 *{mtime_str}* | 💾 *{size_kb:.2f} KB*\n\n"
        
        embed = discord.Embed(
            title="💾 Daftar Backup Database (SQLite)",
            description=description,
            color=discord.Color.from_rgb(214, 204, 224)
        )
        embed.set_footer(text=f"Gunakan !!db restore <nama_file> untuk memulihkan database.")
        await ctx.send(embed=embed)

    @db.command(name="restore")
    @commands.check(is_mod_or_admin)
    async def db_restore(self, ctx, filename: str):
        """Memulihkan database menggunakan file backup tertentu."""
        db_path = database.db_path
        dir_name = os.path.dirname(db_path) or "."
        backup_dir = os.path.join(dir_name, "backups")
        backup_path = os.path.join(backup_dir, filename)
        
        if not os.path.exists(backup_path):
            return await ctx.send(f"❌ File backup `{filename}` tidak ditemukan di folder backups!")
        
        if not filename.endswith(".db"):
            return await ctx.send("❌ File backup yang dipilih harus berekstensi `.db`!")

        view = ConfirmRestore(ctx.author)
        confirm_msg = await ctx.send(
            f"⚠️ **PERINGATAN!**\nApakah kamu yakin ingin menimpa database aktif dengan file `{filename}`?\n"
            "Semua perubahan data setelah waktu backup tersebut akan hilang!",
            view=view
        )
        
        await view.wait()
        
        for item in view.children:
            item.disabled = True
        try:
            await confirm_msg.edit(view=view)
        except Exception:
            pass
            
        if view.value is None:
            await ctx.send("⏱️ Waktu konfirmasi habis. Pemulihan dibatalkan.")
            return
        elif not view.value:
            await ctx.send("❌ Pemulihan dibatalkan.")
            return
        
        try:
            shutil.copy2(backup_path, db_path)
            
            reload_status = ""
            try:
                await self.bot.reload_extension('cogs.events.ppkm')
                reload_status += "\n✅ Konfigurasi PPKM berhasil dimuat ulang!"
            except Exception as re:
                reload_status += f"\n❌ Gagal reload cogs.events.ppkm: {re}"
                
            try:
                await self.bot.reload_extension('cogs.stage.sajam')
                reload_status += "\n✅ Sesi Sajam berhasil dimuat ulang!"
            except Exception as re:
                reload_status += f"\n❌ Gagal reload cogs.stage.sajam: {re}"
            
            await ctx.send(f"✨ **Pemulihan Berhasil!** Database telah dipulihkan menggunakan `{filename}` {reload_status}")
        except Exception as e:
            await ctx.send(f"❌ Gagal memulihkan database: {e}")


async def setup(bot):
    await bot.add_cog(AdminCog(bot))