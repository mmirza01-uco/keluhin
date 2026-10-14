"""Keluhin — Sistem Tiket Keluhan. Controller (routing) + Flask app.

Empat fitur: registrasi, login, logout, dan Manajemen Tiket
(buat tiket + ubah status via state machine + riwayat status).
"""
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, abort)

from db import init_db
from services import (AuthService, TiketService, TRANSISI, STATUS_VALID,
                      PRIORITAS_VALID)

app = Flask(__name__)
app.secret_key = "keluhin-dev-key-ganti-di-produksi"
app.config.update(SESSION_COOKIE_HTTPONLY=True,
                  SESSION_COOKIE_SAMESITE="Lax",
                  MAX_CONTENT_LENGTH=1 * 1024 * 1024)


def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu.")
            return redirect(url_for("login"))
        return f(*a, **k)
    return w


def peran_required(*peran):
    def deco(f):
        @wraps(f)
        def w(*a, **k):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if session.get("peran") not in peran:
                flash("Anda tidak punya hak akses untuk tindakan ini.")
                return redirect(url_for("dashboard"))
            return f(*a, **k)
        return w
    return deco


# ---------- Fitur 1-3: Registrasi, Login, Logout ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            # Registrasi publik selalu sebagai pelanggan (peran dipaksa
            # di server).
            AuthService.register(request.form.get("nama", ""),
                                 request.form.get("email", ""),
                                 request.form.get("password", ""),
                                 "pelanggan")
            flash("Registrasi berhasil. Silakan login.")
            return redirect(url_for("login"))
        except ValueError as e:
            flash(str(e))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = AuthService.login(request.form.get("email", ""),
                              request.form.get("password", ""))
        if u:
            session.clear()
            session["user_id"] = u["id"]
            session["nama"] = u["nama"]
            session["peran"] = u["peran"]
            return redirect(url_for("dashboard"))
        flash("Email atau kata sandi salah.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- Fitur 4: Manajemen Tiket ----------
@app.route("/")
@login_required
def dashboard():
    status = request.args.get("status") or None
    # Pelanggan hanya melihat tiketnya sendiri; agen melihat semua tiket
    # (omni view).
    if session.get("peran") == "pelanggan":
        pembuat_id = session["user_id"]
    else:
        pembuat_id = None
    tiket = TiketService.daftar_tiket(status, pembuat_id)
    return render_template("dashboard.html", tiket=tiket, status=status,
                           semua_status=STATUS_VALID,
                           milik_sendiri=(pembuat_id is not None))


@app.route("/tiket/baru", methods=["GET", "POST"])
@login_required
def tiket_baru():
    kategori = TiketService.daftar_kategori()
    if request.method == "POST":
        try:
            tid = TiketService.buat_tiket(
                request.form.get("judul", ""),
                request.form.get("deskripsi", ""),
                request.form.get("prioritas", ""),
                request.form.get("kategori_id", type=int),
                session["user_id"])
            flash("Tiket berhasil dibuat.")
            return redirect(url_for("tiket_detail", tiket_id=tid))
        except ValueError as e:
            flash(str(e))
    return render_template("tiket_baru.html", kategori=kategori,
                           prioritas=PRIORITAS_VALID)


@app.route("/tiket/<int:tiket_id>")
@login_required
def tiket_detail(tiket_id):
    t = TiketService.ambil_tiket(tiket_id)
    if t is None:
        abort(404)
    # Pelanggan hanya boleh membuka tiket miliknya sendiri.
    if (session.get("peran") == "pelanggan"
            and t["pembuat_id"] != session["user_id"]):
        abort(403)
    return render_template("tiket_detail.html", t=t,
                           riwayat=TiketService.riwayat(tiket_id),
                           transisi=sorted(TRANSISI.get(t["status"], set())),
                           urutan_status=STATUS_VALID)


@app.route("/tiket/<int:tiket_id>/status", methods=["POST"])
@peran_required("agen")
def ubah_status(tiket_id):
    try:
        TiketService.ubah_status(tiket_id,
                                 request.form.get("status_baru", ""),
                                 session["user_id"])
        flash("Status tiket diperbarui.")
    except ValueError as e:
        flash(str(e))
    return redirect(url_for("tiket_detail", tiket_id=tiket_id))


@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", kode=403,
                           pesan="Anda tidak punya akses ke tiket ini."), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", kode=404,
                           pesan="Halaman atau tiket tidak ditemukan."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", kode=500,
                           pesan="Terjadi kesalahan pada server."), 500


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
