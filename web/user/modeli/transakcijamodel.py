from marshmallow import Schema,fields,post_load
from enum import Enum

class StanjeTransakcije(Enum):
    OBRADA = "OBRADA"
    OBRADJENO = "OBRADJENO"
    ODBIJENO = "ODBIJENO"


class Transakcija():
    def __init__(self, posiljalac_id, primalac_id, iznos, valuta, hash_id, stanje,id=None):
        self.iznos = iznos
        self.valuta = valuta
        self.hash_id = hash_id
        self.posiljalac_id = posiljalac_id
        self.primalac_id = primalac_id
        self.stanje = stanje
        self.id=id


class TransakcijaSchema(Schema):
    id = fields.Number()
    hash_id = fields.String()
    posiljalac_id = fields.Number()
    primalac_id = fields.Number()
    iznos = fields.Number()
    valuta = fields.String()
    stanje = fields.String()

    @post_load
    def make_transakciju(self, data, **kwargs):
        return Transakcija(**data)
