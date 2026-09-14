"""Unit & integration test Keluhin (unittest + Flask test client).

Cakupan: registrasi, login, logout, dan Manajemen Tiket
(buat tiket + state machine ubah status + riwayat + kontrol peran).
"""
import os, sys, tempfile, unittest, importlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db


class KeluhinTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False); self.tmp.close()
        db.DB_PATH = self.tmp.name
        db.init_db(seed=True)
        import app as app_module
        importlib.reload(app_module)
        app_module.app.config["TESTING"] = True
        self.app_module = app_module
        self.client = app_module.app.test_client()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def login(self, email="agen@keluhin.app", pw="agen1234"):
        return self.client.post("/login", data={"email": email, "password": pw}, follow_redirects=True)

    # TC-01
    def test_seed(self):
        from services import TiketService
        self.assertEqual(len(TiketService.daftar_kategori()), 4)
        self.assertEqual(len(TiketService.daftar_tiket()), 3)

    # TC-02 / TC-03
    def test_login_benar(self):
        self.assertIn("Daftar Tiket", self.login().get_data(as_text=True))
    def test_login_salah(self):
        self.assertIn("Email atau kata sandi salah", self.login(pw="x").get_data(as_text=True))

    # TC-04 logout
    def test_logout(self):
        self.login()
        r = self.client.get("/logout", follow_redirects=True)
        self.assertIn("Masuk Keluhin", r.get_data(as_text=True))

    # TC-05 / TC-06 / TC-07 registrasi
    def test_registrasi_email_ganda(self):
        from services import AuthService
        with self.assertRaises(ValueError): AuthService.register("X", "agen@keluhin.app", "rahasia123")
    def test_registrasi_peran_tak_dikenal(self):
        from services import AuthService
        with self.assertRaises(ValueError): AuthService.register("X", "baru@k.app", "rahasia123", "hacker")
    def test_registrasi_email_tak_valid(self):
        from services import AuthService
        with self.assertRaises(ValueError): AuthService.register("X", "bukan-email", "rahasia123")

    # TC-08 akses tanpa login
    def test_akses_tanpa_login(self):
        r = self.client.get("/tiket/baru", follow_redirects=True)
        self.assertIn("Masuk Keluhin", r.get_data(as_text=True))

    # TC-09 buat tiket
    def test_buat_tiket_status_baru(self):
        from services import TiketService
        tid = TiketService.buat_tiket("Tes", "isi keluhan", "Sedang", 1, 1)
        t = TiketService.ambil_tiket(tid)
        self.assertEqual(t["status"], "Baru")
        self.assertEqual(len(TiketService.riwayat(tid)), 1)  # log awal tercatat

    # TC-10 transisi sah
    def test_transisi_sah(self):
        from services import TiketService
        tid = TiketService.buat_tiket("T", "x", "Rendah", 1, 1)
        TiketService.ubah_status(tid, "Diproses", 2)
        self.assertEqual(TiketService.ambil_tiket(tid)["status"], "Diproses")

    # TC-11 transisi ilegal ditolak
    def test_transisi_ilegal(self):
        from services import TiketService
        tid = TiketService.buat_tiket("T", "x", "Rendah", 1, 1)
        with self.assertRaises(ValueError):
            TiketService.ubah_status(tid, "Selesai", 2)   # Baru -> Selesai tidak sah

    # TC-12 reopen: Diproses->Selesai->Diproses
    def test_reopen(self):
        from services import TiketService
        tid = TiketService.buat_tiket("T", "x", "Rendah", 1, 1)
        TiketService.ubah_status(tid, "Diproses", 2)
        TiketService.ubah_status(tid, "Selesai", 2)
        TiketService.ubah_status(tid, "Diproses", 2)  # buka ulang, sah
        self.assertEqual(TiketService.ambil_tiket(tid)["status"], "Diproses")
        self.assertEqual(len(TiketService.riwayat(tid)), 4)  # awal + 3 transisi

    # TC-13 status sama ditolak
    def test_status_sama_ditolak(self):
        from services import TiketService
        tid = TiketService.buat_tiket("T", "x", "Rendah", 1, 1)
        with self.assertRaises(ValueError):
            TiketService.ubah_status(tid, "Baru", 2)

    # TC-14 role: pelanggan tak boleh ubah status
    def test_pelanggan_tak_boleh_ubah_status(self):
        self.login("pelanggan@keluhin.app", "pelanggan1234")
        from services import TiketService
        r = self.client.post("/tiket/1/status", data={"status_baru": "Diproses"}, follow_redirects=True)
        self.assertIn("tidak punya hak akses", r.get_data(as_text=True))
        self.assertEqual(TiketService.ambil_tiket(1)["status"], "Baru")  # tak berubah

    # TC-15 404
    def test_tiket_tak_ada_404(self):
        self.login()
        self.assertEqual(self.client.get("/tiket/9999").status_code, 404)

    # TC-16 pelanggan hanya lihat tiket sendiri (service)
    def test_daftar_tiket_filter_pembuat(self):
        from services import TiketService, AuthService
        uid = AuthService.register("Baru", "baru@k.app", "rahasia123", "pelanggan")
        self.assertEqual(len(TiketService.daftar_tiket(pembuat_id=uid)), 0)
        self.assertEqual(len(TiketService.daftar_tiket(pembuat_id=1)), 3)

    # TC-17 dashboard pelanggan baru tak menampilkan tiket pelanggan lain
    def test_dashboard_pelanggan_tak_lihat_tiket_lain(self):
        from services import AuthService
        AuthService.register("Baru", "baru@k.app", "rahasia123", "pelanggan")
        self.login("baru@k.app", "rahasia123")
        html = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("Paket belum sampai", html)

    # TC-18 pelanggan tak boleh buka detail tiket milik orang lain (via URL)
    def test_pelanggan_tak_boleh_buka_tiket_lain(self):
        from services import AuthService
        AuthService.register("Baru", "baru@k.app", "rahasia123", "pelanggan")
        self.login("baru@k.app", "rahasia123")
        self.assertEqual(self.client.get("/tiket/1").status_code, 403)

    # TC-19 agen melihat semua tiket (omni view)
    def test_agen_lihat_semua_tiket(self):
        self.login()  # agen
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Paket belum sampai", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
