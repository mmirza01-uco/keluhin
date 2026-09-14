"""Lapisan data: koneksi SQLite, skema, dan data awal (seed) untuk Keluhin."""
import sqlite3, os
from datetime import datetime
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "keluhin.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS pengguna (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nama          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    peran         TEXT NOT NULL CHECK (peran IN ('pelanggan','agen'))
);
CREATE TABLE IF NOT EXISTS kategori (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS tiket (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    judul        TEXT NOT NULL,
    deskripsi    TEXT NOT NULL,
    prioritas    TEXT NOT NULL CHECK (prioritas IN ('Rendah','Sedang','Tinggi')),
    status       TEXT NOT NULL DEFAULT 'Baru' CHECK (status IN ('Baru','Diproses','Selesai','Ditutup')),
    kategori_id  INTEGER REFERENCES kategori(id),
    pembuat_id   INTEGER NOT NULL REFERENCES pengguna(id),
    dibuat_pada  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS log_status (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    tiket_id    INTEGER NOT NULL REFERENCES tiket(id),
    status_lama TEXT,
    status_baru TEXT NOT NULL,
    diubah_oleh INTEGER REFERENCES pengguna(id),
    waktu       TEXT NOT NULL
);
"""


def init_db(seed=True):
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    if seed and conn.execute("SELECT COUNT(*) AS n FROM pengguna").fetchone()["n"] == 0:
        _seed(conn)
    conn.close()


def _seed(conn):
    now = datetime.now().isoformat(timespec="seconds")
    cur = conn.cursor()
    users = [
        ("Pelanggan Demo", "pelanggan@keluhin.app", "pelanggan1234", "pelanggan"),
        ("Bu Sarah (Agen)", "agen@keluhin.app", "agen1234", "agen"),
    ]
    ids = {}
    for nama, email, pw, peran in users:
        cur.execute("INSERT INTO pengguna (nama,email,password_hash,peran) VALUES (?,?,?,?)",
                    (nama, email, generate_password_hash(pw, method="pbkdf2"), peran))
        ids[peran] = cur.lastrowid
    for k in ("Pengiriman", "Pembayaran", "Produk", "Lainnya"):
        cur.execute("INSERT INTO kategori (nama) VALUES (?)", (k,))
    # tiket contoh + rantai riwayat statusnya
    samples = [
        ("Paket belum sampai", "Sudah 5 hari paket belum tiba.", "Tinggi", 1, ["Baru"]),
        ("Refund belum masuk", "Dana refund belum diterima.", "Sedang", 2, ["Baru", "Diproses"]),
        ("Produk cacat", "Barang rusak saat diterima.", "Tinggi", 3, ["Baru", "Diproses", "Selesai"]),
    ]
    for judul, desk, prio, kat, rantai in samples:
        status_akhir = rantai[-1]
        cur.execute("""INSERT INTO tiket (judul,deskripsi,prioritas,status,kategori_id,pembuat_id,dibuat_pada)
                       VALUES (?,?,?,?,?,?,?)""",
                    (judul, desk, prio, status_akhir, kat, ids["pelanggan"], now))
        tid = cur.lastrowid
        lama = None
        for st in rantai:
            oleh = ids["pelanggan"] if st == "Baru" else ids["agen"]
            cur.execute("INSERT INTO log_status (tiket_id,status_lama,status_baru,diubah_oleh,waktu) VALUES (?,?,?,?,?)",
                        (tid, lama, st, oleh, now))
            lama = st
    conn.commit()


if __name__ == "__main__":
    init_db()
    print("Basis data siap:", DB_PATH)
