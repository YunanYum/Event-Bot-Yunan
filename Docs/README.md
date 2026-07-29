# 🤖 Event Bot Yunan - MAHA5 Helper Bot

Bot Discord multifungsi dan interaktif yang dirancang khusus untuk mengelola event komunitas, gacha slot panggung, panggung live (Sajam), karaoke santai mandiri, bursa kerja puzzle realtime, simulasi ekonomi makro realistis, sistem KTP Digital MAHA5, serta sistem Misi & Title interaktif.

============================================================================

### 📌 Fitur Utama

| Fitur | Deskripsi |
| :--- | :--- |
| **🧩 Bursa Kerja Puzzle Realtime** | 5 Mini-game puzzle pekerjaan khas Indonesia (`!!job`) dengan panel interaktif tunggal, energi harian, dan hukum gaji *Demand & Supply*. |
| **📊 Ekonomi Makro Realistis** | Indeks inflasi dinamis (`!!ekonomi`), penyesuaian harga toko otomatis, pajak Sultan progresif, dan gaji pasif Voice Channel senyap (VC Mining). |
| **🎤 Karaoke Santai Mandiri** | Antrean karaoke harian multi-room (`!!q`), vote skip dinamis (¼ warga VC), dan proteksi minimal 1 menit untuk pencatatan statistik KTP. |
| **🪪 KTP Digital & Kartu Panggung** | Identitas warga MAHA5 2 halaman interaktif (NIM Berurutan `M5-0000-0001`, Username, Nama, Gender, Status, Fans, dan Riwayat Event) dengan tombol `◀️`, `▶️`, dan `⚙️`. |
| **🔍 Pencarian KTP via NIM** | KTP member dapat dicari langsung menggunakan NIM Unik tanpa perlu mentag orangnya (`!!ktp M5-0000-0001`). |
| **👴 Layanan Pak Lurah Interaktif** | Pendaftaran/revisi KTP via Modal Popup dengan saringan nama senonoh otomatis dan omelan khas Pak Lurah. |
| **💖 Sistem Fans & Simp** | Member dapat memberikan apresiasi (`!!simp @member`) untuk menambah jumlah Fans target di Kartu Tanda Panggung. |
| **📜 Misi & Unlock Title** | Title KTP dibuka (*unlocked*) otomatis dari Misi keaktifan event. Tampilan `!!misi` dilengkapi navigasi halaman `◀️` `▶️`. |
| **🏪 Toko Kelurahan MAHA5** | Toko kosmetik Title berjenjang (4 Tier) & item konsumsi **☕ Kopi Suplemen Energi** (+5 Shift Kerja) dengan harga dinamis berbasis inflasi. |
| **🖥️ Monitoring Sistem & Hosting** | Perintah `!!bot` khusus staf/dev untuk memantau performa CPU, RAM, Disk, Latency Ping, dan kesehatan database SQLite. |
| **📖 Role-Based Help System** | Perintah `!!help` secara otomatis menyembunyikan bab-bab khusus Moderator (Filter & Database Admin) dari member biasa. |
| **💾 SQLite WAL Persistence** | Mode *Write-Ahead Logging* (WAL) untuk performa cepat tanpa *database locking*, serta daya tahan data panggung & giveaway saat restart. |

============================================================================

## 🚀 Panduan Instalasi & Persiapan

### A. Prasyarat
- Python 3.11 atau versi lebih baru.
- Discord Bot Token dari [Discord Developer Portal](https://discord.com/developers/applications).

============================================================================

### B. Install Dependency
Buka terminal/command prompt di folder proyek, lalu ketik:

pip install -r requirements.txt

============================================================================

### C. Konfigurasi Environment Variables (.env)

Salin file .env.example menjadi .env, lalu isi variabel sesuai ID server Discord
kamu:

DISCORD_TOKEN=token_bot_kamu_di_sini
DISCORD_PREFIX=!!

ERROR_CHANNEL_ID=1234567890123456789
LOG_CHANNEL_ID=1234567890123456789
ALLOWED_CHANNELS=1234567890123456789
EXCLUDED_ROLE_ID=1234567890123456789

============================================================================

### D. Jalankan Bot

python main.py

📖 Panduan Perintah Bot

⚠️ Catatan Penting: Semua perintah pendapatan (!!harian, !!job, !!pay, VC
Mining) membutuhkan KTP resmi. Member wajib mendaftar KTP via !!lurah terlebih
dahulu!

📖 1. Bantuan & Monitoring

  - !!help ➔ Membuka Buku Saku Warga interaktif ber-dropdown. Menampilkan bab
    yang disesuaikan dengan hak akses (Mod/Member).
  - !!bot (Atau !!botstatus, !!stats - Khusus Mod/Dev) ➔ Menampilkan status
    lengkap performa bot (Ping, Uptime, CPU, RAM, Disk, DB Size).

🪪 2. KTP Digital, Pak Lurah & Sistem Fans

  - !!lurah ➔ Mendatangi Pak Lurah untuk mendaftar/ merevisi KTP (Nama, Gender,
    Status) via formulir Popup Modal.
  - !!ktp (Atau !!ktp @member / !!ktp M5-0000-0001) ➔ Menampilkan KTP Digital 2
    Halaman milik sendiri, member lain, atau via NIM Unik.
      - ▶️ ➔ Pindah ke Kartu Tanda Panggung.
      - ⚙️ (Halaman 2) ➔ Memasang Title & Oshi VTuber MAHA5 secara realtime.
  - !!simp @member (Atau !!fans @member) ➔ Berikan apresiasi +1 Fans kepada
    member favoritmu.

🧩 3. Bursa Kerja Puzzle Realtime

  - !!job (Atau !!pekerjaan, !!kerja) ➔ Membuka Pusat Kerja Puzzle Interaktif
    dalam 1 Panel Pesan.
      - Energi Kerja: 5 Shift / 24 Jam (Dapat diisi ulang menggunakan Kopi
        Suplemen Energi).
      - Pilihan Game: 🛵 Driver Ojol, 🍳 Koki Warteg, 🅿️ Tukang Parkir, 💵 Kasir
        Merch, ☕ Barista Kopi.
      - Gaji Dinamis: Pekerjaan yang sering di-spam gajinya turun (-20%),
        pekerjaan langka dapat bonus (+30%)!

📊 4. Ekonomi Makro, Bank & Toko Kelurahan

  - !!ekonomi (Atau !!bank, !!inflasi) ➔ Menampilkan Dashboard Kesehatan Ekonomi
    (Status Inflasi/Resesi, Indeks Harga Toko, Total Uang Beredar).
  - !!harian (Atau !!daily, !!gaji) ➔ Mengklaim bantuan gaji harian (Rp 30k
    - 75k). Dikenakan Pajak Sultan Progresif 10% jika saldo > Rp 10 Juta.
  - !!saldo (Atau !!dompet, !!bal) ➔ Cek total saldo Rupiah milik sendiri atau
    member lain.
  - !!pay @member [jumlah] (Atau !!tip, !!tf) ➔ Mentransfer / memberi uang tip
    Rupiah ke warga lain.
  - !!toko (Atau !!shop, !!beli) ➔ Membuka Toko Kelurahan (Title Kosmetik MAHA5
    & ☕ Kopi Suplemen Energi) dengan harga terpengaruh inflasi pasar.

🎤 5. Panggung Karaoke Santai & Sajam

  - !!q (Atau !!queue, !!karaoke) ➔ Menampilkan/memanggil ulang panel antrean
    karaoke santai 2 box terpisah di posisi terbawah chat.
  - !!qj / !!ql / !!qd ➔ Pintasan cepat Join, Leave, dan Selesai Tampil.
  - !!qskip (Atau !!qn) ➔ Vote skip untuk menurunkan penyanyi AFK (butuh ¼ vote
    warga VC).
  - !!sajam start / !!sajam end (Khusus Mod/Host) ➔ Memulai dan mengakhiri sesi
    panggung Sajam Resmi di Voice Channel.

📜 6. Misi & Title Pencapaian

  - !!misi (Atau !!title) ➔ Melihat daftar semua Misi pencapaian Title
    berhalaman (◀️ ▶️) lengkap dengan status ✅ TERBUKA atau 🔒 TERKUNCI.

🎲 7. Event Gacha PPKM & Giveaway (Khusus Mod/Admin)

  - !!ppkm [jumlah_slot] [durasi] [channel_target] ➔ Memulai gacha slot PPKM
    dengan tombol pendaftaran interaktif.
  - !!reroll [@Member] ➔ Mengundi ulang seluruh atau pemenang gacha tertentu.
  - !!ppkmconfig ➔ Panel interaktif kelola Whitelist / Blacklist Role & User.
  - !!giveaway ➔ Membuka form Popup Modal pembuat event Giveaway.

💾 8. Manajemen Backup Database (Khusus Mod/Admin)

  - !!db backup ➔ Membuat salinan cadangan instan file database SQLite di folder
    data/backups/.
  - !!db list ➔ Menampilkan daftar 10 file backup database terbaru lengkap
    beserta tanggal dan ukurannya.
  - !!db restore [nama_file_backup.db] ➔ Memulihkan database utama menggunakan
    file cadangan pilihan.

============================================================================

❓ FAQ (Frequently Asked Questions)

1.  Kenapa saya tidak bisa bekerja (!!job) atau klaim gaji (!!harian)?

      - Belum Punya KTP: Seluruh fitur pendapatan mewajibkan warga terdaftar di
        kelurahan. Ketik !!lurah untuk membuat KTP terlebih dahulu!

2.  Bagaimana cara membeli Kopi Suplemen Energi?

      - Ketik !!toko, pilih item ☕ Kopi Suplemen Energi (Rp 150.000) di
        dropdown. Energi kerja kamu akan langsung pulih menjadi 5/5 Shift.

3.  Kenapa harga di toko bisa naik/turun?

      - Toko menggunakan Indeks Inflasi Dinamis. Jika total uang beredar di
        server terlalu banyak, harga toko akan naik. Jika terjadi resesi, toko
        akan memberikan diskon! Ketik !!ekonomi untuk cek kondisi pasar.

4.  Apakah antrean Karaoke atau Giveaway hilang jika bot restart?

      - TIDAK! Sistem dilengkapi SQLite Persistence. Antrean Karaoke, penyanyi
        aktif, dan timer Giveaway akan otomatis dipulihkan persis seperti posisi
        terakhir.

5.  Bagaimana cara sistem mencegah spam Karaoke untuk statistik KTP?

      - Penyanyi wajib berada di atas panggung minimal 60 detik (1 menit) agar
        penampilannya terhitung ke statistik KTP. Tampil di bawah 1 menit tidak
        akan menambah angka KTP.

============================================================================

🏗️ Arsitektur Pembatas Channel (cog_check)

Bot dilengkapi pembatas channel bawaan yang memastikan perintah hanya bisa
dijalankan di channel terdaftar atau di dalam Text Chat Voice Channel:

```bash
async def cog_check(self, ctx):
    """Memastikan perintah dapat dijalankan di channel terdaftar atau Voice Channel."""
    if isinstance(ctx.channel, (discord.VoiceChannel, discord.StageChannel)):
        return True
        
    import os
    allowed_env = os.getenv("ALLOWED_CHANNELS", "")
    if not allowed_env:
        return True

    ALLOWED_CHANNEL_IDS = {int(cid.strip()) for cid in allowed_env.split(",") if cid.strip().isdigit()}
    
    if ctx.channel.id not in ALLOWED_CHANNEL_IDS:
        allowed_mentions = " atau ".join([f"<#{cid}>" for cid in ALLOWED_CHANNEL_IDS])
        await ctx.send(
            f"⚠️ Maaf {ctx.author.mention}, perintah bot ini hanya dapat digunakan di {allowed_mentions}.", 
            delete_after=5
        )
        return False
    return True
```
============================================================================