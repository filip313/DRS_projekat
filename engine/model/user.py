from model import db, ma
from datetime import datetime
from marshmallow import Schema, fields

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    ime = db.Column(db.String(32), nullable=False)
    prezime = db.Column(db.String(32), nullable=False)
    adresa = db.Column(db.String(100), nullable=False)
    grad = db.Column(db.String(32), nullable=False)
    drzava = db.Column(db.String(32), nullable=False)
    telefon = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, ime, prezime, adresa, grad, drzava, telefon, email, password):
        self.ime = ime
        self.prezime = prezime
        self.adresa = adresa
        self.grad = grad
        self.drzava = drzava
        self.telefon = telefon
        self.email = email
        self.password = password



class UserSchema(Schema):
    user_id = fields.Number()
    ime = fields.String()
    prezime = fields.String()
    adresa = fields.String()
    grad = fields.String()
    drzava = fields.String()
    telefon =fields.String() 
    email = fields.String()
    password =fields.String()
