from marshmallow import Schema, fields

class LoginSchema(Schema):
    email = fields.Email()
    password = fields.String()

class VerifikacijaSchema(Schema):
    email = fields.Email()
    brojKartice=fields.String()
    ime=fields.String()
    datumIsteka=fields.String()
    kod = fields.String()

class UplataSchema(VerifikacijaSchema):
    stanje=fields.Number()