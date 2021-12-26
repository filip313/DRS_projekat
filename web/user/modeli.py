from marshmallow import Schema,fields,post_load

class User():
    def __init__(self,ime,prezime,adresa,grad,drzava,telefon,email,password,verifikovan=False,stanja=[],primljene_transakcije=[],poslate_transakcije=[],id=None):
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
    stanja=fields.List()
    primljene_transakcije=fields.List()
    poslate_transakcije=fields.List()

    @post_load
    def make_user(self,data,**kwargs):
        return User(**data)

    