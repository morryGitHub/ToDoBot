# 📁 data/database.py
from sqlite3 import connect
from typing import List, Dict, Any

DB_NAME = "data.db"

def init_db():
    with connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT NOT NULL,
                time TEXT NOT NULL,
                is_done BOOLEAN DEFAULT 0,
                is_remind BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                remind_time TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            );
        """)
        conn.commit()

def add_task_to_db(user_id: int, text: str, time: str):
    with connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        cursor.execute(
            "INSERT INTO tasks (user_id, text, time) VALUES (?, ?, ?)",
            (user_id, text, time)
        )
        conn.commit()

def get_user_tasks(user_id: int) -> List[Dict[str, Any]]:
    with connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, text, time, is_done, is_remind FROM tasks WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "task": row[1],
                "time": row[2],
                "is_done": bool(row[3]),
                "is_remind": bool(row[4]),
            } for row in rows
        ]

def update_task_time(task_id: int, new_time: str):
    with connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks SET time = ?, is_remind = 0 WHERE id = ?
        """, (new_time, task_id))
        conn.commit()

def delete_task(task_id: int):
    with connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        cursor.execute("DELETE FROM reminders WHERE task_id = ?", (task_id,))
        conn.commit()

def mark_task_done(task_id: int):
    with connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET is_done = 1 WHERE id = ?", (task_id,))
        conn.commit()

def set_task_remind_status(task_id: int, status: bool):
    with connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET is_remind = ? WHERE id = ?", (int(status), task_id))
        conn.commit()

def add_reminder(task_id: int, remind_time: str):
    with connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (task_id, remind_time, status) VALUES (?, ?, ?)",
            (task_id, remind_time, "pending")
        )
        conn.commit()

def remove_reminder(task_id: int):
    with connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE task_id = ? AND status = 'pending'", (task_id,))
        conn.commit()

init_db()