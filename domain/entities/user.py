from dataclassses import dataclass

from domain.enus import peran


@dataclass
class User:
    id: int
    nama: str
    email: str
    peran: str

    def adalah_pelanggan(self):
        return self.peran == peran.PELANGGAN

    def adalah_agen(self):
        return self.peran == peran.AGEN