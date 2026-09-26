from domain.entities.tiket import Tiket


class TiketService:
    def __init__(self, tiket_repository, riwayat_repository):
        self.tiket_repository = tiket_repository
        self.riwayat_repository = riwayat_repository

    def buat_tiket(
            self,
            judul,
            deskripsi,
            prioritas,
            kategori_id,
            pembuat_id
           ):
        tiket = Tiket(
            id=None,
            judul=judul,
            deskripsi=deskripsi,
            prioritas=prioritas,
            kategori_id=kategori_id,
            pembuat_id=pembuat_id
        )

        return self.tiket_repository.simpan(tiket)

    def ubah_status(self, tiket_id, status_baru, agen):
        if not agen.adalah_agen():
            raise PermissionError("Hanya agen yang dapat mengubah status tiket.")

        tiket = self.tiket_repository.cari_by_id(tiket_id)

        if tiket is None:
            raise ValueError("Tiket tidak ditemukan")
        status_lama = tiket.status

        tiket.ubah_status(status_baru)
        self.ubah_status(status_baru)
        self.tiket_repository.update(tiket)
        self.riwayat_repository.simpan(
            tiket_id=tiket.id,
            status_lama=status_lama,
            status_baru=status_baru,
            pengubah_id=agen.id
        )