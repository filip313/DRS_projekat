from re import I, S
from flask import Flask, jsonify, request
from model import db, ma
from model.user import User, UserSchema
from model.stanje import Stanje, StanjeSchema
from model.transakcija import Transakcija, TransakcijaSchema
from model.seme import LoginSchema, UbacivanjeSredstavaSchema 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:flask@0.0.0.0/baza'
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


@app.route('/change_user', methods=['PUT'])
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
            db_user.password = user.password
            db.session.commit()
            return 'User izmenjen', 200
        except Exception:
            return 'Nemoguce izmeniti korisnika', 406
    
    return 'Korisnik ne postoji', 404
    
@app.route('/uplata_sredstava', methods=['PUT'])
def uplata_sredstava():
    data = UbacivanjeSredstavaSchema().load(request.get_json())
    email = data["email"]
    id = data["id"]
    vrednost = data["vrednost"]
    user = User.query.filter_by(id=id, email=email).first()
    if user:
        if user.verifikovan:
            stanje = None
            for s in user.stanja:
                if s.valuta == "USD":
                    stanje = s
                    break

            if stanje:
                try:
                    stanje.stanje+= vrednost
                    db.session.commit()
                except Exception:
                    return "Doslo je do greske", 500

                return jsonify(StanjeSchema().dump(stanje)), 200
            else:
                return "Izmena stanja neuspela", 404
        else:
            return "User nije verifikovan", 401
    else:

        return "User ne postoji", 404


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

if __name__ == "__main__":
    app.run(debug=True)