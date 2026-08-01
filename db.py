import aiosqlite

DB_NAME = "bot_database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                status TEXT DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER,
                sender_id INTEGER,
                file_type TEXT,
                file_id TEXT,
                caption TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS replies (
                reply_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER,
                admin_id INTEGER,
                file_type TEXT,
                file_id TEXT,
                caption TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
            )
        """)
        await db.commit()

async def add_user(user_id: int, full_name: str, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users (user_id, full_name, username) 
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
            full_name = excluded.full_name, 
            username = excluded.username
        """, (user_id, full_name, username))
        await db.commit()

async def get_user_open_tickets_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM tickets WHERE user_id = ? AND status = 'Open'", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def create_ticket(user_id: int, title: str) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "INSERT INTO tickets (user_id, title, status) VALUES (?, ?, 'Open')",
            (user_id, title)
        )
        await db.commit()
        return cursor.lastrowid

async def add_ticket_message(ticket_id: int, sender_id: int, file_type: str, file_id: str, caption: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO messages (ticket_id, sender_id, file_type, file_id, caption) VALUES (?, ?, ?, ?, ?)",
            (ticket_id, sender_id, file_type, file_id, caption)
        )
        await db.commit()

async def get_user_tickets(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tickets WHERE user_id = ? ORDER BY ticket_id DESC", (user_id,)) as cursor:
            return await cursor.fetchall()

async def get_ticket_by_id(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)) as cursor:
            return await cursor.fetchone()

async def get_ticket_messages(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM messages WHERE ticket_id = ? ORDER BY message_id ASC", (ticket_id,)) as cursor:
            return await cursor.fetchall()

async def get_ticket_replies(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM replies WHERE ticket_id = ? ORDER BY reply_id ASC", (ticket_id,)) as cursor:
            return await cursor.fetchall()

async def add_reply(ticket_id: int, admin_id: int, file_type: str, file_id: str, caption: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO replies (ticket_id, admin_id, file_type, file_id, caption) VALUES (?, ?, ?, ?, ?)",
            (ticket_id, admin_id, file_type, file_id, caption)
        )
        await db.commit()

async def close_ticket(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE tickets SET status = 'Closed' WHERE ticket_id = ?", (ticket_id,))
        await db.commit()

async def get_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            users_count = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Open'") as c:
            open_tickets = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Closed'") as c:
            closed_tickets = (await c.fetchone())[0]
        async with db.execute("SELECT (SELECT COUNT(*) FROM messages) + (SELECT COUNT(*) FROM replies)") as c:
            total_msgs = (await c.fetchone())[0]
        return users_count, open_tickets, closed_tickets, total_msgs

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as c:
            rows = await c.fetchall()
            return [row[0] for row in rows]

async def get_tickets_by_status(status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tickets WHERE status = ? ORDER BY ticket_id DESC", (status,)) as cursor:
            return await cursor.fetchall()

async def get_all_users_details():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY joined_at DESC") as cursor:
            return await cursor.fetchall()