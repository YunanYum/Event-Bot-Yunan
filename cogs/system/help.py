import discord
from discord.ext import commands
import traceback

THEME_COLOR = discord.Color.from_rgb(214, 204, 224)

def is_mod(author) -> bool:
    if isinstance(author, discord.Member):
        return author.guild_permissions.manage_guild
    return False


def build_cover_embed(author, prefix: str) -> discord.Embed:
    has_mod = is_mod(author)
    
    embed = discord.Embed(
        title="📖 BUKU SAKU WARGA & PANDUAN KELURAHAN MAHA5",
        description=(
            f"Halo {author.mention}! Selamat datang di Pusat Informasi Bot Kelurahan MAHA5.\n"
            "Buku panduan ini berisi seluruh petunjuk kerja, identitas warga, sistem ekonomi makro, panggung hiburan, dan aturan kelurahan.\n\n"
            "📌 **DAFTAR ISI BUKU SAKU:**\n"
            "🪪 **Bab 1:** Identitas Warga & KTP Digital\n"
            "🧩 **Bab 2:** Bursa Kerja Puzzle Realtime (5 Shift/Hari)\n"
            "📊 **Bab 3:** Ekonomi Makro, Bank & Toko Kelurahan\n"
            "📜 **Bab 4:** Sistem Misi & Title Pencapaian\n"
            "🎙️ **Bab 5:** Panggung Karaoke Santai & Voice Backstage\n"
            "🎲 **Bab 6:** Event Gacha Slot PPKM & Giveaway\n"
        ),
        color=THEME_COLOR
    )

    if has_mod:
        embed.description += (
            "⚙️ **Bab 7:** Pengelolaan Moderator & Database *(Khusus Staf)*\n"
        )

    embed.description += "\n💡 *Silakan pilih bab yang ingin dibaca melalui menu dropdown di bawah!*"
    embed.set_thumbnail(url=author.display_avatar.url)
    embed.set_footer(text=f"Sistem Bantuan Terpadu MAHA5 • Prefix: {prefix}")
    return embed


class HelpDropdown(discord.ui.Select):
    def __init__(self, ctx):
        self.ctx = ctx
        self.has_mod = is_mod(ctx.author)

        options = [
            discord.SelectOption(label="Daftar Isi (Cover)", description="Menu utama & ringkasan seluruh sistem bot.", emoji="📖", value="cover"),
            discord.SelectOption(label="Bab 1: KTP Digital & Fans", description="Pendaftaran KTP, NIM unik, & apresiasi Simp.", emoji="🪪", value="ktp"),
            discord.SelectOption(label="Bab 2: Bursa Kerja Puzzle", description="5 Mini-game puzzle kerja, energi, & gaji dinamis.", emoji="🧩", value="kerja"),
            discord.SelectOption(label="Bab 3: Ekonomi & Toko", description="Indeks inflasi, gaji VC, transfer, & Kopi Energi.", emoji="📊", value="ekonomi"),
            discord.SelectOption(label="Bab 4: Misi & Title", description="Cara unlock Title & pasang Oshi VTuber.", emoji="📜", value="misi"),
            discord.SelectOption(label="Bab 5: Panggung & Voice", description="Antrean karaoke live multi-room & vote skip.", emoji="🎙️", value="panggung"),
            discord.SelectOption(label="Bab 6: Gacha & Giveaway", description="Gacha slot event PPKM & event giveaway.", emoji="🎲", value="event"),
        ]

        if self.has_mod:
            options.append(discord.SelectOption(label="Bab 7: Staf Mod & Database", description="Filter gacha, backup SQLite, & monitoring bot.", emoji="⚙️", value="mod"))

        super().__init__(placeholder="📖 Pilih Bab Buku Saku Warga...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != self.ctx.author.id:
                await interaction.response.send_message("❌ Ini buku panduan milik orang lain. Ketik `!!help` sendiri ya!", ephemeral=True)
                return

            value = self.values[0]
            prefix = self.ctx.prefix or "!!"
            embed = None

            if value == "cover":
                embed = build_cover_embed(self.ctx.author, prefix)

            elif value == "ktp":
                embed = discord.Embed(
                    title="🪪 Bab 1: Identitas Warga & KTP Digital",
                    description="Panduan pendaftaran identitas resmi Kelurahan MAHA5.",
                    color=THEME_COLOR
                )
                embed.add_field(
                    name="1️⃣ Pendaftaran KTP di Kantor Kelurahan (Wajib)",
                    value=f"> `{prefix}lurah` ➔ Buka formulir Popup Pak Lurah untuk pendaftaran/revisi KTP.\n*(Catatan: KTP wajib dimiliki untuk bisa bekerja & mengklaim gaji!)*",
                    inline=False
                )
                embed.add_field(
                    name="2️⃣ Menampilkan KTP Digital & Kartu Panggung",
                    value=(
                        f"> `{prefix}ktp` ➔ Lihat KTP milik sendiri.\n"
                        f"> `{prefix}ktp @Member` ➔ Lihat KTP member lain.\n"
                        f"> `{prefix}ktp M5-0000-0001` ➔ Cek KTP via NIM Unik.\n"
                        "*(Gunakan tombol `▶️` untuk pindah ke Kartu Panggung, dan `⚙️` untuk pasang Title & Oshi VTuber!)*"
                    ),
                    inline=False
                )
                embed.add_field(
                    name="3️⃣ Apresiasi Fans / Simp",
                    value=f"> `{prefix}simp @Member` atau `{prefix}fans @Member` ➔ Berikan **+1 Fans** ke member favoritmu!",
                    inline=False
                )

            elif value == "kerja":
                embed = discord.Embed(
                    title="🧩 Bab 2: Bursa Kerja Puzzle Realtime",
                    description="Sistem pekerjaan interaktif untuk menghasilkan Rupiah ekstra.",
                    color=THEME_COLOR
                )
                embed.add_field(
                    name="1️⃣ Memulai Pekerjaan (`!!job`)",
                    value=(
                        f"> `{prefix}job` atau `{prefix}pekerjaan` ➔ Buka pusat kerja puzzle interaktif!\n"
                        "⚡ **Energi Kerja:** 5 Shift / 24 Jam (Reset otomatis setiap hari)."
                    ),
                    inline=False
                )
                embed.add_field(
                    name="2️⃣ Daftar 5 Mini-Game Puzzle",
                    value=(
                        "🛵 **Driver Ojol:** Puzzle Navigasi GPS & Manajemen Bensin.\n"
                        "🍳 **Koki Warteg:** Puzzle Suhu Wajan IDEAL (180°C - 220°C).\n"
                        "🅿️ **Tukang Parkir:** Puzzle Logika Unblock Evakuasi Parkiran.\n"
                        "💵 **Kasir Merch:** Puzzle Trik Kembalian Pecahan Bulat.\n"
                        "☕ **Barista Kopi:** Puzzle Riddle Racikan Kopi 3 Layer."
                    ),
                    inline=False
                )
                embed.add_field(
                    name="3️⃣ Hukum Demand & Supply Gaji",
                    value=(
                        "📉 **Banjir Pekerja:** Job yang sering di-spam gajinya **turun (-20%)**.\n"
                        "🚀 **Pekerjaan Langka:** Job yang jarang dimainkan dapat **bonus (+30% Gaji)**!"
                    ),
                    inline=False
                )

            elif value == "ekonomi":
                embed = discord.Embed(
                    title="📊 Bab 3: Ekonomi Makro, Bank & Toko Kelurahan",
                    description="Sistem keuangan dinamis yang bergerak mengikuti kondisi pasar server.",
                    color=THEME_COLOR
                )
                embed.add_field(
                    name="1️⃣ Dashboard Pasar & Inflasi",
                    value=f"> `{prefix}ekonomi` atau `{prefix}bank` ➔ Cek Indeks Inflasi server, total uang beredar, dan status pasar (Inflasi vs Resesi Diskon).",
                    inline=False
                )
                embed.add_field(
                    name="2️⃣ Keuangan & Transfer",
                    value=(
                        f"> `{prefix}harian` atau `{prefix}gaji` ➔ Klaim gaji harian (Rp 30k - 75k).\n"
                        f"> `{prefix}saldo` atau `{prefix}dompet` ➔ Cek jumlah tabungan Rupiah.\n"
                        f"> `{prefix}pay @Member [jumlah]` ➔ Transfer / kirim uang tip ke warga lain.\n"
                        "⚠️ *Pajak Sultan Progresif (10%) berlaku untuk warga ber-saldo > Rp 10 Juta!*"
                    ),
                    inline=False
                )
                embed.add_field(
                    name="3️⃣ Gaji Pasif Nongkrong Voice Channel (VC Mining)",
                    value="> Otomatis mendapatkan **Rp 15.000 / 15 menit** hanya dengan nongkrong aktif di VC *(Syarat: minimal 2 orang di VC, ber-KTP, dan tidak Deafen)*.",
                    inline=False
                )
                embed.add_field(
                    name="4️⃣ Toko Kelurahan MAHA5 (`!!toko`)",
                    value=(
                        f"> `{prefix}toko` atau `{prefix}shop` ➔ Belanja Title Kosmetik berjenjang & **☕ Kopi Suplemen Energi** *(Pulihkan +5 Energi Kerja secara instan!)*."
                    ),
                    inline=False
                )

            elif value == "misi":
                embed = discord.Embed(
                    title="📜 Bab 4: Sistem Misi & Title Pencapaian",
                    description="Sistem unlock Title KTP berdasarkan keaktifan event & panggung.",
                    color=THEME_COLOR
                )
                embed.add_field(
                    name="1️⃣ Mengecek Progress Misi",
                    value=f"> `{prefix}misi` atau `{prefix}title` ➔ Lihat katalog status Title yang **✅ TERBUKA** atau **🔒 TERKUNCI**.",
                    inline=False
                )
                embed.add_field(
                    name="2️⃣ Cara Memasang Title & Oshi VTuber",
                    value=(
                        f"1. Buka `{prefix}ktp` milikmu.\n"
                        "2. Tekan tombol `▶️` untuk pindah ke **Halaman 2 (Kartu Panggung)**.\n"
                        "3. Klik tombol `⚙️` lalu pilih **Title** dan **Oshi VTuber** dari menu dropdown!"
                    ),
                    inline=False
                )

            elif value == "panggung":
                embed = discord.Embed(
                    title="🎙️ Bab 5: Panggung Karaoke Santai & Voice Backstage",
                    description="Aktivitas jamming live dan antrean bernyanyi otomatis.",
                    color=THEME_COLOR
                )
                embed.add_field(
                    name="1️⃣ Sesi Karaoke Santai (Multi-Room)",
                    value=(
                        f"> `{prefix}q` atau `{prefix}queue` ➔ Tampilkan Panel Panggung Karaoke.\n"
                        f"> Perintah Cepat: `{prefix}qj` (Join) | `{prefix}ql` (Keluar) | `{prefix}qd` (Selesai) | `{prefix}qskip` (Vote Skip)."
                    ),
                    inline=False
                )
                embed.add_field(
                    name="2️⃣ Demokrasi Lengser (Vote Skip)",
                    value="> Jika penyanyi di panggung *stuck*, warga VC bisa menekan tombol **⏩ Lengserkan** (Membutuhkan ¼ vote dari total warga VC).",
                    inline=False
                )

            elif value == "event":
                embed = discord.Embed(
                    title="🎲 Bab 6: Event Gacha Slot PPKM & Giveaway",
                    description="Partisipasi undian slot penampilan dan pembagian hadiah.",
                    color=THEME_COLOR
                )
                embed.add_field(
                    name="1️⃣ Cara Ikut Gacha & Giveaway",
                    value=(
                        "• **Gacha PPKM:** Tekan tombol **Ikutan Gacha** saat panel dibuka.\n"
                        "• **Giveaway:** Tekan tombol **Ikutan Giveaway 🎁** pada pesan event."
                    ),
                    inline=False
                )
                if self.has_mod:
                    embed.add_field(
                        name="2️⃣ Perintah Penyelenggara (Khusus Staf)",
                        value=(
                            f"> `{prefix}ppkm [slot] [durasi] [channel]` ➔ Buat undian slot event.\n"
                            f"> `{prefix}reroll` ➔ Kocok ulang pemenang gacha PPKM.\n"
                            f"> `{prefix}giveaway` ➔ Buka form popup pembuat Giveaway."
                        ),
                        inline=False
                    )

            elif value == "mod" and self.has_mod:
                embed = discord.Embed(
                    title="⚙️ Bab 7: Pengelolaan Moderator & Database",
                    description="Fitur administrasi dan pemeliharaan data kelurahan.",
                    color=THEME_COLOR
                )
                embed.add_field(
                    name="1️⃣ Filter Access Control PPKM",
                    value=(
                        f"> `{prefix}ppkmconfig` ➔ Panel interaktif kelola filter Role & User.\n"
                        f"> `{prefix}blacklist @Role` | `{prefix}whitelist @Role` | `{prefix}userblacklist @User`"
                    ),
                    inline=False
                )
                embed.add_field(
                    name="2️⃣ Manajemen Database SQLite & Hosting",
                    value=(
                        f"> `{prefix}bot` ➔ Monitoring CPU, RAM, Disk Hosting, dan Latency Ping.\n"
                        f"> `{prefix}db backup` ➔ Backup manual database.\n"
                        f"> `{prefix}db list` ➔ Lihat daftar file cadangan.\n"
                        f"> `{prefix}db restore [nama_file.db]` ➔ Pulihkan database aman."
                    ),
                    inline=False
                )

            if embed:
                selected_label = next((o.label for o in self.options if o.value == value), "Panduan")
                embed.set_footer(text=f"Halaman: {selected_label} | Prefix: {prefix}")
                await interaction.response.edit_message(embed=embed, view=self.view)

        except Exception as e:
            print(f"[ERROR HELP DROPDOWN] {e}")
            traceback.print_exc()
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ **Terjadi kesalahan:** `{e}`", ephemeral=True)


class HelpView(discord.ui.View):
    def __init__(self, ctx, timeout=180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.add_item(HelpDropdown(ctx))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class HelpCog(commands.Cog, name="Sistem Bantuan Kelurahan"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = build_cover_embed(ctx.author, ctx.prefix or "!!")
        view = HelpView(ctx)
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))