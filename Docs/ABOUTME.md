==================================================
ABOUT ME: EVENT BOT YUNAN
==================================================

Halo semuanya! Selamat datang. Perkenalkan, saya Event Bot Yunan. Saya adalah bot Discord kustom yang dirancang khusus untuk mengelola berbagai keseruan event, identitas warga, hingga sistem ekonomi di server MAHA5.

Tugas utama saya adalah membantu para staf, moderator, dan member dalam mengatur panggung acara, gacha slot event (PPKM), antrean panggung live (Sajam), bagi-bagi hadiah (Giveaway), penerbitan KTP Digital MAHA5, hingga toko kosmetik Title interaktif agar seluruh aktivitas komunitas berjalan dengan lancar, tertib, dan menyenangkan.

--------------------------------------------------
PROFIL SINGKAT SAYA
--------------------------------------------------

- Nama Bot: Event Bot Yunan
- Tugas Utama: Mengelola Event (PPKM, Sajam, Giveaway), KTP Digital, Misi Title, & Ekonomi Rupiah
- Bahasa & Library: Python (discord.py v2.x)
- Arsitektur Code: Modular (Cogs-based System) — Sangat rapi & mudah dikembangkan
- Penyimpanan Data: SQLite Database Terpusat (`data/event_bot.db`)
- Target Hosting: Laptop/PC Lokal (Sangat ramah untuk self-host) atau VPS

--------------------------------------------------
PRINSIP KERJA SAYA (UNTUK MEMUDAHKAN ANDA)
--------------------------------------------------

Saya dirancang dengan empat prinsip utama agar komunitas dan staf merasa nyaman:

1. Anti-Spam Chat (Menggunakan Tombol, Modal Popup, & Dropdown)
Saya kurang menyukai channel chat yang dipenuhi oleh spam perintah teks. Oleh karena itu, pendaftaran gacha, giveaway, pendaftaran KTP, pembelian toko, hingga antrean panggung dialihkan menggunakan komponen interaktif (Buttons, Modals, & Select Dropdowns). Cukup klik, semua beres!

2. Aman dari Mati Lampu atau Crash (Anti Rusak Data & Persistence)
Karena sering dijalankan di PC/Laptop lokal, saya dibekali sistem pengaman data yang ketat. Jika komputer Anda tiba-tiba mati lampu atau restart saat event berlangsung, sesi panggung Sajam dan seluruh data database saya dijamin aman dan dapat dipulihkan secara otomatis saat dinyalakan kembali.

3. Penyaringan Pemenang & Nama yang Adil
- Pada event Gacha/PPKM: Saya secara otomatis memverifikasi keberadaan peserta di Voice/Stage Channel saat waktu undian habis.
- Pada pendaftaran KTP: Saya dibekali saringan kata kasar/senonoh otomatis (`safety.py`) untuk menjaga ketertiban nama warga.

4. Gamifikasi & Interaksi Komunitas
Member bisa mengumpulkan Fans (`!!simp @member`), klaim gaji harian Rupiah (`!!harian`), membuka Misi pencapaian Title, hingga memamerkan KTP Digital 2 Halaman mereka.

--------------------------------------------------
BEDAH FUNGSI SISTEM (SISTEM COGS & CORE)
--------------------------------------------------

Sistem saya terbagi menjadi modul-modul mandiri di dalam folder `cogs/` dan `core/`:

📂 1. EVENT MODULES (cogs/events/)

- cogs/events/ppkm.py (Gacha Slot Event PPKM)
  Mengundi giliran naik panggung acara PPKM dengan filter Role (Blacklist/Whitelist), User Blacklist, verifikasi keberadaan di Voice Channel, serta sistem Reroll fleksibel.

- cogs/events/sajam.py (Antrean Panggung Sajam)
  Sistem antrean panggung jamming / nyanyi otomatis. Dilengkapi tampilan panel ganda (Panggung Utama & Daftar Antrean), alur giliran otomatis, fitur recall anti-tenggelam (`!!s`), serta state persistence ke SQLite.

- cogs/events/giveaway.py (Giveaway Interaktif)
  Pembuatan giveaway berbasis formulir Modal Popup (Hadiah, Pemenang, Durasi, Channel) dengan counter jumlah peserta real-time.

📂 2. SYSTEM MODULES (cogs/system/)

- cogs/system/ktp.py (KTP Digital MAHA5 & Kartu Tanda Panggung)
  Menangani pembuatan KTP via Pak Lurah (`!!lurah`), tampilan KTP Digital 2 Halaman (`!!ktp`), apresiasi Fans (`!!simp @member`), serta update tampilan panel secara real-time saat mengganti Title/Oshi.

- cogs/system/misi.py (Sistem Misi & Title Pencapaian)
  Menangani pengecekan Misi (`!!misi` / `!!title`) untuk membuka Title KTP secara otomatis berdasarkan statistik keikutsertaan event dan akumulasi Fans.

- cogs/system/economy.py (Ekonomi Rupiah & Toko Title)
  Sistem keuangan lokal (`!!saldo`), klaim gaji harian (`!!harian`), serta Toko Kosmetik Title (`!!toko`) interaktif berbasis Dropdown untuk pembelian instan tanpa mengetik perintah.

- cogs/system/admin.py (Manajemen Database Admin)
  Pusat pengelolaan cadangan database SQLite langsung lewat chat Discord (`!!db backup`, `!!db list`, `!!db restore`).

- cogs/system/help.py (Buku Panduan Dropdown)
  Buku panduan interaktif berbentuk halaman Bab yang dapat dipilih lewat menu dropdown.

📂 3. CORE MODULES (core/)

- core/database.py: Pengelola koneksi dan query SQLite terpusat berbasis asinkron (`asyncio.to_thread`).
- core/safety.py: Sistem pencatat log error (`logs/error.log`), penulisan aman (*Atomic Write*), dan auto-backup.
- core/titles.py: Kamus terpusat daftar Misi Title dan Toko Kosmetik.

--------------------------------------------------
SISTEM KEAMANAN DATA SAYA (safety.py & database.py)
--------------------------------------------------

- Atomic Write & Safe Backup: Mengamankan file database sebelum ditimpa, dengan batasan maksimal 5 file cadangan otomatis di folder `data/backups/`.
- Dynamic Voice Channel Check: Memastikan semua perintah dapat dijalankan baik di channel teks terdaftar maupun di dalam chat room Voice Channel.
- Pencatat Log Error: Jika terjadi kendala sistem, saya akan mencatat rincian traceback di `logs/error.log` agar mudah diperiksa.

==================================================








(*iye gw tau gw pake ai buat bikin aboutme)