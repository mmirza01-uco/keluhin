

class Perna(Enum):
    PELANGGAN = "pelanggan"
    AGEN = "agen"

    @classmethod
    def from_value(cls, value: str):
        for peran in cls:
            if peran.value == value:
                return peran

        raise ValueError(f"Peran tidak valid: {value}")
