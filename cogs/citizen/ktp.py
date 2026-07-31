import discord
from discord.ext import commands
import random
import traceback
from core.database import database
from core.safety import is_inappropriate_name
from core.titles import TITLE_MISSIONS, SHOP_TITLES

THEME_COLOR = discord.Color.from_rgb(214, 204, 224)

OMELAN_PAK_LURAH = [
    "Bocah iki... KTP kok diganti-ganti terus kaya ganti baju! Kamu pikir blanko KTP kantor kelurahan ini gratis?! Yaudah nih data barumu tak perbarui!",
    "Walah, datang lagi! Hobi banget revisi KTP, lagi dikejar debt collector opo piye?! Yaudah awas kalau ganti-ganti lagi ya!",
    "Hadeh! Kantor kelurahan lagi rame antrean malah kamu bolak-balik revisi data. Yaudah ini KTP barumu udah tak ganti, sana balik!",
    "Sumpah ya, baru kali ini ada warga hobi banget bolak-balik kantor lurah cuma buat ganti identitas! Yaudah tak simpen data barumu."
]

GENDER_MAP = {
    "cowok": "Cowok", "pria": "Cowok", "laki": "Cowok", "laki-laki": "Cowok", "cwk": "Cowok",
    "cewek": "Cewek", "wanita": "Cewek", "perempuan": "Cewek", "cwe": "Cewek",
    "hode": "Hode", "femboy": "Hode", "trap": "Hode"
}

STATUS_MAP = {
    "menikah": "Menikah", "nikah": "Menikah", "kawin": "Menikah", "married": "Menikah",
    "jomblo": "Jomblo", "single": "Jomblo", "sendiri": "Jomblo",
    "simpanan": "Simpanan", "selingkuhan": "Simpanan", "cadangan": "Simpanan"
}

async def generate_sequential_nim() -> str:
    count = await database.get_ktp_count()
    seq = count + 1
    while True:
        seq_str = f"{seq:08d}"
        nim = f"M5-{seq_str[:4]}-{seq_str[4:]}"
        if not await database.is_nim_exists(nim):
            return nim
        seq += 1


class TitleSelect(discord.ui.Select):
    def __init__(self, target_id: int, unlocked_titles: list, ktp_view):
        self.target_id = target_id
        self.ktp_view = ktp_view
        options = []
        for t_name in unlocked_titles:
            if t_name in TITLE_MISSIONS:
                info = TITLE_MISSIONS[t_name]
                options.append(discord.SelectOption(label=t_name, emoji=info["emoji"], description=info["misi"][:50]))
            elif t_name in SHOP_TITLES:
                info = SHOP_TITLES[t_name]
                options.append(discord.SelectOption(label=t_name, emoji=info["emoji"], description=f"Title Toko: {info['desc']}"[:50]))
            else:
                options.append(discord.SelectOption(label=t_name, emoji="🛡️", description="Title Terbuka"))

        if not options:
            options.append(discord.SelectOption(label="Warga Teladan", emoji="🛡️", description="Title Dasar"))

        super().__init__(placeholder="👑 Pilih Title Terbuka...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("❌ Kamu hanya bisa mengatur Title pada KTP milikmu sendiri!", ephemeral=True)
            return
        
        chosen_title = self.values[0]
        await database.update_ktp_title_simp(self.target_id, title=chosen_title)
        
        self.ktp_view.profile = await database.get_ktp_profile(self.target_id)
        if hasattr(self.ktp_view, "message") and self.ktp_view.message:
            try:
                embed = self.ktp_view.build_page_2_embed() if self.ktp_view.current_page == 2 else self.ktp_view.build_page_1_embed()
                await self.ktp_view.message.edit(embed=embed, view=self.ktp_view)
            except Exception:
                pass

        await interaction.response.send_message(f"✅ Title kamu berhasil diubah menjadi: **{chosen_title}**!", ephemeral=True)


class SimpSelect(discord.ui.Select):
    def __init__(self, target_id: int, ktp_view):
        self.target_id = target_id
        self.ktp_view = ktp_view
        options = [
            discord.SelectOption(label="Daisy Ignacia Y", emoji="💜", description="Oshi: Daisy Ignacia Y"),
            discord.SelectOption(label="Hera Garalea", emoji="💙", description="Oshi: Hera Garalea"),
            discord.SelectOption(label="Rena Anggraeni", emoji="💚", description="Oshi: Rena Anggraeni"),
            discord.SelectOption(label="Saku Kurata", emoji="💛", description="Oshi: Saku Kurata"),
            discord.SelectOption(label="Maudy Sukaiga", emoji="🧡", description="Oshi: Maudy Sukaiga"),
            discord.SelectOption(label="Fuyumi Celestia", emoji="❤️", description="Oshi: Fuyumi Celestia"),
            discord.SelectOption(label="Semua VTuber MAHA5", emoji="💖", description="DD / Simp Semuanya!"),
            discord.SelectOption(label="Belum Memilih", emoji="⚪", description="Reset pilihan Oshi"),
        ]
        super().__init__(placeholder="💖 Pilih Oshi / Simp VTuber...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("❌ Kamu hanya bisa mengatur Oshi pada KTP milikmu sendiri!", ephemeral=True)
            return
        
        chosen_simp = self.values[0]
        await database.update_ktp_title_simp(self.target_id, simp_vtuber=chosen_simp)
        
        self.ktp_view.profile = await database.get_ktp_profile(self.target_id)
        if hasattr(self.ktp_view, "message") and self.ktp_view.message:
            try:
                embed = self.ktp_view.build_page_2_embed() if self.ktp_view.current_page == 2 else self.ktp_view.build_page_1_embed()
                await self.ktp_view.message.edit(embed=embed, view=self.ktp_view)
            except Exception:
                pass

        await interaction.response.send_message(f"✅ Oshi VTuber kamu berhasil diubah menjadi: **{chosen_simp}**!", ephemeral=True)


class ConfigCardView(discord.ui.View):
    def __init__(self, target_id: int, unlocked_titles: list, ktp_view):
        super().__init__(timeout=120.0)
        self.add_item(TitleSelect(target_id, unlocked_titles, ktp_view))
        self.add_item(SimpSelect(target_id, ktp_view))


class KTPView(discord.ui.View):
    def __init__(self, ctx, target: discord.User, profile, stats, fans_count: int, unlocked_titles: list):
        super().__init__(timeout=180.0)
        self.ctx = ctx
        self.target = target
        self.profile = profile
        self.stats = stats
        self.fans_count = fans_count
        self.unlocked_titles = unlocked_titles
        self.current_page = 1
        self.message = None

    def build_page_1_embed(self) -> discord.Embed:
        nim = self.profile[1]
        nama = self.profile[2]
        gender = self.profile[3] if len(self.profile) > 3 and self.profile[3] else "Cowok"
        status = self.profile[4] if len(self.profile) > 4 and self.profile[4] else "Jomblo"

        embed = discord.Embed(title="KARTU TANDA PENDUDUK MAHA5", color=discord.Color.from_rgb(88, 101, 242))
        embed.set_thumbnail(url=self.target.display_avatar.url)
        
        embed.add_field(
            name="IDENTITAS MEMBER",
            value=f"> **NIM:** `{nim}`\n> **Nama Lengkap:** {nama}\n> **Username:** `@{self.target.name}`",
            inline=False
        )
        embed.add_field(
            name="INFORMASI PROFIL",
            value=f"> **Gender:** {gender}\n> **Status Relationship:** {status}\n> **Kewarganegaraan:** WNM (Warga Negara MAHA5)\n> **Berlaku Hingga:** Menjadi Member Discord",
            inline=False
        )
        embed.set_footer(text="Provinsi MAHA5 Discord • KTP Digital Resmi", icon_url=self.ctx.bot.user.display_avatar.url)
        return embed

    def build_page_2_embed(self) -> discord.Embed:
        nama = self.profile[2]
        title = self.profile[5] if len(self.profile) > 5 and self.profile[5] else "Warga Teladan"
        simp_vtuber = self.profile[6] if len(self.profile) > 6 and self.profile[6] else "Belum Memilih"

        embed = discord.Embed(title="KARTU TANDA PANGGUNG MAHA5", color=discord.Color.from_rgb(224, 170, 170))
        embed.set_thumbnail(url=self.target.display_avatar.url)
        
        embed.add_field(
            name="INFORMASI PANGGUNG & FANS",
            value=(
                f"> **Nama Member:** {nama}\n"
                f"> **Title Member:** `{title}`\n"
                f"> **Oshi / Simp VTuber:** `{simp_vtuber}`\n"
                f"> **Jumlah Fans:** `{self.fans_count}` Fans"
            ),
            inline=False
        )
        embed.add_field(
            name="RIWAYAT EVENT & PANGGUNG",
            value=(
                f"> **Tampil di Sajam:** `{self.stats.get('sajam', 0)}x` Tampil\n"
                f"> **Tampil di Karaoke:** `{self.stats.get('karaoke', 0)}x` Tampil\n"
                f"> **Partisipasi Gacha PPKM:** `{self.stats.get('ppkm', 0)}x` Ikut\n"
                f"> **Partisipasi Giveaway:** `{self.stats.get('giveaway', 0)}x` Ikut"
            ),
            inline=False
        )
        embed.set_footer(text="Provinsi MAHA5 Discord • KTP Digital Resmi", icon_url=self.ctx.bot.user.display_avatar.url)
        return embed

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary, disabled=True)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 1
        self.children[0].disabled = True
        self.children[1].disabled = False
        await interaction.response.edit_message(embed=self.build_page_1_embed(), view=self)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 2
        self.children[0].disabled = False
        self.children[1].disabled = True
        await interaction.response.edit_message(embed=self.build_page_2_embed(), view=self)

    @discord.ui.button(emoji="⚙️", style=discord.ButtonStyle.success)
    async def config_card(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("❌ Kamu hanya bisa mengkonfigurasi Card milikmu sendiri!", ephemeral=True)
            return
        
        view = ConfigCardView(self.target.id, self.unlocked_titles, ktp_view=self)
        await interaction.response.send_message("⚙️ **Pengaturan Kartu Tanda Panggung:**\nPilih **Title** dan **Simp VTuber** kamu di bawah ini:", view=view, ephemeral=True)


class KTPModal(discord.ui.Modal, title="Formulir Pendaftaran KTP MAHA5"):
    nama_input = discord.ui.TextInput(label="Nama Lengkap / Panggilan", placeholder="Ketik nama di KTP...", min_length=3, max_length=30, required=True)
    gender_input = discord.ui.TextInput(label="Gender (Cowok / Cewek / Hode)", placeholder="Ketik: Cowok, Cewek, atau Hode", min_length=4, max_length=10, required=True)
    status_input = discord.ui.TextInput(label="Status Relationship (Menikah/Jomblo/Simpanan)", placeholder="Ketik: Menikah, Jomblo, atau Simpanan", min_length=5, max_length=15, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nama = self.nama_input.value.strip()
            gender_raw = self.gender_input.value.strip().lower()
            status_raw = self.status_input.value.strip().lower()

            if is_inappropriate_name(nama):
                await interaction.response.send_message("❌ **Nama Ditolak!** Harap gunakan nama yang sopan.", ephemeral=True)
                return

            gender = GENDER_MAP.get(gender_raw)
            if not gender:
                await interaction.response.send_message("❌ **Gender Tidak Valid!** Pilih: **Cowok**, **Cewek**, atau **Hode**.", ephemeral=True)
                return

            status = STATUS_MAP.get(status_raw)
            if not status:
                await interaction.response.send_message("❌ **Status Tidak Valid!** Pilih: **Menikah**, **Jomblo**, atau **Simpanan**.", ephemeral=True)
                return

            user_id = interaction.user.id
            existing_ktp = await database.get_ktp_profile(user_id)

            if existing_ktp:
                nim = await database.save_ktp_profile(user_id, nama, gender, status)
                omelan = random.choice(OMELAN_PAK_LURAH)
                response_msg = f"👴 **Pak Lurah:** *\"{omelan}\"*\n\n✅ **KTP Berhasil Diperbarui!**\n• **Nama:** {nama}\n• **Gender:** {gender}\n• **Status:** {status}\n\nKetik `!!ktp` untuk melihat KTP terbarumu!"
                await interaction.response.send_message(response_msg, ephemeral=True)
            else:
                nim = await generate_sequential_nim()
                await database.save_ktp_profile(user_id, nama, gender, status, nim)
                response_msg = f"🎉 **Selamat! KTP MAHA5 Diterbitkan!**\n📌 **NIM Unik:** `{nim}`\n• **Nama:** {nama}\n• **Gender:** {gender}\n• **Status:** {status}\n\nKetik `!!ktp` untuk melihat KTP milikmu!"
                await interaction.response.send_message(response_msg, ephemeral=True)

            interaction.client.dispatch(
                "realtime_activity",
                "✍️ PENDAFTARAN / REVISI KTP BARU",
                f"> **Warga:** {interaction.user.mention} (`{interaction.user.id}`)\n"
                f"> **NIM:** `{nim}`\n"
                f"> **Nama:** `{nama}`\n"
                f"> **Gender:** `{gender}`\n"
                f"> **Status:** `{status}`",
                discord.Color.blue(),
                interaction.user
            )

        except Exception as e:
            traceback.print_exc()
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ **Terjadi Kesalahan Sistem:** `{e}`", ephemeral=True)


class LurahView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120.0)

    @discord.ui.button(label="Isi Form KTP 📜", style=discord.ButtonStyle.primary, emoji="✍️")
    async def open_ktp_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(KTPModal())


class KTPCog(commands.Cog, name="Sistem KTP Member"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lurah", aliases=["Lurah"])
    async def lurah_command(self, ctx):
        try:
            profile = await database.get_ktp_profile(ctx.author.id)
            if profile:
                description = f"👴 *Pak Lurah menatap {ctx.author.mention}...*\n\n\"Walah {ctx.author.mention}, mau revisi KTP lagi?! Yaudah klik **Isi Form KTP 📜** di bawah ini!\""
            else:
                description = f"Halo {ctx.author.mention}! Selamat datang di Kantor Kelurahan MAHA5.\nKlik tombol **Isi Form KTP 📜** di bawah ini untuk mendaftar!"

            embed = discord.Embed(title="🏛️ Kantor Kelurahan Server MAHA5", description=description, color=THEME_COLOR)
            embed.set_footer(text="Diterbitkan oleh Pak Lurah • Server MAHA5")
            await ctx.send(embed=embed, view=LurahView())
        except Exception as e:
            await ctx.send(f"❌ **Terjadi kesalahan database:** `{e}`")

    @commands.command(name="ktp", aliases=["Ktp", "KTP"])
    async def ktp_command(self, ctx, target_input: str = None):
        try:
            target_user = None
            profile = None

            if not target_input:
                target_user = ctx.author
                profile = await database.get_ktp_profile(ctx.author.id)
            else:
                try:
                    target_user = await commands.MemberConverter().convert(ctx, target_input)
                    if target_user:
                        profile = await database.get_ktp_profile(target_user.id)
                except commands.BadArgument:
                    target_user = None

                if not profile:
                    profile = await database.get_ktp_profile(target_input)
                    if profile:
                        user_id = profile[0]
                        target_user = ctx.guild.get_member(user_id)
                        if not target_user:
                            try:
                                target_user = await self.bot.fetch_user(user_id)
                            except Exception:
                                target_user = ctx.author

            if not profile:
                await ctx.send(f"❌ Kamu belum memiliki KTP, Pergi ke ``!!lurah`` untuk membuat KTP", delete_after=10)
                return

            user_id = profile[0]
            stats = await database.get_all_event_stats(user_id)
            fans_count = await database.get_fans_count(user_id)
            purchased_titles = await database.get_user_title_inventory(user_id)

            unlocked_titles = [
                t_name for t_name, info in TITLE_MISSIONS.items()
                if info["check"](stats, fans_count)
            ]
            
            for p_title in purchased_titles:
                if p_title not in unlocked_titles:
                    unlocked_titles.append(p_title)

            display_user = target_user or ctx.author
            view = KTPView(ctx, display_user, profile, stats, fans_count, unlocked_titles)
            msg = await ctx.send(embed=view.build_page_1_embed(), view=view)
            view.message = msg

        except Exception as e:
            traceback.print_exc()
            await ctx.send(f"❌ **Gagal memuat KTP:** `{e}`")

    @commands.command(name="fans", aliases=["simp", "Simp", "Fans"])
    async def fans_command(self, ctx, target: discord.Member):
        if target.id == ctx.author.id:
            await ctx.send("⚠️ Mana bisa nge-simp ke diri sendiri, kocak! Tag member lain ya.", delete_after=10)
            return

        target_ktp = await database.get_ktp_profile(target.id)
        if not target_ktp:
            await ctx.send(f"❌ Member {target.mention} belum mendaftarkan KTP-nya di kelurahan!", delete_after=10)
            return

        success = await database.add_fan(target.id, ctx.author.id)
        if success:
            total_fans = await database.get_fans_count(target.id)
            embed = discord.Embed(
                title="💖 FANS BARU TERDETEKSI! 💖",
                description=f"Selamat {target.mention}! Kamu mendapatkan **+1 Fans** dari {ctx.author.mention}! 🎉\n\n📊 **Total Fans Saat Ini:** `{total_fans}` Fans",
                color=discord.Color.from_rgb(224, 170, 170)
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"⚠️ {ctx.author.mention}, kamu sudah terdaftar sebagai Fans dari {target.mention}!", delete_after=10)


async def setup(bot):
    await bot.add_cog(KTPCog(bot))