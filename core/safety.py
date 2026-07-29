import os
import json
import shutil
import sys
import traceback
import re
import sqlite3
import discord
from datetime import datetime

ERROR_CHANNEL_ID = int(os.getenv("ERROR_CHANNEL_ID", "0"))

# Daftar kata kasar/senonoh yang dilarang digunakan pada nama KTP
PROFANITY_LIST = {
    "anjing", "babi", "kunyuk", "bajingan", "kontol", "memek", "pantek",
    "pepek", "peler", "itil", "jembut", "fuck", "shit", "asshole",
    "bitch", "cunt", "dick", "pussy", "bastard", "titit", "lonte", "bencong",
    "kimak", "pukimak", "tetek", "toket", "bokep", "sange", "ngentot", "colok"
}

# Kamus Leetspeak untuk mencegah bypass simbol & angka
LEET_MAP = {
    '@': 'a', '4': 'a', '0': 'o', '1': 'i', '!': 'i',
    '3': 'e', '5': 's', '$': 's', '7': 't'
}

async def send_error_to_channel(bot, error, ctx=None, event_name=None):
    """Mengirimkan laporan rincian error ke channel Discord khusus."""
    if not ERROR_CHANNEL_ID:
        return

    try:
        channel = bot.get_channel(ERROR_CHANNEL_ID)
        if not channel:
            try:
                channel = await bot.fetch_channel(ERROR_CHANNEL_ID)
            except Exception:
                channel = None

        if not channel:
            return

        # Ambil exception asli jika dibungkus CommandInvokeError
        if hasattr(error, 'original'):
            error = error.original

        tb_lines = traceback.format_exception(type(error), error, error.__traceback__)
        tb_text = "".join(tb_lines)

        if len(tb_text) > 1800:
            tb_text = tb_text[-1800:]

        embed = discord.Embed(
            title="🚨 LAPORAN ERROR SISTEM BOT 🚨",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )

        if ctx:
            embed.add_field(name="📌 Perintah", value=f"`{ctx.command}`", inline=True)
            embed.add_field(name="👤 Pengguna", value=f"{ctx.author.mention} (`{ctx.author.id}`)", inline=True)
            embed.add_field(name="📍 Channel", value=f"{ctx.channel.mention if hasattr(ctx.channel, 'mention') else ctx.channel.id}", inline=True)
        elif event_name:
            embed.add_field(name="⚡ Event/Task", value=f"`{event_name}`", inline=False)

        embed.description = f"```py\n{tb_text}\n```"
        embed.set_footer(text="Sistem Pengawas Error • Event Bot Yunan")

        await channel.send(embed=embed)
    except Exception as e:
        print(f"[ERROR LOGGER FAILED] Gagal mengirim error ke channel: {e}")


def backup_sqlite_database(db_filepath: str, max_backups: int = 5):
    """Membuat salinan cadangan (.db) dari database SQLite secara aman."""
    if not os.path.exists(db_filepath):
        return
        
    dir_name = os.path.dirname(db_filepath) or "."
    backup_dir = os.path.join(dir_name, "backups")
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        backup_filename = f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_filepath = os.path.join(backup_dir, backup_filename)
        
        with sqlite3.connect(db_filepath) as src:
            with sqlite3.connect(backup_filepath) as bck:
                src.backup(bck)
        
        all_backups = sorted(
            [f for f in os.listdir(backup_dir) if f.startswith("db_backup_") and f.endswith(".db")],
            key=lambda x: os.path.getmtime(os.path.join(backup_dir, x))
        )
        while len(all_backups) > max_backups:
            oldest_file = all_backups.pop(0)
            try:
                os.remove(os.path.join(backup_dir, oldest_file))
            except Exception:
                pass
    except Exception:
        pass


def safe_write_json(filepath: str, data: dict):
    """Menulis JSON secara aman (Atomic Write)."""
    dir_name = os.path.dirname(filepath) or "."
    temp_filepath = os.path.join(dir_name, f"{os.path.basename(filepath)}.tmp")
    
    try:
        with open(temp_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        backup_dir = os.path.join(dir_name, "backups")
        os.makedirs(backup_dir, exist_ok=True)
            
        if os.path.exists(filepath):
            backup_filename = f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(filepath, os.path.join(backup_dir, backup_filename))
            
            all_backups = sorted(
                [f for f in os.listdir(backup_dir) if f.startswith("db_backup_") and f.endswith(".json")],
                key=lambda x: os.path.getmtime(os.path.join(backup_dir, x))
            )
            while len(all_backups) > 5:
                oldest_file = all_backups.pop(0)
                try:
                    os.remove(os.path.join(backup_dir, oldest_file))
                except Exception:
                    pass
        
        os.replace(temp_filepath, filepath)
        
    except Exception as e:
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except Exception:
                pass
        raise e


def setup_error_logging():
    """Mengarahkan semua error tidak terduga agar dicatat di file logs/error.log."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
        
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        log_filepath = os.path.join(log_dir, "error.log")
        with open(log_filepath, "a", encoding="utf-8") as f:
            f.write(f"\n=========================================\n")
            f.write(f"CRITICAL ERROR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"=========================================\n")
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
        
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception


def is_inappropriate_name(name: str) -> bool:
    """Memeriksa apakah nama mengandung kata senonoh/kasar (termasuk deteksi leetspeak & simbol)."""
    clean = name.lower()
    
    for char, sub in LEET_MAP.items():
        clean = clean.replace(char, sub)
        
    clean_text = re.sub(r'[^a-z\s]', '', clean)
    words = clean_text.split()
    
    for word in words:
        if word in PROFANITY_LIST:
            return True
            
    no_space_text = re.sub(r'\s+', '', clean_text)
    for bad_word in PROFANITY_LIST:
        if bad_word in no_space_text:
            return True
            
    return False