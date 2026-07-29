import discord
from discord.ext import commands, tasks
import math
import random
from core.database import database
from core.titles import SHOP_TITLES

ITEMS_PER_PAGE = 4

# Target rata-rata saldo ideal per warga (Rp 2.500.000)
BASELINE_TARGET_AVG = 2500000

async def get_inflation_data():
    """Fungsi Helper untuk menghitung Indeks Inflasi & Status Ekonomi Server."""
    total_m, avg_m, citizens = await database.get_macro_stats()
    
    if avg_m == 0:
        return 1.0, "STABIL 🟢", total_m, avg_m, citizens
    
    # Rasio perbandingan rata-rata saat ini vs baseline ideal
    ratio = avg_m / BASELINE_TARGET_AVG
    
    # Batasi faktor inflasi antara 0.75x (Diskon 25%) s/d 1.75x (Inflasi 75%)
    inflation_factor = max(0.75, min(1.75, ratio))
    
    if inflation_factor >= 1.35:
        status = "INFLASI TINGGI 🔥 (Harga Barang Naik)"
    elif inflation_factor >= 1.10:
        status = "INFLASI RINGAN 🟡 (Ekonomi Tumbuh)"
    elif inflation_factor <= 0.85:
        status = "RESESI / DEFLASI 🧊 (Toko Diskon)"
    else:
        status = "EKONOMI STABIL 🟢"
        
    return inflation_factor, status, total_m, avg_m, citizens


# --- DROPDOWNS TOKO DENGAN HARGA DINAMIS INFLASI ---

class ShopSelect(discord.ui.Select):
    def __init__(self, user_id: int, page_items: list, inflation_factor: float):
        self.user_id = user_id
        options = []
        for title, info in page_items:
            # HARGA DINAMIS DILAPISI INFLASI
            effective_price = int(info["price"] * inflation_factor)
            options.append(
                discord.SelectOption(
                    label=title,
                    value=title,
                    emoji=info["emoji"],
                    description=f"Rp {effective_price:,} • {info['desc']}"[:100]
                )
            )
        super().__init__(placeholder="🛒 Pilih Item / Title yang ingin dibeli...", min_values=1, max_values=1, options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ini panel toko milik orang lain!", ephemeral=True)
            return

        selected_title = self.values[0]
        item = SHOP_TITLES[selected_title]
        
        # Hitung harga efektif saat transaksi dilakukan
        inflation_factor, _, _, _, _ = await get_inflation_data()
        effective_price = int(item["price"] * inflation_factor)

        balance = await database.get_balance(self.user_id)
        if balance < effective_price:
            await interaction.response.send_message(
                f"❌ **Saldo Rupiah Kurang!**\n• Harga Pasar Saat Ini: **Rp {effective_price:,}**\n• Saldo Kamu: **Rp {balance:,}**",
                ephemeral=True
            )
            return

        if selected_title == "Kopi Suplemen Energi":
            energy, _ = await database.get_job_energy(self.user_id)
            if energy >= 5:
                await interaction.response.send_message("⚠️ **Energi Kerja Kamu Masih Penuh (5/5)!**", ephemeral=True)
                return

            await database.add_balance(self.user_id, -effective_price)
            await database.add_job_energy(self.user_id, 5)
            new_balance = balance - effective_price

            await interaction.response.send_message(
                f"☕ **SUPLEMEN DIBELI!** (Harga Pasar: Rp {effective_price:,})\n⚡ Energi Kerja Pulih ke (5/5)!\n💰 Sisa Saldo: `Rp {new_balance:,}`",
                ephemeral=True
            )
        else:
            inventory = await database.get_user_title_inventory(self.user_id)
            if selected_title in inventory:
                await interaction.response.send_message(f"⚠️ Kamu sudah memiliki Title **{selected_title}**!", ephemeral=True)
                return

            await database.add_balance(self.user_id, -effective_price)
            await database.add_title_to_inventory(self.user_id, selected_title)
            new_balance = balance - effective_price

            await interaction.response.send_message(
                f"🎉 **PEMBELIAN BERHASIL!**\nKamu membeli {item['emoji']} **{selected_title}** seharga **Rp {effective_price:,}**!\n💰 Sisa Saldo: `Rp {new_balance:,}`",
                ephemeral=True
            )

        self.view.balance = new_balance
        embed = await self.view.build_shop_embed()
        try:
            await interaction.message.edit(embed=embed, view=self.view)
        except Exception:
            pass


class ShopView(discord.ui.View):
    def __init__(self, user: discord.Member, balance: int, inflation_factor: float):
        super().__init__(timeout=180.0)
        self.user = user
        self.balance = balance
        self.inflation_factor = inflation_factor
        self.current_page = 1
        self.all_items = list(SHOP_TITLES.items())
        self.total_pages = math.ceil(len(self.all_items) / ITEMS_PER_PAGE)
        self.update_components()

    def get_current_page_items(self):
        start = (self.current_page - 1) * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        return self.all_items[start:end]

    def update_components(self):
        self.clear_items()
        page_items = self.get_current_page_items()
        self.add_item(ShopSelect(self.user.id, page_items, self.inflation_factor))
        
        prev_button = discord.ui.Button(emoji="◀️", style=discord.ButtonStyle.secondary, disabled=(self.current_page == 1), row=1)
        prev_button.callback = self.prev_page_callback
        self.add_item(prev_button)

        next_button = discord.ui.Button(emoji="▶️", style=discord.ButtonStyle.primary, disabled=(self.current_page == self.total_pages), row=1)
        next_button.callback = self.next_page_callback
        self.add_item(next_button)

    async def prev_page_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id: return
        if self.current_page > 1:
            self.current_page -= 1
            self.update_components()
            await interaction.response.edit_message(embed=await self.build_shop_embed(), view=self)

    async def next_page_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id: return
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_components()
            await interaction.response.edit_message(embed=await self.build_shop_embed(), view=self)

    async def build_shop_embed(self) -> discord.Embed:
        inf_factor, status, _, _, _ = await get_inflation_data()
        self.inflation_factor = inf_factor

        embed = discord.Embed(
            title="🏪 TOKO KELURAHAN MAHA5 🏪",
            description=(
                f"Selamat datang di Toko Kelurahan, {self.user.mention}!\n"
                f"📈 **Indeks Pasar:** `{int(inf_factor * 100)}%` ({status})\n\n"
                f"───────────────────────────────\n"
                f"💰 **Saldo Rupiah Kamu:** `Rp {self.balance:,}`\n"
                f"───────────────────────────────"
            ),
            color=discord.Color.from_rgb(214, 204, 224)
        )

        page_items = self.get_current_page_items()
        for title, info in page_items:
            base_price = info["price"]
            eff_price = int(base_price * inf_factor)
            
            price_note = f" *(Awal: Rp {base_price:,})*" if eff_price != base_price else ""

            embed.add_field(
                name=f"{info['emoji']} {title} — Rp {eff_price:,}{price_note}",
                value=f"> **Deskripsi:** {info['desc']}",
                inline=False
            )

        embed.set_footer(text=f"Halaman {self.current_page} dari {self.total_pages} • Toko Digital MAHA5", icon_url=self.user.display_avatar.url)
        return embed

class EconomyCog(commands.Cog, name="Sistem Ekonomi Rupiah"):
    def __init__(self, bot):
        self.bot = bot
        self.voice_reward_task.start()

    def cog_unload(self):
        self.voice_reward_task.cancel()

    @tasks.loop(minutes=15)
    async def voice_reward_task(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            for vc in guild.voice_channels:
                non_bot_members = [m for m in vc.members if not m.bot]
                if len(non_bot_members) < 2: continue

                for member in non_bot_members:
                    if member.voice and not member.voice.self_deaf and not member.voice.deaf:
                        ktp_profile = await database.get_ktp_profile(member.id)
                        if not ktp_profile: continue

                        reward = 15000
                        await database.add_balance(member.id, reward)
                        await database.log_activity(member.id, "vc_gaji", f"Gaji VC {vc.name} (+Rp 15k)")

    # --- DASHBOARD EKONOMI KELURAHAN (!!ekonomi) ---
    @commands.command(name="ekonomi", aliases=["bank", "inflasi", "pasar"])
    async def ekonomi_command(self, ctx):
        """Menampilkan laporan indikator ekonomi makro Kelurahan MAHA5."""
        inf_factor, status, total_m, avg_m, citizens = await get_inflation_data()
        
        embed = discord.Embed(
            title="📊 DASHBOARD EKONOMI MAKRO KELURAHAN 📊",
            description="Berikut indikator kesehatan ekonomi server saat ini secara realtime:\n",
            color=discord.Color.gold()
        )
        embed.add_field(name="📈 Status Pasar & Inflasi", value=f"> **{status}**\n> **Indeks Harga Toko:** `{int(inf_factor * 100)}%`", inline=False)
        embed.add_field(name="💰 Total Uang Beredar", value=f"> **Rp {total_m:,}**", inline=True)
        embed.add_field(name="🏛️ Rata-Rata Tabungan Warga", value=f"> **Rp {avg_m:,}** / warga", inline=True)
        embed.add_field(name="👥 Warga Terdaftar (KTP)", value=f"> **{citizens}** Jiwa", inline=True)

        embed.set_footer(text="Sistem Pengawas Ekonomi Makro • Kelurahan MAHA5", icon_url=ctx.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="saldo", aliases=["dompet", "bal", "money", "uang"])
    async def saldo_command(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        balance = await database.get_balance(target.id)

        embed = discord.Embed(
            title="💵 DOMPET DIGITAL MAHA5 💵",
            description=f"Informasi saldo keuangan untuk {target.mention}:\n\n> 💰 **Total Saldo:** `Rp {balance:,}`",
            color=discord.Color.from_rgb(173, 204, 173)
        )
        embed.set_footer(text="Ketik !!harian atau !!job untuk menambah saldomu!")
        await ctx.send(embed=embed)

    @commands.command(name="harian", aliases=["daily", "gaji"])
    async def daily_command(self, ctx):
        ktp_profile = await database.get_ktp_profile(ctx.author.id)
        if not ktp_profile:
            return await ctx.send("❌ Kamu belum mendaftarkan KTP! Ketik `!!lurah` terlebih dahulu.", delete_after=10)

        base_reward = random.randint(30000, 75000)
        
        # PAJAK PROGRESIF SULTAN (Jika Saldo > 10 Juta, Kena Pajak 10%)
        balance = await database.get_balance(ctx.author.id)
        tax = 0
        if balance > 10000000:
            tax = int(base_reward * 0.10)
            
        final_reward = base_reward - tax
        success, time_left = await database.claim_daily_reward(ctx.author.id, final_reward)

        if success:
            new_balance = await database.get_balance(ctx.author.id)
            tax_msg = f"\n⚠️ *Dipotong Pajak Sultan (10%): -Rp {tax:,}*" if tax > 0 else ""
            embed = discord.Embed(
                title="🎉 GAJI HARIAN DITERIMA! 🎉",
                description=(
                    f"Selamat {ctx.author.mention}! Kamu menerima gaji harian sebesar **Rp {final_reward:,}**!{tax_msg}\n\n"
                    f"💰 **Saldo Terbaru:** `Rp {new_balance:,}`"
                ),
                color=discord.Color.from_rgb(173, 204, 173)
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"⏳ {ctx.author.mention}, kamu sudah mengklaim gaji hari ini! Tunggu **{time_left}** lagi.", delete_after=10)

    @commands.command(name="pay", aliases=["tip", "transfer", "tf"])
    async def pay_command(self, ctx, target: discord.Member, amount: int):
        if target.id == ctx.author.id or target.bot or amount <= 0:
            return await ctx.send("❌ Transaksi tidak valid!", delete_after=10)

        sender_ktp = await database.get_ktp_profile(ctx.author.id)
        target_ktp = await database.get_ktp_profile(target.id)
        if not sender_ktp or not target_ktp:
            return await ctx.send("❌ Kedua pihak wajib memiliki KTP (`!!lurah`)!", delete_after=10)

        sender_balance = await database.get_balance(ctx.author.id)
        if sender_balance < amount:
            return await ctx.send("❌ Saldo Rupiah kamu tidak cukup!", delete_after=10)

        await database.add_balance(ctx.author.id, -amount)
        await database.add_balance(target.id, amount)

        embed = discord.Embed(
            title="💸 TRANSFER BERHASIL! 💸",
            description=f"{ctx.author.mention} mentransfer **Rp {amount:,}** kepada {target.mention}!\n💰 Sisa Saldo: `Rp {sender_balance - amount:,}`",
            color=discord.Color.from_rgb(173, 204, 173)
        )
        await ctx.send(embed=embed)

    @commands.command(name="toko", aliases=["shop", "store", "beli"])
    async def toko_command(self, ctx):
        balance = await database.get_balance(ctx.author.id)
        inf_factor, _, _, _, _ = await get_inflation_data()
        
        view = ShopView(ctx.author, balance, inf_factor)
        embed = await view.build_shop_embed()
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(EconomyCog(bot))