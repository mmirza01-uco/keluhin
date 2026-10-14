"""Lapisan repository: akses data (kueri SQL) ke basis data Keluhin."""
from datetime import datetime

from db import get_conn

SQL_LOG_STATUS = ("INSERT INTO log_status "
                  "(tiket_id, status_lama, status_baru, diubah_oleh, waktu) "
                  "VALUES (?, ?, ?, ?, ?)")


def cari_pengguna_by_email(email):
    conn = get_conn()
    row = conn.execute("SELECT * FROM pengguna WHERE email = ?",
                       (email,)).fetchone()
    conn.close()
    return row


def tambah_pengguna(nama, email, password_hash, peran):
    conn = get_conn()
    cur = conn.execute("INSERT INTO pengguna (nama, email, password_hash, "
                       "peran) VALUES (?, ?, ?, ?)",
                       (nama, email, password_hash, peran))
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    return uid


def daftar_kategori():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM kategori ORDER BY nama").fetchall()
    conn.close()
    return rows


def buat_tiket(judul, deskripsi, prioritas, kategori_id, pembuat_id):
    conn = get_conn()
    now = datetime.now().isoformat(timespec="seconds")
    try:
        cur = conn.execute(
            """INSERT INTO tiket (judul, deskripsi, prioritas, status,
                                  kategori_id, pembuat_id, dibuat_pada)
               VALUES (?, ?, ?, 'Baru', ?, ?, ?)""",
            (judul, deskripsi, prioritas, kategori_id, pembuat_id, now))
        tid = cur.lastrowid
        conn.execute(SQL_LOG_STATUS, (tid, None, "Baru", pembuat_id, now))
        conn.commit()
        return tid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def cari_tiket(tiket_id):
    conn = get_conn()
    row = conn.execute(
        """SELECT t.*, k.nama AS kategori_nama, p.nama AS pembuat_nama
           FROM tiket t
           LEFT JOIN kategori k ON k.id = t.kategori_id
           LEFT JOIN pengguna p ON p.id = t.pembuat_id
           WHERE t.id = ?""", (tiket_id,)).fetchone()
    conn.close()
    return row


def daftar_tiket(status=None, pembuat_id=None):
    conn = get_conn()
    q = """SELECT t.*, k.nama AS kategori_nama
           FROM tiket t LEFT JOIN kategori k ON k.id = t.kategori_id"""
    kondisi = []
    params = []
    if status:
        kondisi.append("t.status = ?")
        params.append(status)
    if pembuat_id is not None:
        kondisi.append("t.pembuat_id = ?")
        params.append(pembuat_id)
    if kondisi:
        q += " WHERE " + " AND ".join(kondisi)
    q += " ORDER BY t.dibuat_pada DESC, t.id DESC"
    rows = conn.execute(q, tuple(params)).fetchall()
    conn.close()
    return rows


def ubah_status_dan_log(tiket_id, status_lama, status_baru, oleh_id):
    """Ubah status tiket + catat riwayat dalam satu transaksi."""
    conn = get_conn()
    now = datetime.now().isoformat(timespec="seconds")
    try:
        conn.execute("UPDATE tiket SET status = ? WHERE id = ?",
                     (status_baru, tiket_id))
        conn.execute(SQL_LOG_STATUS,
                     (tiket_id, status_lama, status_baru, oleh_id, now))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def riwayat_status(tiket_id):
    conn = get_conn()
    rows = conn.execute(
        """SELECT l.*, p.nama AS oleh_nama FROM log_status l
           LEFT JOIN pengguna p ON p.id = l.diubah_oleh
           WHERE l.tiket_id = ? ORDER BY l.waktu, l.id""",
        (tiket_id,)).fetchall()
    conn.close()
    return rows
