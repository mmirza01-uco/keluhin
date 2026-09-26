from domain.enus.status_tiket import StatusTiket


@dataclass
class RiwayatStatus:
    id: int | None
    tiket_id: int
    status_lama: StatusTiket | None
    status_baru: StatusTiket
    pengubah_id: int
    dibuat_pada: datetime | None = None


