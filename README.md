# Keluhin — Sistem Tiket Keluhan Pelanggan

Aplikasi web helpdesk: keluhan pelanggan menjadi tiket yang punya status, riwayat,
dan alur penanganan yang tegas. Dibangun dengan Flask (Python) + SQLite.

## Empat Fitur
1. **Registrasi** — pembuatan akun (peran: pelanggan atau agen).
2. **Login** — masuk sesuai peran.
3. **Logout** — keluar dari sesi.
4. **Manajemen Tiket (fitur utama)** — pelanggan membuat tiket; agen mengubah
   status tiket mengikuti *state machine*; setiap perubahan tercatat di riwayat.

## Kebutuhan
- Python 3.10+
- Flask (lihat `requirements.txt`)

## Cara Menjalankan
1. (Opsional) `python3 -m venv venv` lalu aktifkan.
2. `pip install -r requirements.txt`
3. `python app.py`  (basis data `keluhin.db` + data awal dibuat otomatis)
4. Buka `http://127.0.0.1:5000`.
5. Akun demo:

| Peran | Email | Sandi |
|-------|-------|-------|
| Pelanggan | pelanggan@keluhin.app | pelanggan1234 |
| Agen Support | agen@keluhin.app | agen1234 |

## Menjalankan Test
`python -m unittest tests.test_keluhin -v`

## Struktur (arsitektur berlapis)
- `db.py` — koneksi SQLite, skema, data awal
- `repository.py` — kueri SQL (akses data)
- `services.py` — logika bisnis: AuthService, TiketService (state machine transisi status)
- `app.py` — controller/routing Flask
- `templates/`, `static/` — tampilan (Jinja2 + CSS responsive)

## State machine status tiket
`Baru → Diproses → Selesai → Ditutup`, dengan `Selesai → Diproses` untuk membuka ulang.
Transisi lain (mis. `Baru → Selesai`) ditolak lapisan Service.
