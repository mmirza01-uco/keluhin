from domain.entities.tiket import Tiket


class TiketController:
    def __init__(self, tiket_service):
        self.tiket_service = tiket_service


    def buat(self):
        if request.method == "POST":
            try:
                tiket = self.tiket_service.buat_tiket(
                    judul=request.form.get("judul",""),
                    deskripsi=request.form.get("desckripsi",""),
                    prioritas=request.form.get("priritas",""),
                    kategori_id=request.form.get("kategori_id",type=int),
                    pembuat_id=session["user_id"]
                )
                flash("Tiket berhasil dibuat")
                return redirect(
                    url_for(
                        "tiket_detail", tiket_id=tiket.id
                    )
                )

            except ValueError as e:
                flash(str(e))

        kategori = self.tiket_service.daftar_kategori()


        return render_template(
            "tiket.baru.html",
            kategori=kategori
        )