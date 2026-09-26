from enum import Enum


class StatusTiket(Enum):
    BARU = "baru"
    DIPROSES = "diproses"
    SELESAI = "selesai"
    DITUTUP = "ditutup"

    TRANSITIONS = {
        "baru": {"diproses"},
        "diproses": {"selesai"},
        "selesai": {"ditutup", "diproses"},
        "ditutup": set(),
    }


    @classmethod
    def from_value(cls, value: str):
        for status in cls:
            if status.value == value:
                return status

        raise ValueError(f"Status tiket tidak valid: {value}")

    def dapat_berubah_ke(self, status_baru):
        if not isinstance(status_baru, StatusTiket):
            raise TypeError("status_baru harus berupa StatusTiket")

        return status_baru.value in self.TRANSITIONS(self.value)

    @classmethod
    def values(cls):
        return [status.value for status in cls]

    def status_selanjutnya(self):
        return sorted(self.TRANSITIONS[self.value])