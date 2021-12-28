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

class User():
    def __init__(self,ime,prezime,adresa,grad,drzava,telefon,email,password,verifikovan=False,stanja=[],primljene_transakcije=[],poslate_transakcije=[],id=-1):
        self.id=id
        self.ime=ime
        self.prezime=prezime
        self.adresa=adresa
        self.grad=grad
        self.drzava=drzava
        self.telefon=telefon
        self.email=email
        self.password=password
        self.verifikovan=verifikovan
        self.stanja=stanja
        self.primljene_transakcije=primljene_transakcije
        self.poslate_transakcije=poslate_transakcije
    
class UserSchema(Schema):
    id=fields.Number()
    ime=fields.String()
    prezime=fields.String()
    adresa=fields.String()
    grad=fields.String()
    drzava=fields.String()
    telefon=fields.String()
    email=fields.Email()
    password=fields.String()
    verifikovan=fields.Boolean()
    stanja=fields.List(fields.Nested(StanjeSchema))
    primljene_transakcije=fields.List(fields.Nested(TransakcijaSchema))
    poslate_transakcije=fields.List(fields.Nested(TransakcijaSchema))

    @post_load
    def make_user(self,data,**kwargs):
        return User(**data)


class LoginSchema(Schema):
    email = fields.Email()
    password = fields.String()




    