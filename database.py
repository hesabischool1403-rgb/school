import aiosqlite
from pathlib import Path

DB_PATH = "school.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER UNIQUE,
                name TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER,
                name TEXT,
                FOREIGN KEY(school_id) REFERENCES schools(id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                national_id TEXT,
                FOREIGN KEY(school_id) REFERENCES schools(id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER,
                first_name TEXT,
                last_name TEXT,
                student_id TEXT,
                FOREIGN KEY(class_id) REFERENCES classes(id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date TEXT,
                present BOOLEAN,
                FOREIGN KEY(student_id) REFERENCES students(id)
            )
        ''')
        await db.commit()