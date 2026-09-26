

class Prioritas(Enum):
    RENDAH = "rendah"
    SEDANG = "sedang",
    TINGGI = "tinggi",
    KRITIS = "kritis"

    @classmethod
    def from_value(cls, value:str):
        for prioritas in cls:
            if prioritas.value == value:
                return prioritas

        raise ValueError(f"Prioritas tidak valid: {value}")

    @classmethod
    def values(cls):
        return [prioritas.value for prioritas in cls]
