from ataclasses import dataclass
from domain.enus.status_tiket import StatusTiket

@dataclass
class Tiket:
    id: int | None
    judul: str
    deskripsi: str
    prioritas: str
    kategori_id: int
    pembuatan_id: int
    status: StatusTiket = StatusTiket.BARU

    def ubah_status(self, status_baru: StatusTiket):
        if not isinstance(status_baru, StatusTiket):
            raise TypeError("status_baru harus berupa StatusTiket")

        if not self.status.dapat_berubah_ke(status_baru):
            raise ValueError(f"Tidak dapat mengubah status "
                             f"{self.status.value} -> {status_baru.value}")
        self.status = status_baru

    def adalah_milik(self, user_id: int):
        return self.pembuatan_id == user_id