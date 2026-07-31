import discord
from discord.ext import commands
import json
import os
import math

SCRIPTS_FILE = "data/scripts.json"


def is_mod_or_admin(ctx_or_interaction):
    """Mengecek apakah pengguna memiliki izin Kelola Server."""
    if isinstance(ctx_or_interaction, discord.Interaction):
        return ctx_or_interaction.user.guild_permissions.manage_guild
    elif hasattr(ctx_or_interaction, 'author'):
        return ctx_or_interaction.author.guild_permissions.manage_guild
    return False


def load_scripts_data():
    """Membaca file data JSON script (Mendukung format Array maupun Pembungkus 'scripts')."""
    if not os.path.exists(SCRIPTS_FILE):
        return []
    try:
        with open(SCRIPTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get("scripts", [])
            elif isinstance(data, list):
                return data
            return []
    except Exception as e:
        print(f"[SCRIPT LOAD ERROR] {e}")
        return []


def save_scripts_data(scripts_list):
    """Menyimpan data script baru ke JSON secara aman (Atomic Write)."""
    os.makedirs("data", exist_ok=True)
    temp_file = f"{SCRIPTS_FILE}.tmp"
    try:
        data_to_save = {"scripts": scripts_list}
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, SCRIPTS_FILE)
        return True
    except Exception as e:
        print(f"[SCRIPT SAVE ERROR] {e}")
        if os.path.exists(temp_file):
            try: os.remove(temp_file)
            except Exception: pass
        return False


def get_cast_category_info(cast_count: int) -> tuple[discord.Color, str, str, str]:
    """
    Mengembalikan (Warna Embed, Tag Category, Emoji Icon, Label Dropdown)
    berdasarkan jumlah pemain (castCount).
    """
    if cast_count == 1:
        # Monolog (1 Orang) - Tema Emas / Solo Spotlight
        color = discord.Color.from_rgb(255, 193, 7)  # Amber / Gold
        tag = "🎙️ SOLO MONOLOG"
        icon = "👤"
        drop_label = "🎙️ Solo Monolog"
    elif cast_count == 2:
        # Dialog 2 Orang - Tema Ungu / Duo Drama
        color = discord.Color.from_rgb(214, 204, 224)  # Lavender Theme
        tag = "👥 DUO DIALOG"
        icon = "👥"
        drop_label = "👥 Duo Dialog"
    else:
        # Dialog >2 Orang - Tema Cyan/Blue / Group Drama
        color = discord.Color.from_rgb(79, 195, 247)  # Cyan / Blue
        tag = "🎭 MULTI-CAST DIALOG"
        icon = "🎭"
        drop_label = f"🎭 Multi-Cast ({cast_count}P)"

    return color, tag, icon, drop_label


def parse_txt_script(txt_content: str) -> dict:
    """Mem-parse isi file .txt menjadi struktur dictionary script."""
    lines = txt_content.strip().split("\n")
    title = "Tanpa Judul"
    genre = "General"
    cast_count = 1
    desc = "Tidak ada deskripsi."
    dialog_start_idx = 0

    for idx, line in enumerate(lines):
        line_str = line.strip()
        if line_str.startswith("---"):
            dialog_start_idx = idx + 1
            break
        
        if ":" in line_str:
            key, val = line_str.split(":", 1)
            key = key.strip().lower()
            val = val.strip()
            if key in ["judul", "title"]: title = val
            elif key in ["genre"]: genre = val
            elif key in ["pemain", "cast", "castcount"]: cast_count = int(val) if val.isdigit() else 1
            elif key in ["deskripsi", "desc", "description"]: desc = val

    dialog_lines = []
    for line in lines[dialog_start_idx:]:
        line_str = line.strip()
        if not line_str: continue

        parts = [p.strip() for p in line_str.split("|")]
        if len(parts) >= 4:
            dialog_lines.append({"speaker": parts[0], "jp": parts[1], "romaji": parts[2], "indo": parts[3]})
        elif len(parts) == 3:
            dialog_lines.append({"speaker": parts[0], "jp": parts[1], "romaji": "", "indo": parts[2]})
        elif len(parts) == 2:
            dialog_lines.append({"speaker": parts[0], "jp": parts[1], "romaji": "", "indo": parts[1]})
        else:
            dialog_lines.append({"speaker": "Action", "jp": "", "romaji": "", "indo": parts[0]})

    return {
        "title": title,
        "genre": genre,
        "castCount": cast_count,
        "description": desc,
        "lines": dialog_lines
    }


def build_script_embed(script_data: dict, current_index: int, total_count: int) -> discord.Embed:
    """Membuat tampilan Embed 1 Script Lengkap dengan pembeda Warna & Tag Pemain."""
    title = script_data.get("title", "Tanpa Judul")
    desc = script_data.get("description", "Tidak ada deskripsi.")
    genre = script_data.get("genre", "General")
    cast_count = script_data.get("castCount", 1)
    lines = script_data.get("lines", [])

    # Ambil Warna, Tag, dan Icon berdasarkan Jumlah Pemain
    embed_color, cast_tag, cast_icon, _ = get_cast_category_info(cast_count)

    formatted_lines = []
    for line in lines:
        speaker = line.get("speaker", "Unknown")
        jp = line.get("jp", "").strip()
        romaji = line.get("romaji", "").strip()
        indo = line.get("indo", "").strip()

        if speaker.lower() == "action":
            formatted_lines.append(f"🎬 *{indo}*\n> 🇯🇵 *{jp}*")
        else:
            turn_text = f"🗣️ **{speaker}**\n"
            if jp: turn_text += f"> 🇯🇵 {jp}\n"
            if romaji: turn_text += f"> 🔤 *{romaji}*\n"
            if indo: turn_text += f"> 🇮🇩 {indo}"
            
            formatted_lines.append(turn_text)

    full_script_text = "\n\n".join(formatted_lines)
    header_text = (
        f"📝 *{desc}*\n\n"
        f"🏷️ **Kategori:** `{cast_tag}` | 📌 **Genre:** `{genre}` | {cast_icon} **Pemain:** `{cast_count} Orang`\n"
        f"───────────────────────────────\n\n"
    )

    full_content = header_text + full_script_text

    if len(full_content) > 3900:
        full_content = full_content[:3900] + "\n\n*(...Naskah dipotong karena batas karakter Discord)*"

    embed = discord.Embed(
        title=f"🎭 #{current_index + 1}. {title}",
        description=full_content,
        color=embed_color
    )

    embed.set_footer(text=f"Halaman Script {current_index + 1} dari {total_count} • MAHA5 Voice Acting Studio")
    return embed


# ==========================================
# 📖 NAVIGASI SCRIPT (DUAL DROPDOWN SYSTEM)
# ==========================================

class BatchSelect(discord.ui.Select):
    def __init__(self, total_count: int, current_batch: int):
        options = []
        total_batches = math.ceil(total_count / 25)

        for b_idx in range(total_batches):
            start = b_idx * 25 + 1
            end = min(total_count, (b_idx + 1) * 25)
            options.append(
                discord.SelectOption(
                    label=f"📑 Rentang Script #{start} - #{end}",
                    value=str(b_idx),
                    description=f"Menampilkan script nomor {start} sampai {end}",
                    default=(b_idx == current_batch)
                )
            )

        super().__init__(
            placeholder="📑 Pilih Rentang Nomor Script...", 
            min_values=1, 
            max_values=1, 
            options=options, 
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        chosen_batch = int(self.values[0])
        self.view.current_batch = chosen_batch
        self.view.current_index = chosen_batch * 25
        self.view.update_components()
        
        embed = build_script_embed(self.view.scripts[self.view.current_index], self.view.current_index, len(self.view.scripts))
        await interaction.response.edit_message(embed=embed, view=self.view)


class ScriptSelect(discord.ui.Select):
    def __init__(self, scripts: list, current_index: int, current_batch: int):
        options = []
        start_idx = current_batch * 25
        end_idx = min(len(scripts), start_idx + 25)

        for idx in range(start_idx, end_idx):
            script = scripts[idx]
            title = script.get("title", f"Script #{idx+1}")
            genre = script.get("genre", "General")
            cast_count = script.get("castCount", 1)
            
            _, _, _, drop_label = get_cast_category_info(cast_count)

            options.append(
                discord.SelectOption(
                    label=f"#{idx+1}. {title}"[:100],
                    value=str(idx),
                    description=f"{drop_label} • {genre}"[:100],
                    default=(idx == current_index)
                )
            )

        row_num = 1 if len(scripts) > 25 else 0
        super().__init__(
            placeholder="📖 Pilih Judul Script...", 
            min_values=1, 
            max_values=1, 
            options=options, 
            row=row_num
        )

    async def callback(self, interaction: discord.Interaction):
        chosen_idx = int(self.values[0])
        self.view.current_index = chosen_idx
        self.view.current_batch = chosen_idx // 25
        self.view.update_components()
        
        embed = build_script_embed(self.view.scripts[chosen_idx], chosen_idx, len(self.view.scripts))
        await interaction.response.edit_message(embed=embed, view=self.view)


class JumpScriptModal(discord.ui.Modal, title="Lompat ke Nomor Script"):
    page_input = discord.ui.TextInput(
        label="Nomor Script",
        placeholder="Masukkan angka (Contoh: 1, 15, 60)",
        min_length=1,
        max_length=4,
        required=True
    )

    def __init__(self, view):
        super().__init__()
        self.script_view = view

    async def on_submit(self, interaction: discord.Interaction):
        val = self.page_input.value.strip()
        if not val.isdigit():
            await interaction.response.send_message("❌ Harap masukkan angka yang valid!", ephemeral=True)
            return

        target_page = int(val) - 1
        if 0 <= target_page < len(self.script_view.scripts):
            self.script_view.current_index = target_page
            self.script_view.current_batch = target_page // 25
            self.script_view.update_components()
            embed = build_script_embed(self.script_view.scripts[target_page], target_page, len(self.script_view.scripts))
            await interaction.response.edit_message(embed=embed, view=self.script_view)
        else:
            await interaction.response.send_message(f"❌ Nomor script harus antara **1** sampai **{len(self.script_view.scripts)}**!", ephemeral=True)


class SearchScriptModal(discord.ui.Modal, title="Cari Script Voice Acting"):
    query_input = discord.ui.TextInput(
        label="Kata Kunci / Judul / Genre",
        placeholder="Contoh: 夕暮れ, Romance, Drama, Kakek",
        min_length=2,
        max_length=50,
        required=True
    )

    def __init__(self, view):
        super().__init__()
        self.script_view = view

    async def on_submit(self, interaction: discord.Interaction):
        query = self.query_input.value.strip().lower()
        matched_index = -1

        for idx, script in enumerate(self.script_view.scripts):
            title = script.get("title", "").lower()
            genre = script.get("genre", "").lower()
            desc = script.get("description", "").lower()

            if query in title or query in genre or query in desc:
                matched_index = idx
                break

        if matched_index != -1:
            self.script_view.current_index = matched_index
            self.script_view.current_batch = matched_index // 25
            self.script_view.update_components()
            embed = build_script_embed(self.script_view.scripts[matched_index], matched_index, len(self.script_view.scripts))
            await interaction.response.send_message(f"🔍 Ditemukan script yang cocok! (Halaman #{matched_index + 1})", ephemeral=True)
            try:
                await interaction.message.edit(embed=embed, view=self.script_view)
            except Exception:
                pass
        else:
            await interaction.response.send_message(f"❌ Tidak ditemukan script dengan kata kunci: **{query}**", ephemeral=True)


class ScriptReaderView(discord.ui.View):
    def __init__(self, scripts: list, current_index: int = 0, author: discord.User = None):
        super().__init__(timeout=300.0)
        self.scripts = scripts
        self.current_index = current_index
        self.current_batch = current_index // 25
        self.author = author
        self.update_components()

    def update_components(self):
        self.clear_items()
        self.current_batch = self.current_index // 25

        if len(self.scripts) > 25:
            self.add_item(BatchSelect(len(self.scripts), self.current_batch))

        self.add_item(ScriptSelect(self.scripts, self.current_index, self.current_batch))

        btn_row = 2 if len(self.scripts) > 25 else 1

        prev_btn = discord.ui.Button(emoji="◀️", style=discord.ButtonStyle.secondary, disabled=(self.current_index == 0), row=btn_row)
        prev_btn.callback = self.prev_page
        self.add_item(prev_btn)

        jump_btn = discord.ui.Button(label="Lompat", emoji="🔢", style=discord.ButtonStyle.primary, row=btn_row)
        jump_btn.callback = self.open_jump_modal
        self.add_item(jump_btn)

        search_btn = discord.ui.Button(label="Cari", emoji="🔍", style=discord.ButtonStyle.success, row=btn_row)
        search_btn.callback = self.open_search_modal
        self.add_item(search_btn)

        next_btn = discord.ui.Button(emoji="▶️", style=discord.ButtonStyle.secondary, disabled=(self.current_index == len(self.scripts) - 1), row=btn_row)
        next_btn.callback = self.next_page
        self.add_item(next_btn)

    async def prev_page(self, interaction: discord.Interaction):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_components()
            embed = build_script_embed(self.scripts[self.current_index], self.current_index, len(self.scripts))
            await interaction.response.edit_message(embed=embed, view=self)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_index < len(self.scripts) - 1:
            self.current_index += 1
            self.update_components()
            embed = build_script_embed(self.scripts[self.current_index], self.current_index, len(self.scripts))
            await interaction.response.edit_message(embed=embed, view=self)

    async def open_jump_modal(self, interaction: discord.Interaction):
        await interaction.response.send_modal(JumpScriptModal(self))

    async def open_search_modal(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SearchScriptModal(self))


# --- COG MAIN CLASS ---
class ScriptCog(commands.Cog, name="Voice Acting Scripts"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="script", aliases=["naskah", "dubbing", "scripts"])
    async def script_command(self, ctx, page: int = None):
        """Membuka Katalog Script Voice Acting Interaktif Berhalaman."""
        scripts = load_scripts_data()

        if not scripts:
            return await ctx.send("❌ Belum ada data script di file `data/scripts.json`!")

        current_idx = 0
        if page and 1 <= page <= len(scripts):
            current_idx = page - 1

        view = ScriptReaderView(scripts, current_idx, ctx.author)
        embed = build_script_embed(scripts[current_idx], current_idx, len(scripts))
        await ctx.send(embed=embed, view=view)

    @commands.command(name="uploadscript", aliases=["importscript", "uploadnaskah", "addscript"])
    @commands.check(is_mod_or_admin)
    async def upload_script_command(self, ctx):
        """Mengimpor script baru dari lampiran file .txt atau .json."""
        if not ctx.message.attachments:
            return await ctx.send(
                "❌ **Harap lampirkan file `.txt` atau `.json` saat mengetik perintah ini!**\n\n"
                "**Cara Penggunaan:**\n"
                "1. Unggah/drag file `.txt` atau `.json` ke chat Discord.\n"
                "2. Pada kolom komentar lampiran, ketik `!!uploadscript` lalu kirim!"
            )

        attachment = ctx.message.attachments[0]
        filename = attachment.filename.lower()

        if not (filename.endswith(".json") or filename.endswith(".txt")):
            return await ctx.send("❌ File harus berekstensi **`.json`** atau **`.txt`**!")

        try:
            file_bytes = await attachment.read()
            content_str = file_bytes.decode("utf-8")
            scripts = load_scripts_data()
            added_count = 0

            if filename.endswith(".json"):
                data = json.loads(content_str)
                if isinstance(data, dict) and "scripts" in data:
                    data = data["scripts"]

                if isinstance(data, list):
                    for item in data:
                        item["id"] = len(scripts) + 1
                        scripts.append(item)
                        added_count += 1
                elif isinstance(data, dict):
                    data["id"] = len(scripts) + 1
                    scripts.append(data)
                    added_count += 1
            else:
                parsed = parse_txt_script(content_str)
                parsed["id"] = len(scripts) + 1
                scripts.append(parsed)
                added_count = 1

            success = save_scripts_data(scripts)
            if success:
                await ctx.send(
                    f"🎉 **BERHASIL MENGIMPOR {added_count} SCRIPT BARU!**\n"
                    f"📊 Total Script saat ini: **{len(scripts)}** halaman.\n"
                    f"Ketik `!!script {len(scripts)}` untuk melihat script terbaru!"
                )
            else:
                await ctx.send("❌ Gagal menyimpan data ke file `data/scripts.json`!")

        except Exception as e:
            await ctx.send(f"❌ **Gagal memproses file:** `{e}`")


async def setup(bot):
    await bot.add_cog(ScriptCog(bot))