from flask import Flask, jsonify, request
from model import db, ma, SQLAlchemy
from model.user import User, UserSchema
from model.stanje import Stanje, StanjeSchema
from model.transakcija import Transakcija, TransakcijaSchema, StanjeTransakcije
from model.seme import LoginSchema, UplataSchema, VerifikacijaSchema, TransakcijaSchemaReq
import datetime
from time import sleep
import threading
from multiprocessing import Process, Queue, Pipe
from sha3 import keccak_256
from random import random 
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:flask@localhost/baza'
app.config['SECRET_KEY'] = '123'
db.init_app(app)
ma.init_app(app)

@app.route('/')
def index():
    users = User.query.all()
    shema = UserSchema(many=True)
    dump = shema.dump(users)
    return jsonify(dump)

@app.route('/register', methods=['POST'])
def register():
    user = UserSchema().load(request.get_json())
    user.stanja.append(Stanje("USD", 0, None))
    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        return "User sa tim mejlom vec postoji", 406

    return 'User napravljen', 201

@app.route('/login', methods=['POST'])
def login():
    data =  LoginSchema().load(request.get_json())
    email = data["email"]
    password = data["password"]
    user = User.query.filter_by(email=email).first()

    if user:
        if user.password == password:
            ret_user = UserSchema().dump(user)
            ret_user["password"] = ""
            return jsonify(ret_user), 202
        else:
            return 'Losa sifra', 404
    
    return 'Nepostojeci korisnik', 404


@app.route('/change_user', methods=['POST'])
def change_user():
    user = UserSchema().load(request.get_json())
    db_user = User.query.filter_by(id=user.id , email=user.email).first()

    if db_user:
        try:
            db_user.ime = user.ime
            db_user.prezime = user.prezime
            db_user.grad = user.grad
            db_user.drzava = user.drzava
            db_user.telefon = user.telefon
            db_user.adresa = user.adresa
            if user.password != "":
                db_user.password = user.password
            db.session.commit()
            user.password = ""
            return jsonify(UserSchema().dump(user)), 200
        except Exception:
            return 'Nemoguce izmeniti korisnika', 406
    
    return 'Korisnik ne postoji', 404

def verifikacija_kartice(user,data):
    if user.ime==data["ime"]:
        if data["brojKartice"]== "4242424242424242":
            datum=data["datumIsteka"]
            datumisteka=datum.split('/')
            datumnovi=datetime.datetime.now()
            if int(datumisteka[0])>datumnovi.date().month and int("20" + datumisteka[1])>=datumnovi.date().year:
                if data["kod"]=='123':
                    return True
    return False
    
@app.route('/verifikacija', methods=['POST'])
def verifikacija():
    data = VerifikacijaSchema().load(request.get_json())
    email = data["email"]
    user = User.query.filter_by(email=email).first()
    if user:
        if verifikacija_kartice(user,data):
            user.verifikovan=True
            db.session.commit()
            return "Korisnik uspesno verifikovan"
        else:
            return "Kartica nije verifikovana,pokusajte opet!",403
            
    else:
        return "User ne postoji", 404

@app.route("/uplata",methods=['POST'])
def uplata():
    data=UplataSchema().load(request.get_json())
    email=data['email']
    user=User.query.filter_by(email=email).first()
    if user and user.verifikovan:
        if verifikacija_kartice(user,data):
            kraj=True
            for stanje in user.stanja:
                if stanje.valuta== "USD":
                    stanje.stanje+=data['stanje']
                    kraj =False
            if kraj:
                stanje=Stanje(valuta="USD",stanje=data['stanje'])
                user.stanja.append(stanje)
            db.session.commit()
            return jsonify(StanjeSchema(many=True).dump(user.stanja))
        else:
            return "Podaci o kartici nisu ispravni!",403
    else:
        return "Korisnik ne postoji ili nije verifikovan!",404

@app.route('/prenos', methods=['POST'])
def prenos():
    data = TransakcijaSchemaReq().load(request.get_json())
    if data["valuta"] == "RSD":
        return "Ne vazeca valuta!", 400
    if data['posiljalac'] == data['primalac']:
        return 'Nije moguce izvrsiti prenos samom sebi!', 400

    posiljalac = User.query.filter_by(email=data['posiljalac']).first()
    primalac = User.query.filter_by(email=data['primalac']).first()
    if posiljalac and posiljalac.verifikovan and primalac and primalac.verifikovan: 
        transakcija = Transakcija(posiljalac.id, primalac.id, data['iznos'],data['iznos'] * 0.05, data['valuta'], "", StanjeTransakcije.OBRADA)
        db.session.add(transakcija)
        db.session.commit()
        p = threading.Thread(target=obrada_transakcija, args=(posiljalac.email, primalac.email, transakcija.id))
        p.start()
        return "Transakcija uspesno zapoceta!", 201
    else:
        return 'Doslo je do greske proverite ispravnost email-a!', 400

def obrada_transakcija(pos_em, prim_em, t_id):
    with app.app_context():
        sleep(5)
        posiljalac = User.query.filter_by(email=pos_em).first()
        primalac = User.query.filter_by(email=prim_em).first()
        transakcija = Transakcija.query.filter_by(id=t_id).first()
        str_za_hash = posiljalac.email + primalac.email + str(transakcija.iznos) + str(random())
        k = keccak_256()
        k.update(bytes(str_za_hash, 'utf-8'))
        transakcija.hash_id = k.hexdigest()
        stanje = None
        for s in posiljalac.stanja:
            if s.valuta == transakcija.valuta:
                stanje = s
                break
            
        if stanje:

            if stanje.stanje >= (transakcija.iznos + transakcija.provizija):
                transakcija.stanje = StanjeTransakcije.OBRADJENO
                stanje.stanje -= (transakcija.iznos + transakcija.provizija)
                kraj = True 
                for s in primalac.stanja:
                    if s.valuta == transakcija.valuta:
                        s.stanje += transakcija.iznos
                        kraj = False
                
                if kraj:
                    primalac.stanja.append(Stanje(transakcija.valuta, transakcija.iznos, primalac.id))
            else:
                transakcija.stanje = StanjeTransakcije.ODBIJENO
        else:
            transakcija.stanje = StanjeTransakcije.ODBIJENO 

        db.session.commit()


@app.route('/transakcije/<user_id>', methods=['GET'])
def get_sve_transakcije(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        user.password = ""
        return jsonify(UserSchema().dump(user))
    else:
        return "Trazeni korisnik ne postoji", 400

## privremene metode
@app.route('/dodaj_usera', methods=['POST'])
def dodaj_usera():
    user = UserSchema().load(request.get_json())
    db.session.add(user)
    db.session.commit()
    u = User.query.filter_by(id=1).first()
    return u.ime

@app.route('/dodaj_transakciju', methods=['POST'])
def dodaj_transakciju():
    transakcija = TransakcijaSchema().load(request.get_json())
    db.session.add(transakcija)
    db.session.commit()
    return 'Ok', 204

@app.route('/get_transakcije_cnt/<user_id>')
def get_transakcije_cnt(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.poslate_transakcije[0].valuta

@app.route('/drop_table')
def drop_table():
    db.drop_all()
    return 'dropovao sve'

@app.route('/create_all')
def create_all():
    db.create_all()
    return 'napravio nove tabele'

@app.route('/asdf')
def get_transakcije():
    tr = Transakcija.query.all()
    return tr[1].hash_id
if __name__ == "__main__":
    app.run(debug=True)