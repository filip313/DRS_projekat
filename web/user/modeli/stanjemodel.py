from marshmallow import Schema,fields,post_load
from enum import Enum

class Stanje():
    def __init__(self, valuta, stanje, user_id,id=None):
        self.valuta = valuta
        self.user_id = user_id
        self.stanje = stanje
        self.id=id

class StanjeSchema(Schema):
    id = fields.Number()
    valuta = fields.String()
    stanje = fields.Number()
    user_id = fields.Number()

    @post_load
    def make_stanje(self, data, **kwargs):
        return Stanje(**data)
