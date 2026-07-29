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
        title="📖 BUKU PANDUAN EVENT BOT YUNAN",
        description=(
            f"Halo {author.mention}! Selamat datang di Pusat Bantuan Bot Event.\n\n"
            "📌 **DAFTAR ISI PANDUAN:**\n"
            "🎙️ **Bab 1:** Sesi Panggung Karaoke Santai & Sajam Live\n"
            "🎲 **Bab 2:** Event Gacha Slot PPKM & Giveaway\n"
        ),
        color=THEME_COLOR
    )

    if has_mod:
        embed.description += (
            "⚙️ **Bab 3:** Pengelolaan Moderator & Database *(Khusus Staf)*\n"
        )

    embed.description += "\n💡 *Silakan pilih bab melalui menu dropdown di bawah!*"
    embed.set_thumbnail(url=author.display_avatar.url)
    embed.set_footer(text=f"Sistem Bantuan Bot Event • Prefix: {prefix}")
    return embed


class HelpDropdown(discord.ui.Select):
    def __init__(self, ctx):
        self.ctx = ctx
        self.has_mod = is_mod(ctx.author)

        options = [
            discord.SelectOption(label="Daftar Isi (Cover)", description="Menu utama & ringkasan bantuan.", emoji="📖", value="cover"),
            discord.SelectOption(label="Bab 1: Panggung & Voice", description="Antrean karaoke live & panggung Sajam.", emoji="🎙️", value="panggung"),
            discord.SelectOption(label="Bab 2: Gacha & Giveaway", description="Gacha slot event PPKM & event giveaway.", emoji="🎲", value="event"),
        ]

        if self.has_mod:
            options.append(discord.SelectOption(label="Bab 3: Staf Mod & Database", description="Filter gacha, backup SQLite, & monitoring bot.", emoji="⚙️", value="mod"))

        super().__init__(placeholder="📖 Pilih Bab Buku Panduan...", min_values=1, max_values=1, options=options)

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

            elif value == "panggung":
                embed = discord.Embed(
                    title="🎙️ Bab 1: Panggung Karaoke Santai & Sajam Live",
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
                if self.has_mod:
                    embed.add_field(
                        name="2️⃣ Sesi Resmi Sajam (Khusus Host/Mod)",
                        value=(
                            f"> `{prefix}sajam start` ➔ Memulai sesi Sajam di Voice Channel.\n"
                            f"> `{prefix}sajam` ➔ Recall / tampilkan ulang panel Sajam.\n"
                            f"> `{prefix}sajam end` ➔ Mengakhiri sesi dan merekap statistik panggung."
                        ),
                        inline=False
                    )

            elif value == "event":
                embed = discord.Embed(
                    title="🎲 Bab 2: Event Gacha Slot PPKM & Giveaway",
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
                            f"> `{prefix}giveaway` ➔ Buka form popup pembuat Giveaway.\n"
                            "└ *Form Modal mendukung Sponsor (Opsional) & Filter Role Whitelist (`@Role`) / Blacklist (`!@Role`) temporer.*"
                        ),
                        inline=False
                    )

            elif value == "mod" and self.has_mod:
                embed = discord.Embed(
                    title="⚙️ Bab 3: Pengelolaan Moderator & Database",
                    description="Fitur administrasi, monitoring hosting, dan database.",
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
                    name="2️⃣ Monitoring Sistem Hosting & DB",
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


class HelpCog(commands.Cog, name="Sistem Bantuan"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = build_cover_embed(ctx.author, ctx.prefix or "!!")
        view = HelpView(ctx)
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))