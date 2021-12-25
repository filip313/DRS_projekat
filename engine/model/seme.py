from marshmallow import Schema, fields

class LoginSchema(Schema):
    email = fields.Email()
    password = fields.String()

class UbacivanjeSredstavaSchema(Schema):
    email = fields.Email()
    id = fields.Number()
    vrednost = fields.Number()