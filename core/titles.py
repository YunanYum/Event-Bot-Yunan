# core/titles.py

# --- KAMUS SYARAT MISI UNTUK UNLOCK TITLE ---
TITLE_MISSIONS = {
    "Warga Teladan": {
        "emoji": "🛡️",
        "misi": "Title dasar seluruh warga MAHA5",
        "check": lambda stats, fans: True
    },
    "Penyanyi Karaoke": {
        "emoji": "🎤",
        "misi": "Pernah tampil bernyanyi di Karaoke Santai (1x)",
        "check": lambda stats, fans: stats.get("karaoke", 0) >= 1
    },
    "Bintang Karaoke": {
        "emoji": "🎵",
        "misi": "Tampil bernyanyi di Karaoke Santai sebanyak 3x",
        "check": lambda stats, fans: stats.get("karaoke", 0) >= 3
    },
    "SAJAM Singer": {
        "emoji": "🌟",
        "misi": "Pernah tampil bernyanyi di Sajam Resmi (1x)",
        "check": lambda stats, fans: stats.get("sajam", 0) >= 1
    },
    "SAJAM Enjoyer": {
        "emoji": "☕",
        "misi": "Tampil di panggung Sajam Resmi sebanyak 5x",
        "check": lambda stats, fans: stats.get("sajam", 0) >= 5
    },
    "Legend SAJAM": {
        "emoji": "🔥",
        "misi": "Tampil di panggung Sajam Resmi sebanyak 10x",
        "check": lambda stats, fans: stats.get("sajam", 0) >= 10
    },
    "Si Paling PPKM": {
        "emoji": "👑",
        "misi": "Ikut gacha PPKM sebanyak 5x",
        "check": lambda stats, fans: stats.get("ppkm", 0) >= 5
    },
    "Langganan PPKM": {
        "emoji": "🎲",
        "misi": "Ikut gacha PPKM sebanyak 10x",
        "check": lambda stats, fans: stats.get("ppkm", 0) >= 10
    },
    "Sepuh PPKM": {
        "emoji": "🎰",
        "misi": "Ikut gacha PPKM sebanyak 20x",
        "check": lambda stats, fans: stats.get("ppkm", 0) >= 20
    },
    "Penonton Setia": {
        "emoji": "🎧",
        "misi": "Ikut event Giveaway sebanyak 5x",
        "check": lambda stats, fans: stats.get("giveaway", 0) >= 5
    },
    "Pemburu Hadiah": {
        "emoji": "🎁",
        "misi": "Ikut event Giveaway sebanyak 10x",
        "check": lambda stats, fans: stats.get("giveaway", 0) >= 10
    },
    "Pasti Dapet Giveaway": {
        "emoji": "✨",
        "misi": "Ikut event Giveaway sebanyak 20x",
        "check": lambda stats, fans: stats.get("giveaway", 0) >= 20
    },
    "Simp Sejati": {
        "emoji": "🌟",
        "misi": "Memiliki minimal 3 Fans (dari !!simp/@fans)",
        "check": lambda stats, fans: fans >= 3
    },
    "Bintang MAHA5": {
        "emoji": "💎",
        "misi": "Memiliki minimal 10 Fans (dari !!simp/@fans)",
        "check": lambda stats, fans: fans >= 10
    },
    "Artis MAHA5": {
        "emoji": "💖",
        "misi": "Memiliki minimal 25 Fans (dari !!simp/@fans)",
        "check": lambda stats, fans: fans >= 25
    },
    "MAHA5 Idol": {
        "emoji": "💫",
        "misi": "Memiliki minimal 50 Fans (dari !!simp/@fans)",
        "check": lambda stats, fans: fans >= 50
    },
    "Penggiat Event": {
        "emoji": "🎯",
        "misi": "Total keikutsertaan seluruh event mencapai 10x",
        "check": lambda stats, fans: (stats.get("sajam", 0) + stats.get("karaoke", 0) + stats.get("ppkm", 0) + stats.get("giveaway", 0)) >= 10
    },

    "Veteran Server": {
        "emoji": "🏛️",
        "misi": "Total keikutsertaan seluruh event mencapai 30x",
        "check": lambda stats, fans: (stats.get("sajam", 0) + stats.get("karaoke", 0) + stats.get("ppkm", 0) + stats.get("giveaway", 0)) >= 30
    }
}

# --- DAFTAR TITLE KOSMETIK YANG BISA DIBELI DI TOKO ---
SHOP_TITLES = {

    "Kopi Suplemen Energi": {
        "price": 150000, 
        "emoji": "☕", 
        "desc": "Pulihkan +5 Energi Kerja (!!job) secara instan!"
    },
    "Penonton Jam Kalong": {
        "price": 250000, 
        "emoji": "🌙", 
        "desc": "Setia mantengin live stream VTuber sampai subuh"
    },
    "Penikmat Free Chat": {
        "price": 350000, 
        "emoji": "🍵", 
        "desc": "Warga santai yang suka nongkrong di waiting room"
    },
    "Tim Replay Stream": {
        "price": 500000, 
        "emoji": "🎧", 
        "desc": "Tetap setia nonton vod meskipun ketinggalan live"
    },
    "Penghuni Backstage": {
        "price": 650000, 
        "emoji": "🛋️", 
        "desc": "Nongkrong abadi di ruang obrolan server MAHA5"
    },
    "Pamer Badge Member": {
        "price": 750000, 
        "emoji": "💸", 
        "desc": "Hobi pamer badge hijau & emoji eksklusif di chat"
    },
    "Kurir Merch MAHA5": {
        "price": 1000000, 
        "emoji": "🛵", 
        "desc": "Driver ojol langganan antar merchandise & voice pack"
    },
    "Chef Warteg Backstage": {
        "price": 1250000, 
        "emoji": "🍳", 
        "desc": "Ahli goreng mendoan favorit para talent & warga"
    },
    "Jukir Studio MAHA5": {
        "price": 1500000, 
        "emoji": "🅿️", 
        "desc": "Raja jukir pengaman parkiran studio stream"
    },
    "Kasir Fanmerch MAHA5": {
        "price": 1800000, 
        "emoji": "💵", 
        "desc": "Hitung kembalian cepat kilat saat khilaf beli merch"
    },
    "Barista Kafe Backstage": {
        "price": 2000000, 
        "emoji": "☕", 
        "desc": "Racik kopi gula aren penahan kantuk saat stream marathon"
    },
    "Warga Emas Kelurahan": {
        "price": 2500000, 
        "emoji": "✨", 
        "desc": "Gelar eksklusif warga teladan kesayangan kelurahan"
    },
    "Pemberi Saweran Merah": {
        "price": 3500000, 
        "emoji": "🏮", 
        "desc": "Rutin nyawer chat merah pas VTuber stream gacha"
    },
    "Sultan Supachat MAHA5": {
        "price": 5000000, 
        "emoji": "💎", 
        "desc": "Gelar kehormatan penyumbang superchat terbesar"
    },
    "Taipan Membership Tier 3": {
        "price": 7500000, 
        "emoji": "🎩", 
        "desc": "Langganan member tingkat tertinggi di semua channel Oshi"
    },
    "Investor Agensi MAHA5": {
        "price": 12500000, 
        "emoji": "🏛️", 
        "desc": "Sultan kelas kakap penyokong dana project kelurahan"
    },
    "Kolektor Title & Merch": {
        "price": 25000000, 
        "emoji": "👑", 
        "desc": "Gelar bergengsi borong semua kosmetik & merch"
    },
    "Tuan Tanah Backstage": {
        "price": 50000000, 
        "emoji": "🏰", 
        "desc": "Pemilik kapling ruang ngobrol paling luas di server"
    },
    "Petinggi Kelurahan MAHA5": {
        "price": 100000000, 
        "emoji": "💳", 
        "desc": "Kasta tertinggi pemegang kekuasaan ekonomi MAHA5"
    }
}