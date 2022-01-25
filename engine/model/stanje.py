from model import db, ma
from datetime import datetime
from marshmallow import Schema, fields, post_load

class Stanje(db.Model):
    __tablename__ = 'stanje'
    id = db.Column(db.Integer, primary_key=True)
    valuta = db.Column(db.String(10), nullable=False)
    stanje = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('useri.id'))


    def __init__(self, valuta, stanje, user_id, id):
        self.valuta = valuta
        self.user_id = user_id
        self.stanje = stanje
        self.id = id

class StanjeSchema(Schema):
    id = fields.Number()
    valuta = fields.String()
    stanje = fields.Number()
    user_id = fields.Number()

    @post_load
    def make_stanje(self, data, **kwargs):
        return Stanje(**data)