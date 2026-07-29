import sqlite3
import os
import asyncio
from datetime import datetime
from core.safety import backup_sqlite_database

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

            # 3. Tabel Persistence Karaoke
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

database = SQLiteDatabase()