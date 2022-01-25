from model import db, ma
from enum import Enum
from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField

class StanjeTransakcije(Enum):
    OBRADA = "OBRADA"
    OBRADJENO = "OBRADJENO"
    ODBIJENO = "ODBIJENO"


class Transakcija(db.Model):
    __tablename__ = 'transakcija'
    id = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.String(256), nullable=False)
    iznos = db.Column(db.Float, nullable=False)
    provizija = db.Column(db.Float, nullable=False)
    valuta = db.Column(db.String(10), nullable=False)
    primalac_id = db.Column(db.Integer, db.ForeignKey('useri.id'))
    posiljalac_id = db.Column(db.Integer, db.ForeignKey('useri.id'))
    stanje = db.Column(db.Enum(StanjeTransakcije), nullable=False)

    def __init__(self, posiljalac_id, primalac_id, iznos, provizija, valuta, hash_id, stanje, id):
        self.iznos = iznos
        self.provizija = provizija
        self.valuta = valuta
        self.hash_id = hash_id
        self.posiljalac_id = posiljalac_id
        self.primalac_id = primalac_id
        self.stanje = stanje
        self.id = id


class TransakcijaSchema(Schema):
    id = fields.Number()
    hash_id = fields.String()
    iznos = fields.Number()
    provizija = fields.Number()
    valuta = fields.String()
    primalac_id = fields.Number()
    posiljalac_id = fields.Number()
    stanje = EnumField(StanjeTransakcije)

    @post_load
    def make_transakcija(self, data, **kwargs):
        return Transakcija(**data)


