from model import db, ma
from enum import Enum
from marshmallow import Schema, fields, post_load

class StanjeTransakcije(Enum):
    OBRADA = "OBRADA"
    OBRADJENO = "OBRADJENO"
    ODBIJENO = "ODBIJENO"


class Transakcija(db.Model):
    __tablename__ = 'transakcija'
    id = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.String(256), nullable=False, unique=True)
    iznos = db.Column(db.Float, nullable=False)
    valuta = db.Column(db.String(10), nullable=False)
    primalac_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    posiljalac_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    stanje = db.Column(db.Enum(StanjeTransakcije), nullable=False)

    def __init__(self, posiljalac_id, primalac_id, iznos, valuta, hash_id, stanje):
        self.iznos = iznos
        self.valuta = valuta
        self.hash_id = hash_id
        self.posiljalac_id = posiljalac_id
        self.primalac_id = primalac_id
        self.stanje = stanje


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


