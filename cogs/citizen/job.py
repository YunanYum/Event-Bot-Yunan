import discord
from discord.ext import commands
import asyncio
import random
from datetime import datetime
from core.database import database

THEME_COLOR = discord.Color.from_rgb(214, 204, 224)

# ==========================================
# 🔄 TOMBOL KEMBALI KE MENU UTAMA
# ==========================================
class BackToMenuButton(discord.ui.Button):
    def __init__(self, cog, author: discord.User):
        super().__init__(label="Kembali ke Menu Kerja", emoji="🔄", style=discord.ButtonStyle.primary)
        self.cog = cog
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Ini menu pekerjaan orang lain!", ephemeral=True)
            return

        await interaction.response.defer()
        await self.cog.show_main_job_panel(interaction.message, self.author)


# ==========================================
# 🛵 1. PUZZLE OJOL (GPS & BENSIN)
# ==========================================
class OjolGameView(discord.ui.View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=30.0)
        self.author = author
        self.fuel = 100
        self.choice = None

    @discord.ui.button(label="Gang Sempit (-20% Bensin | Cepat)", emoji="🛣️", style=discord.ButtonStyle.primary, row=0)
    async def alley(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return
        self.fuel -= 20
        self.choice = "gang"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Jalan Utama (-50% Bensin | Macet)", emoji="🚗", style=discord.ButtonStyle.secondary, row=0)
    async def main_road(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return
        self.fuel -= 50
        self.choice = "macet"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Jalan Tol Toll Rp 5k (-10% Bensin | Cepat)", emoji="🛣️", style=discord.ButtonStyle.success, row=1)
    async def toll(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return
        self.fuel -= 10
        self.choice = "tol"
        self.stop()
        await interaction.response.defer()


# ==========================================
# 🍳 2. PUZZLE WARTEG (KONTROL SUHU WAJAN)
# ==========================================
class WartegPuzzleView(discord.ui.View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=30.0)
        self.author = author
        self.temp = 100  # Suhu awal 100°C
        self.is_done = False

    @discord.ui.button(label="🔥 Besarkan Api (+50°C)", style=discord.ButtonStyle.danger, row=0)
    async def heat_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return
        self.temp += 50
        await self.update_status(interaction)

    @discord.ui.button(label="🔉 Kecilkan Api (-30°C)", style=discord.ButtonStyle.secondary, row=0)
    async def heat_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return
        self.temp = max(50, self.temp - 30)
        await self.update_status(interaction)

    @discord.ui.button(label="🍳 ANGKAT MENDOAN!", style=discord.ButtonStyle.success, row=1)
    async def lift(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return
        self.is_done = True
        self.stop()
        await interaction.response.defer()

    async def update_status(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        status = "🟦 DINGIN" if self.temp < 180 else ("🟩 IDEAL" if self.temp <= 220 else "🟥 SANGAT PANAS / GOSONG")
        embed.description = f"⚠️ **Target Suhu:** `180°C - 220°C (IDEAL)`\n\n🔥 **Suhu Wajan Saat Ini:** `{self.temp}°C` **[{status}]**"
        await interaction.response.edit_message(embed=embed, view=self)


# ==========================================
# 🅿️ 3. PUZZLE PARKIR (LOGIKA UNBLOCK)
# ==========================================
class ParkirPuzzleView(discord.ui.View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=25.0)
        self.author = author
        self.step = 1
        self.is_failed = False
        self.is_success = False

    @discord.ui.button(label="1️⃣ Geser Motor", style=discord.ButtonStyle.primary, row=0)
    async def move_motor(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return
        if self.step == 1:
            self.step = 2
            embed = interaction.message.embeds[0]
            embed.description = "✅ Motor berhasil digeser! Sekarang jalan Bajaj terbuka.\n\n👉 **Langkah 2:** Pilih kendaraan berikutnya yang harus digeser!"
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            self.is_failed = True
            self.stop()
            await interaction.response.defer()

    @discord.ui.button(label="2️⃣ Geser Bajaj", style=discord.ButtonStyle.primary, row=0)
    async def move_bajaj(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return
        if self.step == 2:
            self.step = 3
            embed = interaction.message.embeds[0]
            embed.description = "✅ Bajaj berhasil digeser! Jalur Alphard kini sepenuhnya bersih!\n\n👉 **Langkah 3:** Arahkan Alphard maju keluar!"
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            self.is_failed = True
            self.stop()
            await interaction.response.defer()

    @discord.ui.button(label="3️⃣ Alphard Maju Keluar", style=discord.ButtonStyle.success, row=1)
    async def move_car(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return
        if self.step == 3:
            self.is_success = True
            self.stop()
            await interaction.response.defer()
        else:
            self.is_failed = True
            self.stop()
            await interaction.response.defer()


# ==========================================
# 💵 4. PUZZLE KASIR (TRIK KEMBALIAN)
# ==========================================
class KasirPuzzleView(discord.ui.View):
    def __init__(self, author: discord.User, correct_answer: int):
        super().__init__(timeout=25.0)
        self.author = author
        self.correct_answer = correct_answer
        self.chosen = None

    async def check_answer(self, interaction: discord.Interaction, val: int):
        if interaction.user.id != self.author.id: return
        self.chosen = val
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Rp 20.000", style=discord.ButtonStyle.primary, row=0)
    async def ans1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 20000)

    @discord.ui.button(label="Rp 17.500", style=discord.ButtonStyle.secondary, row=0)
    async def ans2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 17500)

    @discord.ui.button(label="Rp 22.500", style=discord.ButtonStyle.secondary, row=1)
    async def ans3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 22500)

    @discord.ui.button(label="Rp 10.000", style=discord.ButtonStyle.secondary, row=1)
    async def ans4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 10000)


# ==========================================
# ☕ 5. PUZZLE BARISTA (RECIPE RIDDLE 3 LAYER)
# ==========================================
class BaristaLayerPuzzleView(discord.ui.View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=30.0)
        self.author = author
        self.layer1 = None
        self.layer2 = None
        self.layer3 = None
        self.step = 1

    async def advance_layer(self, interaction: discord.Interaction, val: str):
        if interaction.user.id != self.author.id: return
        
        if self.step == 1:
            self.layer1 = val
            self.step = 2
            self.clear_items()
            b1 = discord.ui.Button(label="Susu Fresh Milk 🥛", style=discord.ButtonStyle.primary)
            b2 = discord.ui.Button(label="Sirup Sirsak 🧃", style=discord.ButtonStyle.secondary)
            async def cb1(i): await self.advance_layer(i, "Susu Fresh Milk")
            async def cb2(i): await self.advance_layer(i, "Sirup Sirsak")
            b1.callback = cb1; b2.callback = cb2
            self.add_item(b1); self.add_item(b2)

            embed = interaction.message.embeds[0]
            embed.description = "✅ **Layer 1 Terpasang!** Sekarang pilih bahan untuk **LAPISAN TENGAH (LAYER 2)**!"
            await interaction.response.edit_message(embed=embed, view=self)

        elif self.step == 2:
            self.layer2 = val
            self.step = 3
            self.clear_items()
            b1 = discord.ui.Button(label="Es Batu Kopyor 🧊", style=discord.ButtonStyle.primary)
            b2 = discord.ui.Button(label="Keju Parut 🧀", style=discord.ButtonStyle.secondary)
            async def cb1(i): await self.advance_layer(i, "Es Batu Kopyor")
            async def cb2(i): await self.advance_layer(i, "Keju Parut")
            b1.callback = cb1; b2.callback = cb2
            self.add_item(b1); self.add_item(b2)

            embed = interaction.message.embeds[0]
            embed.description = "✅ **Layer 2 Terpasang!** Terakhir, pilih topping untuk **LAPISAN ATAS (LAYER 3)**!"
            await interaction.response.edit_message(embed=embed, view=self)

        elif self.step == 3:
            self.layer3 = val
            self.stop()
            await interaction.response.defer()

    @discord.ui.button(label="Gula Aren 🍯", style=discord.ButtonStyle.primary, row=0)
    async def l1_gula(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.advance_layer(interaction, "Gula Aren")

    @discord.ui.button(label="Espresso ☕", style=discord.ButtonStyle.secondary, row=0)
    async def l1_espresso(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.advance_layer(interaction, "Espresso")


# ==========================================
# 📄 MAIN MENU SELECTOR (MENU UTAMA JOB)
# ==========================================
class JobMainSelect(discord.ui.Select):
    def __init__(self, cog, author: discord.User):
        self.cog = cog
        self.author = author
        options = [
            discord.SelectOption(label="Driver Ojek Online", emoji="🛵", description="Puzzle GPS Navigasi & Manajemen Bensin!"),
            discord.SelectOption(label="Koki Warteg", emoji="🍳", description="Puzzle Suhu Wajan & Kontrol Api Gorengan!"),
            discord.SelectOption(label="Tukang Parkir", emoji="🅿️", description="Puzzle Logika Unblock Evakuasi Parkiran!"),
            discord.SelectOption(label="Kasir Minimarket", emoji="💵", description="Puzzle Trik Matematika Kembalian Cerdas!"),
            discord.SelectOption(label="Barista Kopi", emoji="☕", description="Puzzle Riddle Racikan Kopi 3 Layer!")
        ]
        super().__init__(placeholder="🛠️ Pilih Pekerjaan Puzzle yang ingin dimainkan...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Ini menu pekerjaan orang lain! Ketik `!!job` sendiri.", ephemeral=True)
            return

        selected_job = self.values[0]

        has_energy = await database.consume_job_energy(self.author.id)
        if not has_energy:
            await interaction.response.send_message("❌ **Energi Kerja Kamu Habis!** Tunggu reset besok atau beli Kopi Suplemen di `!!toko`!", ephemeral=True)
            return

        await interaction.response.defer()

        if selected_job == "Driver Ojek Online":
            await self.cog.start_ojol_puzzle(interaction, self.author)
        elif selected_job == "Koki Warteg":
            await self.cog.start_warteg_puzzle(interaction, self.author)
        elif selected_job == "Tukang Parkir":
            await self.cog.start_parkir_puzzle(interaction, self.author)
        elif selected_job == "Kasir Minimarket":
            await self.cog.start_kasir_puzzle(interaction, self.author)
        elif selected_job == "Barista Kopi":
            await self.cog.start_barista_puzzle(interaction, self.author)

class JobMainView(discord.ui.View):
    def __init__(self, cog, author: discord.User):
        super().__init__(timeout=120.0)
        self.add_item(JobMainSelect(cog, author))


# ==========================================
# 🎮 COG MAIN CLASS (PUZZLE ENGINE)
# ==========================================
class JobCog(commands.Cog, name="Sistem Pekerjaan Realtime"):
    def __init__(self, bot):
        self.bot = bot

    # --- HITUNG GAJI DINAMIS (PASAR DEMAND & SUPPLY) ---
    async def calculate_dynamic_salary(self, job_name: str, base_salary: int) -> tuple[int, str]:
        """Menghitung gaji berdasarkan hukum Penawaran & Permintaan (Demand/Supply) 24 Jam."""
        demand_data = await database.get_job_demand_stats()
        count = demand_data.get(job_name, 0)
        
        if count >= 15:
            multiplier = 0.80  # Gaji Turun 20%
            note = "\n📉 *Pasar Kebanjiran Pekerja (-20% Gaji)*"
        elif count <= 3:
            multiplier = 1.30  # Gaji Bonus +30%
            note = "\n🚀 *Pekerjaan Langka / High Demand (+30% Bonus Gaji)!*"
        else:
            multiplier = 1.0
            note = "\n⚖️ *Gaji Pasar Normal*"
            
        final_salary = int(base_salary * multiplier)
        return final_salary, note

    async def show_main_job_panel(self, message_or_ctx, author: discord.User):
        """Helper untuk menampilkan/mengedit panel utama pekerjaan (Dengan Pengecekan KTP)."""
        ktp_profile = await database.get_ktp_profile(author.id)
        if not ktp_profile:
            embed = discord.Embed(
                title="🏛️ DITOLAK OLEH PAK LURAH! 👴",
                description=(
                    f"Walah {author.mention}! Kamu belum terdaftar sebagai warga resmi di Kelurahan MAHA5!\n\n"
                    "👴 **Pak Lurah:** *\"Bocah ini mau lamar kerja tapi KTP aja belum punya! Sana pergi ke **!!lurah** buat KTP dulu baru boleh cari rejeki!\"*\n\n"
                    "👉 Ketik `!!lurah` untuk mengisi formulir KTP Digital kamu!"
                ),
                color=discord.Color.red()
            )
            if isinstance(message_or_ctx, discord.Message):
                await message_or_ctx.edit(embed=embed, view=None)
            else:
                await message_or_ctx.send(embed=embed)
            return

        energy, time_left = await database.get_job_energy(author.id)
        energy_bar = "⚡" * energy + "⚪" * (5 - energy)

        embed = discord.Embed(
            title="🏢 PUSAT PEKERJAAN PUZZLE MAHA5 🏢",
            description=(
                f"Halo {author.mention}! Siap asah otak sambil mencari Rupiah ekstra?\n"
                "Pilih salah satu mini-game puzzle pekerjaan di bawah ini!\n\n"
                f"───────────────────────────────\n"
                f"🔋 **Energi Kerja Hari Ini:** {energy_bar} `({energy}/5 Shift)`\n"
                f"{f'⏳ *Reset energi dalam: {time_left}*' if energy < 5 else '✨ *Energi penuh! Ready untuk kerja!*'}\n"
                f"───────────────────────────────"
            ),
            color=THEME_COLOR
        )
        embed.set_footer(text="Setiap pekerjaan membutuhkan 1 Energi Kerja.", icon_url=author.display_avatar.url)

        view = JobMainView(self, author)
        if isinstance(message_or_ctx, discord.Message):
            await message_or_ctx.edit(embed=embed, view=view)
        else:
            await message_or_ctx.send(embed=embed, view=view)

    @commands.command(name="job", aliases=["pekerjaan", "kerja"])
    async def job_command(self, ctx):
        await self.show_main_job_panel(ctx, ctx.author)

    # --- 1. PUZZLE OJOL ---
    async def start_ojol_puzzle(self, interaction: discord.Interaction, user: discord.User):
        panel_msg = interaction.message
        view = OjolGameView(user)

        embed = discord.Embed(
            title="🛵 OJOL PUZZLE: Navigasi GPS & Bensin",
            description="📍 **Tujuan:** Stasiun Kereta\n⛽ **Bensin:** `100%`\n\n⚠️ **Persimpangan 1:** Jalan utama macet total! Pilih rute terbaik agar bensin tidak habis di jalan!",
            color=discord.Color.gold()
        )
        await panel_msg.edit(embed=embed, view=view)
        await view.wait()

        # Catat aktivitas untuk pasar demand/supply
        await database.log_activity(user.id, "job_exec", "Driver Ojek Online")

        base_reward = 0
        if view.choice == "tol":
            base_reward = 60000
            res_text = f"🎉 **Navigasi Cerdas!** Lewat tol tepat waktu dengan sisa Bensin {view.fuel}%!"
            color = discord.Color.green()
        elif view.choice == "gang":
            base_reward = 40000
            res_text = f"👍 **Berhasil Lolos!** Lewat gang agak memutar tapi selamat. Sisa Bensin {view.fuel}%."
            color = discord.Color.gold()
        else:
            res_text = "😭 **BENSIN HABIS DI JALAN!** Terjebak macet 2 jam, penumpang batalkan pesanan! (Rp 0)"
            color = discord.Color.red()

        if base_reward > 0:
            reward, market_note = await self.calculate_dynamic_salary("Driver Ojek Online", base_reward)
            await database.add_balance(user.id, reward)
            res_text += f"\n\n💰 **Gaji Diterima:** `Rp {reward:,}` {market_note}"

        result_view = discord.ui.View(timeout=120)
        result_view.add_item(BackToMenuButton(self, user))
        res_embed = discord.Embed(title="🏁 OJOL: Hasil Perjalanan", description=res_text, color=color)
        await panel_msg.edit(embed=res_embed, view=result_view)

    # --- 2. PUZZLE WARTEG ---
    async def start_warteg_puzzle(self, interaction: discord.Interaction, user: discord.User):
        panel_msg = interaction.message
        view = WartegPuzzleView(user)

        embed = discord.Embed(
            title="🍳 WARTEG PUZZLE: Kontrol Suhu Wajan",
            description="⚠️ **Target Suhu:** `180°C - 220°C (IDEAL)`\n\n🔥 **Suhu Wajan Saat Ini:** `100°C` **[🟦 DINGIN]**\n\nAtur tombol api agar suhu wajan masuk zona IDEAL sebelum diangkat!",
            color=discord.Color.gold()
        )
        await panel_msg.edit(embed=embed, view=view)
        await view.wait()

        await database.log_activity(user.id, "job_exec", "Koki Warteg")

        base_reward = 0
        if 180 <= view.temp <= 220:
            base_reward = 65000
            res_text = f"🎉 **MATANG SEMPURNA!** Suhu wajan tepat di {view.temp}°C! Mendoan garing pas!"
            color = discord.Color.green()
        elif 120 <= view.temp < 180:
            base_reward = 20000
            res_text = f"😐 **AGAK MENTAH!** Suhu cuma {view.temp}°C."
            color = discord.Color.orange()
        else:
            res_text = f"😭 **GOSONG / HANGUS!** Suhu mencapai {view.temp}°C! Mendoan berubah jadi arang! (Rp 0)"
            color = discord.Color.red()

        if base_reward > 0:
            reward, market_note = await self.calculate_dynamic_salary("Koki Warteg", base_reward)
            await database.add_balance(user.id, reward)
            res_text += f"\n\n💰 **Gaji Diterima:** `Rp {reward:,}` {market_note}"

        result_view = discord.ui.View(timeout=120)
        result_view.add_item(BackToMenuButton(self, user))
        res_embed = discord.Embed(title="🍳 WARTEG: Hasil Masakan", description=res_text, color=color)
        await panel_msg.edit(embed=res_embed, view=result_view)

    # --- 3. PUZZLE PARKIR ---
    async def start_parkir_puzzle(self, interaction: discord.Interaction, user: discord.User):
        panel_msg = interaction.message
        view = ParkirPuzzleView(user)

        embed = discord.Embed(
            title="🅿️ PARKIR PUZZLE: Unblock Evakuasi",
            description=(
                "🚙 **Situasi:** Mobil [Alphard] mau keluar, tapi terhalang [Bajaj], dan [Bajaj] terhalang [Motor]!\n\n"
                "👉 **Langkah 1:** Urutkan kendaraan yang HARUS digeser pertama kali!"
            ),
            color=discord.Color.gold()
        )
        await panel_msg.edit(embed=embed, view=view)
        await view.wait()

        await database.log_activity(user.id, "job_exec", "Tukang Parkir")

        base_reward = 0
        if view.is_success:
            base_reward = 50000
            res_text = f"🎉 **EVAKUASI SUKSES!** Urutan geser tepat, Alphard mulus keluar tanpa lecet!"
            color = discord.Color.green()
        else:
            res_text = "💥 **BRET!!** Salah urutan geser! Bajaj menabrak Alphard hingga lecet! (Rp 0)"
            color = discord.Color.red()

        if base_reward > 0:
            reward, market_note = await self.calculate_dynamic_salary("Tukang Parkir", base_reward)
            await database.add_balance(user.id, reward)
            res_text += f"\n\n💰 **Gaji Diterima:** `Rp {reward:,}` {market_note}"

        result_view = discord.ui.View(timeout=120)
        result_view.add_item(BackToMenuButton(self, user))
        res_embed = discord.Embed(title="🅿️ PARKIR: Hasil Evakuasi", description=res_text, color=color)
        await panel_msg.edit(embed=res_embed, view=result_view)

    # --- 4. PUZZLE KASIR ---
    async def start_kasir_puzzle(self, interaction: discord.Interaction, user: discord.User):
        panel_msg = interaction.message
        view = KasirPuzzleView(user, correct_answer=20000)

        embed = discord.Embed(
            title="💵 KASIR PUZZLE: Trik Kembalian Cerdas",
            description=(
                "🛒 **Total Belanja:** `Rp 32.500`\n"
                "💵 **Uang Pembeli:** `Rp 52.500` *(1 lembar 50rb + 1 lembar 2rb + 1 koin 500)*\n\n"
                "❓ **Pertanyaan:** Pembeli sengaja memberi pecahan tersebut agar mendapat lembar kembalian bulat. Berapa kembalian pas yang HARUS kamu serahkan?"
            ),
            color=discord.Color.gold()
        )
        await panel_msg.edit(embed=embed, view=view)
        await view.wait()

        await database.log_activity(user.id, "job_exec", "Kasir Minimarket")

        base_reward = 0
        if view.chosen == 20000:
            base_reward = 55000
            res_text = f"🎉 **MATEMATIKA CERDAS!** Kembalian Rp 20.000 bulat pas! Pembeli kagum!"
            color = discord.Color.green()
        else:
            res_text = f"❌ **SALAH HITUNG!** (Pilihanmu: Rp {view.chosen:,} | Tepat: Rp 20.000). Kasir rugi dipotong ganti rugi! (Rp 0)"
            color = discord.Color.red()

        if base_reward > 0:
            reward, market_note = await self.calculate_dynamic_salary("Kasir Minimarket", base_reward)
            await database.add_balance(user.id, reward)
            res_text += f"\n\n💰 **Gaji Diterima:** `Rp {reward:,}` {market_note}"

        result_view = discord.ui.View(timeout=120)
        result_view.add_item(BackToMenuButton(self, user))
        res_embed = discord.Embed(title="💵 KASIR: Hasil Transaksi", description=res_text, color=color)
        await panel_msg.edit(embed=res_embed, view=result_view)

    # --- 5. PUZZLE BARISTA ---
    async def start_barista_puzzle(self, interaction: discord.Interaction, user: discord.User):
        panel_msg = interaction.message
        view = BaristaLayerPuzzleView(user)

        embed = discord.Embed(
            title="☕ BARISTA PUZZLE: Riddle Kopi 3 Layer",
            description=(
                "🗣️ **Pelanggan:** *\"Mbak, aku mau kopi yang manis manis Gula Aren di LAPISAN BAWAH (LAYER 1), Susu Fresh Milk di LAPISAN TENGAH (LAYER 2), dan Topping Es Batu Kopyor di LAPISAN ATAS (LAYER 3)!\"*\n\n"
                "👉 **Langkah 1:** Pilih bahan untuk **LAPISAN BAWAH (LAYER 1)**!"
            ),
            color=discord.Color.gold()
        )
        await panel_msg.edit(embed=embed, view=view)
        await view.wait()

        await database.log_activity(user.id, "job_exec", "Barista Kopi")

        base_reward = 0
        if view.layer1 == "Gula Aren" and view.layer2 == "Susu Fresh Milk" and view.layer3 == "Es Batu Kopyor":
            base_reward = 60000
            res_text = f"🎉 **RACIKAN PERFECT!** Kopi 3 Layer terpasang persis sesuai teka-teki!"
            color = discord.Color.green()
        else:
            res_text = f"🤮 **SALAH RACIK!** (Racikanmu: {view.layer1} -> {view.layer2} -> {view.layer3}). Rasanya aneh & pelanggan komplain! (Rp 0)"
            color = discord.Color.red()

        if base_reward > 0:
            reward, market_note = await self.calculate_dynamic_salary("Barista Kopi", base_reward)
            await database.add_balance(user.id, reward)
            res_text += f"\n\n💰 **Gaji Diterima:** `Rp {reward:,}` {market_note}"

        result_view = discord.ui.View(timeout=120)
        result_view.add_item(BackToMenuButton(self, user))
        res_embed = discord.Embed(title="☕ BARISTA: Hasil Racikan", description=res_text, color=color)
        await panel_msg.edit(embed=res_embed, view=result_view)


async def setup(bot):
    await bot.add_cog(JobCog(bot))