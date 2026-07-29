import sqlite3
import os
import asyncio
from datetime import datetime, timedelta
from core.safety import safe_write_json, backup_sqlite_database

DB_PATH = "data/event_bot.db"

class SQLiteDatabase:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        backup_sqlite_database(self.db_path)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        # --- PERBAIKAN: Aktifkan WAL Mode & Pengaturan Performa Concurrent ---
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        """Membuat tabel-tabel penting jika belum ada."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Tabel PPKM
            cursor.execute("CREATE TABLE IF NOT EXISTS ppkm_roles (role_id INTEGER PRIMARY KEY, type TEXT NOT NULL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS ppkm_users (user_id INTEGER PRIMARY KEY, type TEXT NOT NULL)")
            
            # 2. Tabel Sajam
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sajam_session (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    is_active INTEGER DEFAULT 0,
                    queue_open INTEGER DEFAULT 1,
                    voice_channel_id INTEGER,
                    current_performer_id INTEGER,
                    start_time TEXT,
                    peak_visitors INTEGER DEFAULT 0,
                    peak_queue INTEGER DEFAULT 0,
                    active_message_id INTEGER,
                    active_message_channel_id INTEGER
                )
            """)
            cursor.execute("INSERT OR IGNORE INTO sajam_session (id) VALUES (1)")
            cursor.execute("CREATE TABLE IF NOT EXISTS sajam_queue (user_id INTEGER PRIMARY KEY, position INTEGER NOT NULL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS sajam_sing_count (user_id INTEGER PRIMARY KEY, count INTEGER DEFAULT 0)")
            cursor.execute("CREATE TABLE IF NOT EXISTS sajam_vc_participants (user_id INTEGER PRIMARY KEY)")

            # 3. [MULTI-CHANNEL] Tabel Persistence Karaoke
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS karaoke_sessions (
                    channel_id INTEGER PRIMARY KEY,
                    current_performer_id INTEGER,
                    active_message_id INTEGER
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS karaoke_queues (
                    channel_id INTEGER,
                    user_id INTEGER,
                    position INTEGER,
                    PRIMARY KEY (channel_id, user_id)
                )
            """)

            # 4. Tabel Persistence Giveaway
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS giveaways (
                    message_id INTEGER PRIMARY KEY,
                    channel_id INTEGER NOT NULL,
                    prize TEXT NOT NULL,
                    winners_count INTEGER NOT NULL,
                    end_time TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS giveaway_participants (
                    message_id INTEGER,
                    user_id INTEGER,
                    PRIMARY KEY (message_id, user_id)
                )
            """)

            # 5. Tabel KTP Member
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ktp_profiles (
                    user_id INTEGER PRIMARY KEY,
                    nim TEXT UNIQUE NOT NULL,
                    nama TEXT NOT NULL,
                    gender TEXT DEFAULT 'Cowok',
                    status TEXT DEFAULT 'Jomblo',
                    title TEXT DEFAULT 'Warga Teladan',
                    simp_vtuber TEXT DEFAULT 'Belum Memilih',
                    created_at TEXT
                )
            """)

            # 6. Tabel Fans & Event Stats
            cursor.execute("CREATE TABLE IF NOT EXISTS ktp_fans (target_id INTEGER, giver_id INTEGER, PRIMARY KEY (target_id, giver_id))")
            cursor.execute("CREATE TABLE IF NOT EXISTS user_event_stats (user_id INTEGER, event_type TEXT, count INTEGER DEFAULT 0, PRIMARY KEY (user_id, event_type))")

            # 7. Tabel Ekonomi & Title
            cursor.execute("CREATE TABLE IF NOT EXISTS user_economy (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, last_daily TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS user_title_inventory (user_id INTEGER, title TEXT, PRIMARY KEY (user_id, title))")

            # 8. Tabel Activity Logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    details TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            # 9. Tabel Energi Pekerjaan
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_job_energy (
                    user_id INTEGER PRIMARY KEY,
                    energy INTEGER DEFAULT 5,
                    last_reset TEXT
                )
            """)

            conn.commit()

    # --- METODE PPKM & SAJAM ---
    async def load_roles_config(self):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT role_id, type FROM ppkm_roles")
                rows = cursor.fetchall()
                return {row[0] for row in rows if row[1] == 'blacklist'}, {row[0] for row in rows if row[1] == 'whitelist'}
        return await asyncio.to_thread(_op)

    async def load_user_blacklist(self):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM ppkm_users WHERE type = 'blacklist'")
                return {row[0] for row in cursor.fetchall()}
        return await asyncio.to_thread(_op)

    async def save_roles_config(self, blacklisted_roles, whitelisted_roles):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ppkm_roles")
                for r_id in blacklisted_roles:
                    cursor.execute("INSERT INTO ppkm_roles (role_id, type) VALUES (?, 'blacklist')", (r_id,))
                for r_id in whitelisted_roles:
                    cursor.execute("INSERT INTO ppkm_roles (role_id, type) VALUES (?, 'whitelist')", (r_id,))
                conn.commit()
        await asyncio.to_thread(_op)

    async def save_user_blacklist(self, blacklisted_users):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ppkm_users")
                for u_id in blacklisted_users:
                    cursor.execute("INSERT INTO ppkm_users (user_id, type) VALUES (?, 'blacklist')", (u_id,))
                conn.commit()
        await asyncio.to_thread(_op)

    # SAJAM PERSISTENCE
    async def save_sajam_session(self, is_active, queue_open, voice_channel_id, current_performer_id, start_time, peak_visitors, peak_queue, active_message_id, active_message_channel_id):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sajam_session SET is_active=?, queue_open=?, voice_channel_id=?, current_performer_id=?, 
                    start_time=?, peak_visitors=?, peak_queue=?, active_message_id=?, active_message_channel_id=? WHERE id=1
                """, (1 if is_active else 0, 1 if queue_open else 0, voice_channel_id, current_performer_id, start_time, peak_visitors, peak_queue, active_message_id, active_message_channel_id))
                conn.commit()
        await asyncio.to_thread(_op)

    async def load_sajam_session(self):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT is_active, queue_open, voice_channel_id, current_performer_id, start_time, peak_visitors, peak_queue, active_message_id, active_message_channel_id FROM sajam_session WHERE id=1")
                return cursor.fetchone()
        return await asyncio.to_thread(_op)

    async def save_sajam_queue(self, queue_list):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sajam_queue")
                for pos, user_id in enumerate(queue_list):
                    cursor.execute("INSERT INTO sajam_queue (user_id, position) VALUES (?, ?)", (user_id, pos))
                conn.commit()
        await asyncio.to_thread(_op)

    async def load_sajam_queue(self):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM sajam_queue ORDER BY position ASC")
                return [row[0] for row in cursor.fetchall()]
        return await asyncio.to_thread(_op)

    async def save_sajam_sing_count(self, sing_count_dict):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sajam_sing_count")
                for u_id, count in sing_count_dict.items():
                    cursor.execute("INSERT INTO sajam_sing_count (user_id, count) VALUES (?, ?)", (u_id, count))
                conn.commit()
        await asyncio.to_thread(_op)

    async def load_sajam_sing_count(self):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, count FROM sajam_sing_count")
                return {row[0]: row[1] for row in cursor.fetchall()}
        return await asyncio.to_thread(_op)

    async def save_sajam_vc_participants(self, participants_set):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sajam_vc_participants")
                for u_id in participants_set:
                    cursor.execute("INSERT INTO sajam_vc_participants (user_id) VALUES (?)", (u_id,))
                conn.commit()
        await asyncio.to_thread(_op)

    async def load_sajam_vc_participants(self):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM sajam_vc_participants")
                return {row[0] for row in cursor.fetchall()}
        return await asyncio.to_thread(_op)

    async def clear_sajam_data(self):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE sajam_session SET is_active=0, queue_open=1, voice_channel_id=NULL, current_performer_id=NULL, start_time=NULL, peak_visitors=0, peak_queue=0, active_message_id=NULL, active_message_channel_id=NULL WHERE id=1")
                cursor.execute("DELETE FROM sajam_queue")
                cursor.execute("DELETE FROM sajam_sing_count")
                cursor.execute("DELETE FROM sajam_vc_participants")
                conn.commit()
        await asyncio.to_thread(_op)

    # --- METODE MULTI-CHANNEL KARAOKE PERSISTENCE ---
    async def save_karaoke_session(self, channel_id: int, performer_id: int, msg_id: int, queue_ids: list):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO karaoke_sessions (channel_id, current_performer_id, active_message_id)
                    VALUES (?, ?, ?)
                    ON CONFLICT(channel_id) DO UPDATE SET current_performer_id=?, active_message_id=?
                """, (channel_id, performer_id, msg_id, performer_id, msg_id))
                
                cursor.execute("DELETE FROM karaoke_queues WHERE channel_id = ?", (channel_id,))
                for pos, u_id in enumerate(queue_ids):
                    cursor.execute("INSERT INTO karaoke_queues (channel_id, user_id, position) VALUES (?, ?, ?)", (channel_id, u_id, pos))
                conn.commit()
        await asyncio.to_thread(_op)

    async def clear_karaoke_session_db(self, channel_id: int):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM karaoke_sessions WHERE channel_id = ?", (channel_id,))
                cursor.execute("DELETE FROM karaoke_queues WHERE channel_id = ?", (channel_id,))
                conn.commit()
        await asyncio.to_thread(_op)

    async def load_all_karaoke_sessions(self) -> dict:
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT channel_id, current_performer_id, active_message_id FROM karaoke_sessions")
                rows = cursor.fetchall()
                
                result = {}
                for chan_id, perf_id, msg_id in rows:
                    cursor.execute("SELECT user_id FROM karaoke_queues WHERE channel_id = ? ORDER BY position ASC", (chan_id,))
                    q_ids = [r[0] for r in cursor.fetchall()]
                    result[chan_id] = {
                        "performer_id": perf_id,
                        "msg_id": msg_id,
                        "queue_ids": q_ids
                    }
                return result
        return await asyncio.to_thread(_op)

    # --- METODE GIVEAWAY PERSISTENCE ---
    async def save_giveaway(self, message_id, channel_id, prize, winners_count, end_time_iso):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO giveaways (message_id, channel_id, prize, winners_count, end_time, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (message_id, channel_id, prize, winners_count, end_time_iso))
                conn.commit()
        await asyncio.to_thread(_op)

    async def add_giveaway_participant(self, message_id, user_id):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO giveaway_participants (message_id, user_id) VALUES (?, ?)", (message_id, user_id))
                conn.commit()
        await asyncio.to_thread(_op)

    async def get_giveaway_participants(self, message_id):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM giveaway_participants WHERE message_id = ?", (message_id,))
                return [r[0] for r in cursor.fetchall()]
        return await asyncio.to_thread(_op)

    async def get_active_giveaways(self):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT message_id, channel_id, prize, winners_count, end_time FROM giveaways WHERE is_active = 1")
                return cursor.fetchall()
        return await asyncio.to_thread(_op)

    async def end_giveaway_db(self, message_id):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE giveaways SET is_active = 0 WHERE message_id = ?", (message_id,))
                conn.commit()
        await asyncio.to_thread(_op)

    # --- METODE KTP & PROFILE ---
    async def get_ktp_count(self) -> int:
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM ktp_profiles")
                res = cursor.fetchone()
                return res[0] if res else 0
        return await asyncio.to_thread(_op)

    async def get_ktp_profile(self, identifier):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
                    cursor.execute("SELECT user_id, nim, nama, gender, status, title, simp_vtuber FROM ktp_profiles WHERE user_id = ?", (int(identifier),))
                else:
                    cursor.execute("SELECT user_id, nim, nama, gender, status, title, simp_vtuber FROM ktp_profiles WHERE UPPER(nim) = UPPER(?)", (str(identifier).strip(),))
                return cursor.fetchone()
        return await asyncio.to_thread(_op)

    async def save_ktp_profile(self, user_id: int, nama: str, gender: str, status: str, nim: str = None):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nim FROM ktp_profiles WHERE user_id = ?", (user_id,))
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute("UPDATE ktp_profiles SET nama = ?, gender = ?, status = ? WHERE user_id = ?", (nama, gender, status, user_id))
                    updated_nim = existing[0]
                else:
                    cursor.execute("""
                        INSERT INTO ktp_profiles (user_id, nim, nama, gender, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, nim, nama, gender, status, datetime.now().isoformat()))
                    updated_nim = nim
                    
                conn.commit()
                return updated_nim
        return await asyncio.to_thread(_op)

    async def update_ktp_title_simp(self, user_id: int, title: str = None, simp_vtuber: str = None):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if title:
                    cursor.execute("UPDATE ktp_profiles SET title = ? WHERE user_id = ?", (title, user_id))
                if simp_vtuber:
                    cursor.execute("UPDATE ktp_profiles SET simp_vtuber = ? WHERE user_id = ?", (simp_vtuber, user_id))
                conn.commit()
        await asyncio.to_thread(_op)

    async def is_nim_exists(self, nim: str) -> bool:
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM ktp_profiles WHERE nim = ?", (nim,))
                return cursor.fetchone() is not None
        return await asyncio.to_thread(_op)

    # --- FANS / SIMP SYSTEM ---
    async def add_fan(self, target_id: int, giver_id: int) -> bool:
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO ktp_fans (target_id, giver_id) VALUES (?, ?)", (target_id, giver_id))
                    conn.commit()
                    return True
                except sqlite3.IntegrityError:
                    return False
        return await asyncio.to_thread(_op)

    async def get_fans_count(self, target_id: int) -> int:
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM ktp_fans WHERE target_id = ?", (target_id,))
                res = cursor.fetchone()
                return res[0] if res else 0
        return await asyncio.to_thread(_op)

    # --- STATISTIK EVENT ---
    async def increment_event_stat(self, user_id: int, event_type: str):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_event_stats (user_id, event_type, count) VALUES (?, ?, 1)
                    ON CONFLICT(user_id, event_type) DO UPDATE SET count = count + 1
                """, (user_id, event_type))
                conn.commit()
        await asyncio.to_thread(_op)

    async def get_all_event_stats(self, user_id: int) -> dict:
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT count FROM sajam_sing_count WHERE user_id = ?", (user_id,))
                sajam_res = cursor.fetchone()
                sajam_count = sajam_res[0] if sajam_res else 0

                cursor.execute("SELECT event_type, count FROM user_event_stats WHERE user_id = ?", (user_id,))
                rows = cursor.fetchall()
                
                stats = {'sajam': sajam_count, 'karaoke': 0, 'ppkm': 0, 'giveaway': 0}
                for r in rows:
                    stats[r[0]] = r[1]
                return stats
        return await asyncio.to_thread(_op)

    # --- METODE EKONOMI RUPIAH ---
    async def get_balance(self, user_id: int) -> int:
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT balance FROM user_economy WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                return row[0] if row else 0
        return await asyncio.to_thread(_op)

    async def add_balance(self, user_id: int, amount: int):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_economy (user_id, balance) VALUES (?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?
                """, (user_id, amount, amount))
                conn.commit()
        await asyncio.to_thread(_op)

    async def claim_daily_reward(self, user_id: int, reward_amount: int):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now()
                cursor.execute("SELECT last_daily FROM user_economy WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if row and row[0]:
                    last_claim = datetime.fromisoformat(row[0])
                    if now - last_claim < timedelta(hours=24):
                        remaining = timedelta(hours=24) - (now - last_claim)
                        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                        minutes, _ = divmod(remainder, 60)
                        return False, f"{hours} jam {minutes} menit"
                
                cursor.execute("""
                    INSERT INTO user_economy (user_id, balance, last_daily) VALUES (?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?, last_daily = ?
                """, (user_id, reward_amount, now.isoformat(), reward_amount, now.isoformat()))
                conn.commit()
                return True, ""
        return await asyncio.to_thread(_op)

    # --- METODE INVENTARIS TITLE ---
    async def add_title_to_inventory(self, user_id: int, title: str):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO user_title_inventory (user_id, title) VALUES (?, ?)", (user_id, title))
                conn.commit()
        await asyncio.to_thread(_op)

    async def get_user_title_inventory(self, user_id: int) -> set:
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT title FROM user_title_inventory WHERE user_id = ?", (user_id,))
                return {row[0] for row in cursor.fetchall()}
        return await asyncio.to_thread(_op)

    # --- METODE LOG AKTIVITAS & REKAP MINGGUAN ---
    async def log_activity(self, user_id: int, action_type: str, details: str = ""):
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO activity_logs (user_id, action_type, details, created_at)
                    VALUES (?, ?, ?, ?)
                """, (user_id, action_type, details, datetime.now().isoformat()))
                conn.commit()
        await asyncio.to_thread(_op)

    async def get_weekly_recap_data(self) -> dict:
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
                
                cursor.execute("SELECT COUNT(*), COUNT(DISTINCT user_id) FROM activity_logs WHERE created_at >= ?", (seven_days_ago,))
                row_tot = cursor.fetchone()
                total_actions = row_tot[0] if row_tot else 0
                active_users = row_tot[1] if row_tot else 0

                cursor.execute("SELECT action_type, COUNT(*) FROM activity_logs WHERE created_at >= ? GROUP BY action_type", (seven_days_ago,))
                action_counts = dict(cursor.fetchall())

                cursor.execute("""
                    SELECT user_id, COUNT(*) as cnt FROM activity_logs 
                    WHERE created_at >= ? AND action_type IN ('karaoke', 'sajam')
                    GROUP BY user_id ORDER BY cnt DESC LIMIT 3
                """, (seven_days_ago,))
                top_singers = cursor.fetchall()

                cursor.execute("""
                    SELECT target_id, COUNT(*) as cnt FROM ktp_fans 
                    GROUP BY target_id ORDER BY cnt DESC LIMIT 3
                """)
                top_fans = cursor.fetchall()

                return {
                    "total_actions": total_actions,
                    "active_users": active_users,
                    "actions": action_counts,
                    "top_singers": top_singers,
                    "top_fans": top_fans
                }
        return await asyncio.to_thread(_op)

# --- METODE ENERGI PEKERJAAN ---
    async def get_job_energy(self, user_id: int) -> tuple[int, str]:
        """Mengambil energi kerja member & otomatis reset ke 5 jika sudah 24 jam."""
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now()
                cursor.execute("SELECT energy, last_reset FROM user_job_energy WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if not row:
                    cursor.execute("INSERT INTO user_job_energy (user_id, energy, last_reset) VALUES (?, 5, ?)", (user_id, now.isoformat()))
                    conn.commit()
                    return 5, ""
                
                energy, last_reset_str = row[0], row[1]
                if last_reset_str:
                    last_reset = datetime.fromisoformat(last_reset_str)
                    if now - last_reset >= timedelta(hours=24):
                        cursor.execute("UPDATE user_job_energy SET energy = 5, last_reset = ? WHERE user_id = ?", (now.isoformat(), user_id))
                        conn.commit()
                        return 5, ""
                    else:
                        remaining = timedelta(hours=24) - (now - last_reset)
                        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                        minutes, _ = divmod(remainder, 60)
                        return energy, f"{hours} jam {minutes} menit"
                return energy, ""
        return await asyncio.to_thread(_op)

    async def consume_job_energy(self, user_id: int) -> bool:
        """Mengurangi 1 energi kerja member."""
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE user_job_energy SET energy = energy - 1 WHERE user_id = ? AND energy > 0", (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        return await asyncio.to_thread(_op)

    async def add_job_energy(self, user_id: int, amount: int = 5):
        """Memulihkan/Menambah energi kerja member (Maksimal 5)."""
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT energy FROM user_job_energy WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                now = datetime.now().isoformat()
                
                if row:
                    new_energy = min(5, row[0] + amount)
                    cursor.execute("UPDATE user_job_energy SET energy = ? WHERE user_id = ?", (new_energy, user_id))
                else:
                    cursor.execute("INSERT INTO user_job_energy (user_id, energy, last_reset) VALUES (?, ?, ?)", (user_id, min(5, amount), now))
                conn.commit()
        await asyncio.to_thread(_op)

    async def cleanup_old_logs(self, days: int = 30):
        """Menghapus activity logs yang lebih lama dari N hari."""
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cutoff = (datetime.now() - timedelta(days=days)).isoformat()
                cursor.execute("DELETE FROM activity_logs WHERE created_at < ?", (cutoff,))
                conn.commit()
        await asyncio.to_thread(_op)

# --- METODE EKONOMI MAKRO DINAMIS ---
    async def get_macro_stats(self) -> tuple[int, int, int]:
        """Mengambil Total Uang Beredar, Rata-rata Saldo, dan Total Warga Ber-KTP."""
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT SUM(e.balance), AVG(e.balance), COUNT(k.user_id) 
                    FROM ktp_profiles k 
                    LEFT JOIN user_economy e ON k.user_id = e.user_id
                """)
                row = cursor.fetchone()
                total_money = row[0] if row and row[0] else 0
                avg_money = int(row[1]) if row and row[1] else 0
                total_citizens = row[2] if row and row[2] else 1
                return total_money, avg_money, total_citizens
        return await asyncio.to_thread(_op)

    async def get_job_demand_stats(self) -> dict:
        """Menghitung frekuensi pengerjaan job dalam 24 jam terakhir."""
        def _op():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
                cursor.execute("""
                    SELECT details, COUNT(*) FROM activity_logs 
                    WHERE action_type = 'job_exec' AND created_at >= ? 
                    GROUP BY details
                """, (cutoff,))
                return dict(cursor.fetchall())
        return await asyncio.to_thread(_op)

database = SQLiteDatabase()