# 🤖 Event Bot Yunan - MAHA5 Helper Bot

Bot Discord multifungsi dan interaktif yang dirancang khusus untuk mengelola event komunitas, gacha slot panggung event, panggung live (Sajam), antrean karaoke santai multi-room, event giveaway ber-filter, monitoring hosting, serta logging realtime.

============================================================================

### 📌 Fitur Utama

| Fitur | Deskripsi |
| :--- | :--- |
| **🎲 Gacha Interaktif PPKM** | Pendaftaran gacha slot panggung menggunakan Tombol (Buttons) dengan *live-counter* peserta real-time, penyaringan Voice Channel, serta fitur Reroll. |
| **🎙️ Panggung Live Sajam** | Sistem panggung jamming/nyanyi resmi terintegrasi dengan pemantauan pengunjung VC dan rekapitulasi statistik lengkap saat sesi diakhiri. |
| **🎤 Karaoke Santai Multi-Room** | Antrean karaoke harian mandiri tanpa butuh moderator (`!!q`). Dilengkapi panel ganda, vote skip dinamis (¼ warga VC), dan override lengser dari Mod. |
| **🎁 Event Giveaway Filtered** | Pembuat event pembagian hadiah berbasis Popup Modal. Mendukung Sponsor (Opsional) & Filter Role Whitelist (`@Role`) / Blacklist (`!@Role`) temporer. |
| **🖥️ Monitoring System & Hosting** | Perintah `!!bot` khusus staf/dev untuk memantau performa CPU, RAM Hosting, RAM Bot, Disk, Latency Ping, dan kesehatan SQLite. |
| **📜 Realtime Audit Logger** | Pencatatan otomatis secara realtime ke channel log (`#bot-log`) untuk 6 peristiwa penting (Sajam, PPKM, Giveaway, Backup DB). |
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
    dengan tombol pendaftaran interaktif dan counter peserta real-time.
  - !!reroll ➔ Mengundi ulang seluruh pemenang gacha terakhir.
  - !!reroll @NamaMember ➔ Mengundi ulang pemenang tertentu saja (mencoret
    pemenang lama dan mencarikan penggantinya).
  - !!ppkmconfig ➔ Membuka panel interaktif untuk mengelola role
    blacklist/whitelist & user blacklist.
  - !!giveaway ➔ Membuka panel pembuat giveaway berbasis Modal Popup.
      - Sponsor / Dari Siapa: Opsional (Akan ditampilkan di Embed jika diisi).
      - Filter Role: Tulis @Role untuk Whitelist atau !@Role untuk Blacklist
        (Temporer per-giveaway).

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

🎙️ Panggung & Karaoke

    Apakah Karaoke Santai bisa digunakan di banyak channel sekaligus?

        BISA! Sistem Karaoke menggunakan arsitektur Multi-Room. Antrean dan penyanyi aktif di setiap channel/room terisolasi secara mandiri dan tidak akan bertabrakan.

    Gimana cara menurunkan penyanyi Karaoke yang AFK atau tidak mau turun?

        Member lain bisa menekan tombol ⏩ LENGSERKAN DIA atau mengetik !!qskip. Jika jumlah vote mencapai ¼ dari total warga di VC, penyanyi akan otomatis diturunkan.

        Moderator yang menekan tombol tersebut dapat langsung melengserkan penyanyi secara instan (override).

    Apa perbedaan antara Sesi Sajam dan Karaoke Santai?

        Karaoke Santai (!!q): Bersifat mandiri/harian tanpa perlu dijaga Host/Mod.

        Sajam Resmi (!!sajam): Sesi panggung resmi yang dipandu Host/Mod (!!sajam start), dilengkapi pemantauan pengunjung VC realtime dan laporan rekapitulasi statistik panggung lengkap saat diakhiri (!!sajam end).

🎲 Event PPKM & Giveaway

    Bagaimana cara membuat Giveaway khusus Role tertentu (Whitelist/Blacklist)?

        Jalankan !!giveaway, klik Buat Giveaway 🎁. Di kolom ke-5 (Filter Role), tulis @Role untuk Whitelist (hanya role tersebut yang bisa ikut) atau !@Role untuk Blacklist (role tersebut dilarang ikut).

        Filter ini bersifat temporer per-giveaway, sehingga pembuatan giveaway berikutnya otomatis kembali tanpa filter.

    Apa yang terjadi jika kolom Channel Target dikosongkan saat membuat Giveaway?

        Bot akan otomatis mengirimkan pesan Giveaway ke channel tempat perintah !!giveaway dipanggil.

    Bagaimana jika pemenang Gacha PPKM berhalangan hadir atau tidak ada di VC?

        Moderator dapat mengetik !!reroll untuk mengundi ulang seluruh pemenang, atau !!reroll @NamaMember untuk mengganti pemenang tertentu saja.

    Bagaimana cara membatasi siapa saja yang boleh ikut Gacha PPKM?

        Ketik !!ppkmconfig untuk membuka panel interaktif kelola Whitelist/Blacklist Role dan User.

💾 Database, Hosting & System

    Apakah antrean Karaoke atau Giveaway hilang jika bot restart?

        TIDAK! Sistem dilengkapi SQLite Persistence. Antrean Karaoke, penyanyi aktif, dan timer Giveaway akan otomatis dipulihkan persis seperti posisi terakhir saat bot dinyalakan kembali.

    Mengapa di folder data/ ada file event_bot.db-wal dan event_bot.db-shm?

        Itu adalah file bawaan dari mode SQLite WAL (Write-Ahead Logging). Mode ini aktif untuk memastikan proses read/write database berlangsung super cepat tanpa mengalami error database is locked. Ini 100% normal.

    Bagaimana cara memantau kondisi CPU, RAM, dan Hosting tempat bot berjalan?

        Moderator/Dev dapat mengetik !!bot (atau !!botstatus) untuk melihat laporan realtime penggunaan CPU, RAM, Disk, Latency Ping, dan kesehatan database.

    Bagaimana cara kerja sistem Realtime Logging (#bot-log)?

        Bot secara otomatis mencatat 5 peristiwa penting ke channel #bot-log: Mulai/Selesai Sajam, Memulai PPKM, Memulai Giveaway, serta Backup/Restore Database.

    Bagaimana cara memulihkan database jika terjadi kesalahan data?

        Moderator dapat mengetik !!db list untuk melihat daftar file cadangan, lalu jalankan !!db restore [nama_file.db]. Sistem dilengkapi tombol konfirmasi keselamatan sebelum menimpa data.

🔧 Troubleshooting

    Kok bot tidak merespon sama sekali saat diketik perintah?

        Salah Channel: Pastikan Anda mengetik perintah di channel yang ID-nya terdaftar pada .env (ALLOWED_CHANNELS) atau di dalam Text Chat Voice Channel.

        Izin Kurang: Perintah admin/mod memerlukan izin Discord bernama "Manage Server" (Kelola Server).

        Bot Offline: Periksa terminal VS Code / hosting Anda, pastikan skrip python main.py berjalan tanpa error.

    Bagaimana jika saya mengubah ID channel/role pada file .env?

        Setiap kali Anda mengubah isi file .env, Anda wajib melakukan restart bot (Ctrl + C lalu jalankan kembali python main.py) agar variabel baru terbaca oleh Python.