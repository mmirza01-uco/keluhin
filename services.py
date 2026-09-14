"""Lapisan layanan (service): logika bisnis & validasi Keluhin."""
import re, sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import repository as repo

PERAN_VALID = ("pelanggan", "agen")
PRIORITAS_VALID = ("Rendah", "Sedang", "Tinggi")
STATUS_VALID = ("Baru", "Diproses", "Selesai", "Ditutup")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_SANDI = 6

# --- State machine: transisi status yang diizinkan ---
TRANSISI = {
    "Baru":     {"Diproses"},
    "Diproses": {"Selesai"},
    "Selesai":  {"Diproses", "Ditutup"},   # Selesai -> Diproses = buka ulang
    "Ditutup":  set(),                      # status akhir
}


class AuthService:
    @staticmethod
    def register(nama, email, password, peran="pelanggan"):
        nama = (nama or "").strip(); email = (email or "").strip().lower()
        if not (nama and email and password):
            raise ValueError("Nama, email, dan kata sandi wajib diisi.")
        if not EMAIL_RE.match(email):
            raise ValueError("Format email tidak valid.")
        if len(password) < MIN_SANDI:
            raise ValueError(f"Kata sandi minimal {MIN_SANDI} karakter.")
        if peran not in PERAN_VALID:
            raise ValueError("Peran tidak dikenal.")
        if repo.cari_pengguna_by_email(email):
            raise ValueError("Email sudah terdaftar.")
        try:
            return repo.tambah_pengguna(nama, email, generate_password_hash(password, method="pbkdf2"), peran)
        except sqlite3.IntegrityError:
            raise ValueError("Email sudah terdaftar.")

    @staticmethod
    def login(email, password):
        email = (email or "").strip().lower()
        u = repo.cari_pengguna_by_email(email)
        if u and check_password_hash(u["password_hash"], password or ""):
            return u
        return None


class TiketService:
    @staticmethod
    def daftar_kategori(): return repo.daftar_kategori()

    @staticmethod
    def daftar_tiket(status=None, pembuat_id=None): return repo.daftar_tiket(status, pembuat_id)

    @staticmethod
    def ambil_tiket(tiket_id): return repo.cari_tiket(tiket_id)

    @staticmethod
    def buat_tiket(judul, deskripsi, prioritas, kategori_id, pembuat_id):
        judul = (judul or "").strip(); deskripsi = (deskripsi or "").strip()
        if not (judul and deskripsi):
            raise ValueError("Judul dan deskripsi wajib diisi.")
        if prioritas not in PRIORITAS_VALID:
            raise ValueError("Prioritas tidak valid.")
        return repo.buat_tiket(judul, deskripsi, prioritas, kategori_id, pembuat_id)

    @staticmethod
    def transisi_diizinkan(status_lama, status_baru):
        return status_baru in TRANSISI.get(status_lama, set())

    @staticmethod
    def ubah_status(tiket_id, status_baru, oleh_id):
        """Ubah status hanya bila transisi sah (state machine)."""
        if status_baru not in STATUS_VALID:
            raise ValueError(f"Status tidak dikenal: {status_baru}")
        tiket = repo.cari_tiket(tiket_id)
        if tiket is None:
            raise ValueError("Tiket tidak ditemukan.")
        lama = tiket["status"]
        if status_baru == lama:
            raise ValueError("Status tidak berubah.")
        if not TiketService.transisi_diizinkan(lama, status_baru):
            raise ValueError(f"Transisi {lama} -> {status_baru} tidak diizinkan.")
        repo.ubah_status_dan_log(tiket_id, lama, status_baru, oleh_id)
        return status_baru

    @staticmethod
    def riwayat(tiket_id): return repo.riwayat_status(tiket_id)
