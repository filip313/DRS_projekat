from marshmallow import Schema, fields

class TransakcijaSchemaReq(Schema):
    posiljalac = fields.Email()
    primalac = fields.Email()
    valuta = fields.String()
    iznos = fields.Number()

class KupovinaSchema(Schema):
    email=fields.Email()
    valuta=fields.String()
    kolicina=fields.Number()
    vrednost=fields.Number()

class ZamenaSchema(Schema):
    email = fields.Email()
    valuta_pre = fields.String()
    valuta_posle = fields.String()
    kolicina = fields.Number()
    cena_pre = fields.Number()
    cena_posle = fields.Number()