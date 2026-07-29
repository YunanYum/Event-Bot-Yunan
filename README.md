# 🤖 Event Bot Yunan - MAHA5 Helper Bot

Bot Discord multifungsi yang dirancang khusus untuk mengelola event komunitas, gacha slot panggung, antrean panggung live (Sajam), karaoke santai mandiri, giveaway, sistem identitas warga (KTP Digital MAHA5), ekonomi Rupiah, serta sistem Misi & Title interaktif.


### 📌 Fitur Utama

| Fitur | Deskripsi |
| :--- | :--- |
| **Gacha Interaktif PPKM** | Pendaftaran peserta gacha menggunakan Tombol (Buttons) dengan *live-counter* peserta real-time dan penyaringan Voice Channel. |
| **Panggung Live Sajam** | Sistem antrean jamming/nyanyi resmi terintegrasi dengan tombol aksi member dan kontrol moderator (Persisten SQLite). |
| **🎤 Karaoke Santai Mandiri** | Antrean karaoke harian tanpa butuh moderator (`!!q`). Dilengkapi panel ganda, vote skip dinamis (¼ warga VC), dan override lengser instan dari Mod. |
| **🪪 KTP Digital & Kartu Panggung** | Kartu identitas warga MAHA5 2 halaman interaktif (NIM Berurutan `M5-0000-0001`, Username, Nama, Gender, Status, Fans, dan Riwayat Event) dengan tombol `◀️`, `▶️`, dan `⚙️`. |
| **🔍 Pencarian KTP via NIM** | KTP member dapat dicari langsung menggunakan NIM Unik tanpa perlu mencari/mentag orangnya (`!!ktp M5-0000-0001`). |
| **👴 Layanan Pak Lurah Interaktif** | Pendaftaran/revisi KTP via formulir Modal Popup yang dilengkapi saringan nama senonoh otomatis dan omelan khas Pak Lurah. |
| **💖 Sistem Fans & Simp** | Member dapat memberikan apresiasi (`!!simp @member` / `!!fans @member`) untuk menambah jumlah Fans target di Kartu Tanda Panggung. |
| **📜 Misi & Unlock Title Berhalaman** | Title KTP dibuka (*unlocked*) otomatis dari Misi keaktifan event. Tampilan `!!misi` dilengkapi navigasi halaman `◀️` `▶️`. |
| **💵 Ekonomi Rupiah & Toko Berhalaman** | Saldo lokal (Rp), gaji harian (`!!harian`), serta Toko Kosmetik (`!!toko`) interaktif berhalaman (`◀️` `▶️`) dengan pembelian instan via Dropdown. |
| **📖 Role-Based Help System** | Perintah `!!help` secara otomatis menyembunyikan bab-bab khusus Moderator (Filter & Database Admin) dari member biasa. |
| **Sistem Persistence SQLite** | Antrean Karaoke, sesi Sajam, dan event Giveaway aktif tersimpan di SQLite sehingga **tidak hilang/rusak meskipun bot di-restart**. |
| **Manajemen Backup via Discord** | Moderator dapat mengelola cadangan database langsung lewat chat (`!!db backup`, `!!db list`, `!!db restore`). |

========================================================================================================================================================================

🚀 Panduan Instalasi & Persiapan

A. Install Dependency
Buka terminal/command prompt di VS Code (tekan Ctrl + ~), lalu ketik:

  pip install -r requirements.txt

B. Cara Menjalankan Bot

  python main.py

========================================================================================================================================================================

🚀 Panduan Perintah Bot

Catatan: Semua perintah di bawah ini dapat digunakan pada channel yang sudah didaftarkan pada file .env (ALLOWED_CHANNELS) atau di dalam Text Chat Voice Channel.


### 📖 1. Bantuan & Panduan Umum
* **`!!help`**
  Membuka buku panduan interaktif dalam bentuk Dropdown. Menampilkan bab yang disesuaikan dengan hak akses penggunanya (Mod/Member).


### 🪪 2. KTP Digital, Pak Lurah & Sistem Fans
* **`!!lurah`** *(Atau `!!Lurah`)*
  Mendatangi Pak Lurah untuk mendaftar KTP baru atau merevisi data KTP (Nama, Gender, Status) via formulir Modal Popup.
* **`!!ktp`** *(Atau `!!ktp @member` / `!!ktp M5-0000-0001`)*
  Menampilkan KTP Digital 2 Halaman milik sendiri, member lain via Mention, atau via **NIM Unik**.
  - Gunakan tombol **`▶️`** untuk beralih ke Kartu Tanda Panggung.
  - Gunakan tombol **`⚙️`** di Halaman 2 untuk memasang Title & Oshi VTuber secara real-time.
* **`!!simp @member`** *(Atau `!!fans @member`)*
  Memberikan apresiasi Fans kepada member lain (+1 Fans pada Kartu Tanda Panggung target).


### 🎤 3. Karaoke Santai Mandiri (Untuk Semua Member)
* **`!!q`** *(Atau `!!queue`, `!!karaoke`)*
  Menampilkan/memanggil ulang panel antrean karaoke santai 2 box terpisah di posisi terbawah chat (otomatis menghapus panel lama).
* **`!!qj`** *(Atau `!!qjoin`)*
  Pintasan teks cepat untuk bergabung ke antrean karaoke.
* **`!!ql`** *(Atau `!!qleave`)*
  Pintasan teks cepat untuk keluar dari antrean karaoke.
* **`!!qd`** *(Atau `!!qdone`)*
  Pintasan teks selesai tampil *(Khusus penyanyi aktif di panggung)*.
* **`!!qskip`** *(Atau `!!qn`, `!!qnext`)*
  Memberikan vote skip untuk menurunkan penyanyi AFK/stuck. Membutuhkan vote sebanyak **¼ dari warga VC** (atau langsung lengser jika ditekan Moderator).
* **`!!qclear`** *(Khusus Mod/Admin)*
  Membersihkan seluruh antrean karaoke.


### 📜 4. Misi & Pencapaian Title
* **`!!misi`** *(Atau `!!title`)*
  Melihat daftar semua Misi pencapaian Title berhalaman (`◀️` `▶️`) lengkap dengan status **`✅ TERBUKA`** atau **`🔒 TERKUNCI`**.


### 💵 5. Ekonomi Rupiah & Toko Kosmetik
* **`!!saldo`** *(Atau `!!dompet`, `!!bal`)*
  Mengecek total saldo Rupiah (Rp) milik sendiri atau member lain.
* **`!!harian`** *(Atau `!!daily`, `!!gaji`)*
  Mengklaim gaji harian berupa uang Rupiah acak (Rp 30.000 – Rp 75.000) setiap 24 jam sekali.
* **`!!toko`** *(Atau `!!shop`, `!!beli`)*
  Membuka Toko Kosmetik Title Berhalaman (`◀️` `▶️`). Pembelian dilakukan langsung via **Menu Dropdown** di bawah toko tanpa perlu mengetik perintah.


### 🎲 6. Gacha Slot Event PPKM (Khusus Mod/Admin)
* **`!!ppkm [jumlah_slot] [durasi] [channel_target]`**
  Memulai gacha slot PPKM dengan tombol pendaftaran interaktif dan counter peserta real-time.
  *Contoh:* `!!ppkm 3 25s #event-voice`
* **`!!reroll`**
  Mengundi ulang seluruh pemenang gacha terakhir.
* **`!!reroll @NamaMember`**
  Mengundi ulang pemenang tertentu saja (mencoret pemenang lama dan mencarikan penggantinya).
* **`!!ppkmconfig`**
  Membuka panel interaktif untuk mengelola role blacklist/whitelist & user blacklist.


### 🎙️ 7. Sesi Jamming / Panggung Sajam Resmi (Khusus Mod/Admin)
* **`!!sajam start`**
  Memulai sesi Sajam Resmi di Voice Channel tempat Anda bergabung saat ini.
* **`!!sajam`** *(Atau `!!s`)*
  Recall / menampilkan ulang panel antrean Sajam terupdate.
* **`!!sajam end`**
  Mengakhiri seluruh sesi Sajam dan menampilkan rekapitulasi statistik lengkap panggung.


### 🎁 8. Event Giveaway (Khusus Mod/Admin)
* **`!!giveaway`**
  Membuka panel pembuat giveaway. Klik tombol "Buat Giveaway 🎁" untuk mengisi formulir Modal Popup.


### 💾 9. Manajemen Backup Database (Khusus Mod/Admin)
* **`!!db`**
  Menampilkan panduan singkat perintah database.
* **`!!db backup`**
  Membuat salinan cadangan instan file database SQLite di folder `data/backups/`.
* **`!!db list`**
  Menampilkan daftar 10 file backup database terbaru lengkap beserta tanggal dan ukurannya.
* **`!!db restore [nama_file_backup.db]`**
  Memulihkan database utama menggunakan file cadangan pilihan (dilengkapi tombol konfirmasi keamanan).

========================================================================================================================================================================

❓ FAQ

1. **Kok bot-nya ga ngerespon sama sekali pas aku ketik perintah?**
   - **Salah Channel:** Pastikan Anda mengetik perintah di salah satu channel yang ID-nya tercantum di `.env` (`ALLOWED_CHANNELS`) atau di dalam *Text Chat Voice Channel*.
   - **Izin Kurang:** Perintah admin/mod memerlukan izin sistem Discord bernama *"Manage Server"* (Kelola Server).
   - **Bot Offline:** Periksa terminal/CMD di laptop/hosting Anda, pastikan proses `python main.py` masih berjalan.

2. **Bagaimana cara mencari KTP member menggunakan NIM Unik?**
   - Cukup ketik `!!ktp` diikuti dengan NIM member tersebut.
   - *Contoh:* `!!ktp M5-0000-0001`

3. **Gimana cara membuka/mendapatkan Title KTP baru?**
   - Title bisa didapatkan lewat 2 cara:
     1. **Menyelesaikan Misi:** Ketik `!!misi` untuk melihat syarat keaktifan event (Sajam, Karaoke, PPKM, Giveaway, atau Fans).
     2. **Membeli di Toko:** Ketik `!!toko` lalu pilih Title eksklusif pilihanmu di menu dropdown menggunakan saldo Rupiah harian Anda.

4. **Apakah antrean Karaoke atau Giveaway hilang jika bot dimatikan?**
   - **TIDAK!** Sistem dilengkapi *SQLite Persistence*. Antrean Karaoke, penyanyi aktif, dan timer Giveaway akan otomatis dipulihkan persis seperti posisi terakhir saat bot dinyalakan kembali.

5. **Gimana cara menurunkan penyanyi Karaoke yang AFK / tidak mau turun?**
   - Member lain bisa menekan tombol **`⏩ Turunkan / Skip`** atau mengetik **`!!qskip`**. Jika jumlah vote mencapai **¼ dari total warga VC**, penyanyi tersebut akan otomatis diturunkan. Moderator bisa menekan tombol tersebut untuk langsung menurunkan penyanyi secara instan.

========================================================================================================================================================================

# Pembatas Channel (cog_check)

    async def cog_check(self, ctx):
        """Memastikan perintah dapat dijalankan di channel terdaftar atau Voice Channel."""
        if isinstance(ctx.channel, (discord.VoiceChannel, discord.StageChannel)):
            return True
            
        import os
        allowed_env = os.getenv("ALLOWED_CHANNELS", "967590921510191104,1134648796366786611")
        ALLOWED_CHANNEL_IDS = {int(cid.strip()) for cid in allowed_env.split(",") if cid.strip().isdigit()}
        
        if ctx.channel.id not in ALLOWED_CHANNEL_IDS:
            allowed_mentions = " atau ".join([f"<#{cid}>" for cid in ALLOWED_CHANNEL_IDS])
            await ctx.send(
                f"⚠️ Maaf {ctx.author.mention}, perintah bot ini hanya dapat digunakan di {allowed_mentions}.", 
                delete_after=5
            )
            return False
        return True

========================================================================================================================================================================