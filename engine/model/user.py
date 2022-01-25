from model import db, ma
from model.stanje import Stanje, StanjeSchema
from model.transakcija import Transakcija, TransakcijaSchema
from datetime import datetime
from marshmallow import Schema, fields, post_load


class User(db.Model):
    __tablename__ = 'useri'
    id = db.Column(db.Integer, primary_key=True)
    ime = db.Column(db.String(32), nullable=False)
    prezime = db.Column(db.String(32), nullable=False)
    adresa = db.Column(db.String(100), nullable=False)
    grad = db.Column(db.String(32), nullable=False)
    drzava = db.Column(db.String(32), nullable=False)
    telefon = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    verifikovan = db.Column(db.Boolean(), nullable=False)
    stanja = db.relationship('Stanje', backref='pripada_user', lazy=True)
    primljene_transakcije = db.relationship('Transakcija', foreign_keys='Transakcija.primalac_id')
    poslate_transakcije = db.relationship('Transakcija', foreign_keys='Transakcija.posiljalac_id')

    def __init__(self, ime, prezime, adresa, grad, drzava, telefon, email, password, stanja, primljene_transakcije, poslate_transakcije, id=None, verifikovan=False):
        self.id = id
        self.ime = ime
        self.prezime = prezime
        self.adresa = adresa
        self.grad = grad
        self.drzava = drzava
        self.telefon = telefon
        self.email = email
        self.password = password
        self.verifikovan = verifikovan 
        self.stanja = stanja
        self.primljene_transakcije = primljene_transakcije
        self.poslate_transakcije = poslate_transakcije


class UserSchema(Schema):
    id = fields.Number()
    ime = fields.String()
    prezime = fields.String()
    adresa = fields.String()
    grad = fields.String()
    drzava = fields.String()
    telefon =fields.String() 
    email = fields.String()
    password =fields.String()
    verifikovan = fields.Boolean()
    stanja = fields.List(fields.Nested(StanjeSchema))
    primljene_transakcije = fields.List(fields.Nested(TransakcijaSchema))
    poslate_transakcije = fields.List(fields.Nested(TransakcijaSchema))

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)