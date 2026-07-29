# 🤖 Event Bot Yunan - MAHA5 Helper Bot

Bot Discord multifungsi dan interaktif yang dirancang khusus untuk mengelola event komunitas, gacha slot panggung event, panggung live (Sajam), antrean karaoke santai multi-room, event giveaway, monitoring hosting, serta logging realtime.

============================================================================

### 📌 Fitur Utama

| Fitur | Deskripsi |
| :--- | :--- |
| **🎲 Gacha Interaktif PPKM** | Pendaftaran gacha slot panggung menggunakan Tombol (Buttons) dengan *live-counter* peserta real-time, penyaringan Voice Channel, serta fitur Reroll. |
| **🎙️ Panggung Live Sajam** | Sistem panggung jamming/nyanyi resmi terintegrasi dengan pemantauan pengunjung VC dan rekapitulasi statistik lengkap saat sesi diakhiri. |
| **🎤 Karaoke Santai Multi-Room** | Antrean karaoke harian mandiri tanpa butuh moderator (`!!q`). Dilengkapi panel ganda, vote skip dinamis (¼ warga VC), dan override lengser dari Mod. |
| **🎁 Event Giveaway** | Pembuat event pembagian hadiah interaktif berbasis formulir Popup Modal dengan timer otomatis dan ketahanan data (*persistence*). |
| **🖥️ Monitoring System & Hosting** | Perintah `!!bot` khusus staf/dev untuk memantau performa CPU, RAM Hosting, RAM Bot, Disk, Latency Ping, dan kesehatan SQLite. |
| **📜 Realtime Audit Logger** | Pencatatan otomatis secara realtime ke channel log (`#bot-log`) untuk 6 peristiwa penting (KTP, Sajam, PPKM, Giveaway, Backup DB). |
| **📖 Role-Based Help System** | Perintah `!!help` secara otomatis menyembunyikan bab-bab khusus Moderator (Filter & Database Admin) dari member biasa. |
| **💾 SQLite WAL & Backup System** | Mode *Write-Ahead Logging* (WAL) untuk performa cepat tanpa *database locking*, serta manajemen backup DB langsung dari chat (`!!db`). |

============================================================================

## 🚀 Panduan Instalasi & Persiapan

### A. Prasyarat
- Python 3.11 atau versi lebih baru.
- Discord Bot Token dari [Discord Developer Portal](https://discord.com/developers/applications).

### B. Install Dependency
Buka terminal di folder proyek, lalu jalankan:

pip install -r requirements.txt

### C. Konfigurasi Environment Variables (.env)

Salin file .env.example menjadi .env, lalu isi variabel sesuai ID server Discord
kamu:

DISCORD_TOKEN=token_bot_kamu_di_sini

DISCORD_PREFIX=!!

ERROR_CHANNEL_ID=1234567890123456789

LOG_CHANNEL_ID=1234567890123456789

ALLOWED_CHANNELS=1234567890123456789

EXCLUDED_ROLE_ID=1234567890123456789

### D. Jalankan Bot

python main.py

📖 Panduan Perintah Bot

📖 1. Bantuan Umum & Status Hosting

  - !!help ➔ Membuka Buku Panduan interaktif ber-dropdown. Menampilkan bab yang
    disesuaikan dengan hak akses penggunanya (Mod/Member).
  - !!bot (Atau !!botstatus, !!stats - Khusus Mod/Dev) ➔ Menampilkan status
    realtime performa bot dan sistem hosting (Ping, Uptime, CPU, RAM, Disk, DB
    Size).

🎤 2. Karaoke Santai Mandiri (Untuk Semua Member)

  - !!q (Atau !!queue, !!karaoke) ➔ Menampilkan/memanggil ulang panel antrean
    karaoke santai 2 box terpisah di posisi terbawah chat.
  - !!qj (Atau !!qjoin) ➔ Pintasan cepat bergabung ke antrean karaoke.
  - !!ql (Atau !!qleave) ➔ Pintasan cepat keluar dari antrean karaoke.
  - !!qd (Atau !!qdone) ➔ Pintasan selesai tampil (Khusus penyanyi aktif di
    panggung).
  - !!qskip (Atau !!qn) ➔ Memberikan vote skip untuk menurunkan penyanyi
    AFK/stuck. Membutuhkan vote sebanyak ¼ dari warga VC (atau langsung lengser
    jika ditekan Moderator).
  - !!qclear (Khusus Mod/Admin) ➔ Membersihkan seluruh antrean karaoke di
    channel tersebut.

🎙️ 3. Sesi Jamming / Panggung Sajam Resmi (Khusus Mod/Host)

  - !!sajam start ➔ Memulai sesi Sajam Resmi di Voice Channel tempat Anda
    bergabung saat ini.
  - !!sajam (Atau !!s) ➔ Recall / menampilkan ulang panel antrean Sajam
    terupdate.
  - !!sajam end ➔ Mengakhiri seluruh sesi Sajam dan menampilkan rekapitulasi
    statistik lengkap panggung.

🎲 4. Event Gacha PPKM & Giveaway (Khusus Mod/Admin)

  - !!ppkm [jumlah_slot] [durasi] [channel_target] ➔ Memulai gacha slot PPKM
    dengan tombol pendaftaran interaktif dan counter peserta real-time. Contoh:
    !!ppkm 3 25s #event-voice
  - !!reroll ➔ Mengundi ulang seluruh pemenang gacha terakhir.
  - !!reroll @NamaMember ➔ Mengundi ulang pemenang tertentu saja (mencoret
    pemenang lama dan mencarikan penggantinya).
  - !!ppkmconfig ➔ Membuka panel interaktif untuk mengelola role
    blacklist/whitelist & user blacklist.
  - !!giveaway ➔ Membuka panel pembuat giveaway. Klik tombol "Buat Giveaway 🎁"
    untuk mengisi formulir Modal Popup.

💾 5. Manajemen Backup Database (Khusus Mod/Admin)

  - !!db ➔ Menampilkan panduan singkat perintah database.
  - !!db backup ➔ Membuat salinan cadangan instan file database SQLite di folder
    data/backups/.
  - !!db list ➔ Menampilkan daftar 10 file backup database terbaru lengkap
    beserta tanggal dan ukurannya.
  - !!db restore [nama_file_backup.db] ➔ Memulihkan database utama menggunakan
    file cadangan pilihan (dilengkapi tombol konfirmasi keamanan).

============================================================================

❓ FAQ (Frequently Asked Questions)

1.  Kok bot-nya ga ngerespon sama sekali pas aku ketik perintah?

      - Salah Channel: Pastikan Anda mengetik perintah di salah satu channel
        yang ID-nya tercantum di .env (ALLOWED_CHANNELS) atau di dalam Text Chat
        Voice Channel.
      - Izin Kurang: Perintah admin/mod memerlukan izin sistem Discord bernama
        "Manage Server" (Kelola Server).
      - Bot Offline: Periksa terminal/CMD Anda, pastikan proses python main.py
        masih berjalan.

2.  Apakah antrean Karaoke atau Giveaway hilang jika bot dimatikan?

      - TIDAK! Sistem dilengkapi SQLite Persistence. Antrean Karaoke, penyanyi
        aktif, dan timer Giveaway akan otomatis dipulihkan persis seperti posisi
        terakhir saat bot dinyalakan kembali.

3.  Bagaimana cara kerja sistem Realtime Logging (#bot-log)?

      - Bot secara otomatis mencatat 6 peristiwa penting ke channel #bot-log:
        Pendaftaran KTP, Mulai/Selesai Sajam, Memulai PPKM, Memulai Giveaway,
        serta Backup/Restore Database.
