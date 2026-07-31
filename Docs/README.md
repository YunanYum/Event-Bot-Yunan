# 🤖 Event Bot Yunan - MAHA5 Helper Bot

Bot Discord multifungsi dan interaktif yang dirancang khusus untuk komunitas MAHA5. Dilengkapi dengan sistem KTP Digital, bursa kerja puzzle realtime, simulasi ekonomi makro realistis, studio naskah dubbing (60+ script), panggung musik live (Sajam & Karaoke), gacha slot event, event giveaway ber-filter, monitoring hosting, serta logging realtime.

============================================================================

### 📌 Fitur Utama

| Fitur | Deskripsi |
| :--- | :--- |
| **🪪 KTP Digital & Kartu Panggung** | Kartu identitas warga MAHA5 2 halaman interaktif (NIM Berurutan `M5-0000-0001`, Username, Nama, Gender, Status, Fans, dan Riwayat Event) dengan pencarian via NIM Unik (`!!ktp M5-0000-0001`) dan pendaftaran Pak Lurah (`!!lurah`). |
| **🧩 Bursa Kerja Puzzle Realtime** | 5 Mini-game puzzle pekerjaan khas Indonesia (`!!job`) dalam single-panel UI, 5 Energi/Shift harian, KTP guard, dan hukum gaji dinamis *Demand & Supply*. |
| **📊 Ekonomi Makro Realistis** | Indeks inflasi dinamis (`!!ekonomi`), penyesuaian harga toko otomatis, pajak Sultan progresif (> Rp 10 Juta), transfer saldo (`!!pay`), dan gaji pasif Voice Channel senyap (VC Mining). |
| **🏪 Toko Kelurahan MAHA5** | Toko kosmetik Title berjenjang (4 Tier) & item konsumsi **☕ Kopi Suplemen Energi** (+5 Shift Kerja) dengan harga terpengaruh inflasi pasar. |
| **📜 Misi & Unlock Title** | Title KTP dibuka (*unlocked*) otomatis dari Misi keaktifan event & Fans. Tampilan `!!misi` dilengkapi navigasi halaman `◀️` `▶️`. |
| **🎭 Studio Naskah Dubbing 60+** | Katalog 60+ naskah Voice Acting interaktif (`!!script`) dengan tampilan lirik 3 bahasa (🇯🇵 JP, 🔤 Romaji, 🇮🇩 Indo), pembeda warna kategori (Monolog 🟡, Duo 🟣, Multi-Cast 🔷), serta impor file `.txt`/`.json` (`!!uploadscript`). |
| **🎤 Karaoke Santai Multi-Room** | Antrean karaoke harian multi-room (`!!q`), vote skip dinamis (¼ warga VC), dan proteksi minimal 1 menit panggung untuk pencatatan statistik KTP. |
| **🎙️ Panggung Live Sajam** | Sistem panggung jamming/nyanyi resmi terintegrasi dengan pemantauan pengunjung VC dan rekapitulasi statistik lengkap saat sesi diakhiri. |
| **🎁 Event Giveaway Filtered** | Pembuat event pembagian hadiah via Modal Popup atau **Slash Command `/giveaway`**. Mendukung Sponsor (Opsional) & Filter Role Whitelist (`@Role`) / Blacklist (`!@Role`) temporer. |
| **🎲 Gacha Interaktif PPKM** | Pendaftaran gacha slot panggung menggunakan Tombol (Buttons) dengan *live-counter* peserta real-time, penyaringan Voice Channel, serta fitur Reroll. |
| **🖥️ Monitoring System & Hosting** | Perintah `!!bot` khusus staf/dev untuk memantau performa CPU, RAM Hosting, RAM Bot, Disk, Latency Ping, dan kesehatan SQLite. |
| **📜 Realtime Audit Logger** | Pencatatan otomatis secara realtime ke channel log (`#bot-log`) untuk 5 peristiwa penting (KTP, Sajam, PPKM, Giveaway, Backup DB). |
| **📖 Adaptive Help Book** | Buku saku warga interaktif 7 Bab (`!!help`) dengan tampilan adaptif berdasarkan hak akses (Warga vs Staf/Mod). |
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

============================================================================

📖 Panduan Perintah Bot

⚠️ Catatan Penting: Semua perintah pendapatan (!!harian, !!job, !!pay, VC
Mining) membutuhkan KTP resmi. Member wajib mendaftar KTP via !!lurah terlebih
dahulu!

📖 1. Bantuan Umum & Status Hosting

  - !!help ➔ Membuka Buku Saku Warga interaktif 7 Bab ber-dropdown.
  - !!bot (Atau !!botstatus, !!stats - Khusus Mod/Dev) ➔ Menampilkan status
    realtime performa bot dan sistem hosting (Ping, Uptime, CPU, RAM, Disk, DB
    Size).
  - !!sync (Khusus Mod/Dev) ➔ Memaksa Discord mensinkronkan Slash Commands
    (/giveaway) secara instan di server.

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
        Suplemen Energi di !!toko).
      - Pilihan Game Puzzle: 🛵 Driver Ojol, 🍳 Koki Warteg, 🅿️ Tukang Parkir, 💵
        Kasir Merch, ☕ Barista Kopi.
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

🎭 5. Studio Naskah Dubbing (Voice Acting)

  - !!script (Atau !!naskah, !!dubbing) ➔ Membuka Katalog 60+ Naskah Voice
    Acting interaktif (◀️, ▶️, 🔢 Lompat, 🔍 Cari, Dropdown Batch).
      - 🟡 Solo Monolog (1P): Warna Embed Emas.
      - 🟣 Duo Dialog (2P): Warna Embed Lavender/Ungu.
      - 🔷 Multi-Cast (3P+): Warna Embed Cyan/Biru.
  - !!uploadscript (Atau !!uploadnaskah, !!addscript - Khusus Mod) ➔
    Mengimpor/menambah naskah baru secara instan dengan melampirkan file .txt
    atau .json.

🎤 6. Panggung Karaoke Santai & Sajam

  - !!q (Atau !!queue, !!karaoke) ➔ Menampilkan/memanggil ulang panel antrean
    karaoke santai 2 box terpisah di posisi terbawah chat.
  - !!qj / !!ql / !!qd ➔ Pintasan cepat Join, Leave, dan Selesai Tampil.
  - !!qskip (Atau !!qn) ➔ Vote skip untuk menurunkan penyanyi AFK (butuh ¼ vote
    warga VC).
  - !!sajam start / !!sajam end (Khusus Mod/Host) ➔ Memulai dan mengakhiri sesi
    panggung Sajam Resmi di Voice Channel.

📜 7. Misi & Title Pencapaian

  - !!misi (Atau !!title) ➔ Melihat daftar semua Misi pencapaian Title
    berhalaman (◀️ ▶️) lengkap dengan status ✅ TERBUKA atau 🔒 TERKUNCI.

🎲 8. Event Gacha PPKM & Giveaway (Khusus Mod/Admin)

  - !!ppkm [jumlah_slot] [durasi] [channel_target] ➔ Memulai gacha slot PPKM
    dengan tombol pendaftaran interaktif.
  - !!reroll [@Member] ➔ Mengundi ulang seluruh atau pemenang gacha tertentu.
  - !!ppkmconfig ➔ Panel interaktif kelola Whitelist / Blacklist Role & User.
  - !!giveaway atau /giveaway ➔ Membuka form pembuat event Giveaway.
      - Sponsor / Dari Siapa: Opsional (Akan ditampilkan di Embed jika diisi).
      - Filter Role: Tulis @Role untuk Whitelist atau !@Role untuk Blacklist
        (Temporer per-giveaway).

💾 9. Manajemen Backup Database (Khusus Mod/Admin)

  - !!db backup ➔ Membuat salinan cadangan instan file database SQLite di folder
    data/backups/.
  - !!db list ➔ Menampilkan daftar 10 file backup database terbaru lengkap
    beserta tanggal dan ukurannya.
  - !!db restore [nama_file_backup.db] ➔ Memulihkan database utama menggunakan
    file cadangan pilihan.

============================================================================

❓ FAQ (Frequently Asked Questions)

1.  Kategori naskah apa saja yang tersedia di Studio !!script?

      - Katalog memiliki 60+ Naskah yang terbagi dalam 6 Kategori: Romance &
        Drama, Thriller & Dark Drama, Komedi Militer, Edukasi & Budaya Jepang,
        VTuber Special (Debut & Collab), serta Rekreasi Adegan Anime Populer
        (Your Name, Jujutsu Kaisen, Attack on Titan, Demon Slayer, Death Note,
        dll.).

2.  Bagaimana cara mengimpor naskah dubbing baru secara massal?

      - Cukup unggah file .json atau .txt berisi naskah kamu di Discord, lalu
        pada komentar lampiran ketik !!uploadscript. Bot akan langsung mengimpor
        semuanya dalam 1 detik!

3.  Kenapa saya tidak bisa bekerja (!!job) atau klaim gaji (!!harian)?

      - Belum Punya KTP: Seluruh fitur pendapatan mewajibkan warga terdaftar di
        kelurahan. Ketik !!lurah untuk membuat KTP terlebih dahulu!

4.  Bagaimana cara membuat Giveaway khusus Role tertentu (Whitelist/Blacklist)?

      - Jalankan !!giveaway atau Slash Command /giveaway. Pada kolom Filter
        Role, tulis @Role untuk Whitelist atau !@Role untuk Blacklist. Filter
        ini bersifat temporer per-giveaway.

5.  Apakah antrean Karaoke atau Giveaway hilang jika bot restart?

      - TIDAK! Sistem dilengkapi SQLite Persistence. Antrean Karaoke, penyanyi
        aktif, dan timer Giveaway akan otomatis dipulihkan persis seperti posisi
        terakhir.