import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "keluhin.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                                                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                 nama TEXT NOT NULL,
                                                 email TEXT NOT NULL UNIQUE,
                                                 password_hash TEXT NOT NULL,
                                                 peran TEXT NOT NULL
                                                     CHECK (peran IN ('pelanggan', 'agen')),
                                                 dibuat_pada TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS kategori (
                                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                    nama TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS tiket (
                                                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                 judul TEXT NOT NULL,
                                                 deskripsi TEXT NOT NULL,
                                                 prioritas TEXT NOT NULL,
                                                 kategori_id INTEGER NOT NULL,
                                                 pembuat_id INTEGER NOT NULL,
                                                 status TEXT NOT NULL DEFAULT 'baru',
                                                 dibuat_pada TEXT NOT NULL,
                                                 diperbarui_pada TEXT NOT NULL,

                                                 FOREIGN KEY (kategori_id)
                                                     REFERENCES kategori(id),

                                                 FOREIGN KEY (pembuat_id)
                                                     REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS riwayat_status (
                                                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                          tiket_id INTEGER NOT NULL,
                                                          status_lama TEXT,
                                                          status_baru TEXT NOT NULL,
                                                          pengubah_id INTEGER NOT NULL,
                                                          dibuat_pada TEXT NOT NULL,

                                                          FOREIGN KEY (tiket_id)
                                                              REFERENCES tiket(id)
                                                              ON DELETE CASCADE,

                                                          FOREIGN KEY (pengubah_id)
                                                              REFERENCES users(id)
            );
            """
        )

        _seed_kategori(cursor)

        connection.commit()

    finally:
        connection.close()


def _seed_kategori(cursor):
    kategori = [
        "Aplikasi",
        "Pembayaran",
        "Akun",
        "Layanan",
        "Infrastruktur",
        "Lainnya",
    ]

    for nama in kategori:
        cursor.execute(
            """
            INSERT OR IGNORE INTO kategori (nama)
            VALUES (?)
            """,
            (nama,),
        )