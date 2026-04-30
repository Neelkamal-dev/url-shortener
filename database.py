import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from flask import g

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///urls.db')

# Render gives 'postgres://' but SQLAlchemy needs 'postgresql://'
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Split into separate statements for SQLite compatibility
STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS urls (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        original_url  TEXT NOT NULL,
        short_code    VARCHAR(20) NOT NULL UNIQUE,
        clicks        INTEGER DEFAULT 0,
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_accessed TIMESTAMP
    )""",
    "CREATE INDEX IF NOT EXISTS idx_short_code ON urls(short_code)"
]


def init_db():
    with engine.connect() as conn:
        for stmt in STATEMENTS:
            conn.execute(text(stmt))
        conn.commit()
    db_type = DATABASE_URL.split('://')[0]
    print(f"✅ Database initialized ({db_type})")


def get_db():
    if 'db' not in g:
        g.db = engine.connect()
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
