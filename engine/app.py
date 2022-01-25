from flask import Flask, jsonify, request
from model import db, ma, pc, cc 
from model.user import User, UserSchema
from model.stanje import Stanje, StanjeSchema
from model.transakcija import Transakcija, TransakcijaSchema, StanjeTransakcije
from model.seme.transakcijasema import *
from model.seme.usersema import *
import datetime
from time import sleep
import threading
from multiprocessing import Process
from sha3 import keccak_256
from random import random 
import os
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ndissgnadnzmkv:30d37d5b811610d66d650e0caec30a9e0854eb6d5a70865e754fa27b3eeef95b@ec2-34-194-171-47.compute-1.amazonaws.com:5432/d6dlguqq0jhh8q'
app.config['SECRET_KEY'] = '123'
db.init_app(app)
ma.init_app(app)

lock = threading.Lock()

@app.route('/')
def index():
    users = User.query.all()
    shema = UserSchema(many=True)
    dump = shema.dump(users)
    return jsonify(dump)

@app.route('/register', methods=['POST'])
def register():
    user = UserSchema().load(request.get_json())
    user.stanja.append(Stanje("USD", 0, None, None))
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
    if data["valuta"] == "USD":
        return "Ne vazeca valuta!", 400
    if data['posiljalac'] == data['primalac']:
        return 'Nije moguce izvrsiti prenos samom sebi!', 400

    posiljalac = User.query.filter_by(email=data['posiljalac']).first()
    primalac = User.query.filter_by(email=data['primalac']).first()
    if posiljalac and posiljalac.verifikovan and primalac and primalac.verifikovan: 
        transakcija = Transakcija(posiljalac.id, primalac.id, data['iznos'],data['iznos'] * 0.05, data['valuta'], "", StanjeTransakcije.OBRADA, None)
        db.session.add(transakcija)
        db.session.commit()
        p = threading.Thread(target=obrada_transakcija, args=(posiljalac.email, primalac.email, transakcija.id))
        p.start()
        return "Transakcija uspesno zapoceta!", 201
    else:
        return 'Doslo je do greske proverite ispravnost email-a!', 400

def obrada_transakcija(pos_em, prim_em, t_id):
    with app.app_context():
        lock.acquire()
        posiljalac = User.query.filter_by(email=pos_em).first()
        primalac = User.query.filter_by(email=prim_em).first()
        transakcija = Transakcija.query.filter_by(id=t_id).first()
        pc.send(UserSchema().dump(posiljalac))
        pc.send(UserSchema().dump(primalac))
        pc.send(TransakcijaSchema().dump(transakcija)) 
        pos_stanje= StanjeSchema().load(pc.recv())
        prim_stanje = pc.recv()
        t= TransakcijaSchema().load(pc.recv())
        posiljalac = User.query.filter_by(email=pos_em).first()
        primalac = User.query.filter_by(email=prim_em).first()
        transakcija.hash_id = t.hash_id
        transakcija.stanje = t.stanje
        if pos_stanje.id != -1:
            kraj = True
            for s in posiljalac.stanja:
                if s.valuta == pos_stanje.valuta:
                    s.stanje = pos_stanje.stanje
                    kraj = False
            if kraj:
                posiljalac.stanja.append(pos_stanje)
        if 'id' not in prim_stanje:
            kraj = True
            for s in primalac.stanja:
                if s.valuta == prim_stanje['valuta']:
                    s.stanje = prim_stanje['stanje']
                    kraj = False
            if kraj:
                primalac.stanja.append(Stanje(prim_stanje['valuta'], prim_stanje['stanje'], primalac.id, None))
        db.session.commit()
        lock.release()


@app.route('/transakcije/<user_id>', methods=['GET'])
def get_sve_transakcije(user_id):
    user_id = float(user_id)
    user = User.query.filter_by(id=user_id).first()
    if user:
        user.password = ""
        user=UserSchema().dump(user)
        t1=threading.Thread(target=pribavi_email,args=(user["poslate_transakcije"],True))
        t2=threading.Thread(target=pribavi_email,args=(user["primljene_transakcije"],False))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
       
        return jsonify(user)
        
    else:
        return "Trazeni korisnik ne postoji", 400

def pribavi_email(lista,poslate):
    with app.app_context():
        for t in lista:
            if poslate:
                user=User.query.filter_by(id=t['primalac_id']).first()
                t["primalac_id"]=user.email
            else:
                user=User.query.filter_by(id=t['posiljalac_id']).first()
                t["posiljalac_id"]=user.email
        return lista

@app.route('/kupovina',methods=['POST'])
def kupovina():
    data = KupovinaSchema().load(request.get_json())
    user=User.query.filter_by(email=data['email']).first()
    if user and user.verifikovan:
        cena=data['kolicina']*data['vrednost']
        stanje_usd=None
        for s in user.stanja:
            if s.valuta=="USD":
                stanje_usd=s
                break
        if stanje_usd and stanje_usd.stanje >= cena:
            stanje_usd.stanje-=cena
            kraj=True
            for s in user.stanja:
                if s.valuta==data['valuta']:
                    s.stanje+=data['kolicina']
                    kraj=False
                    break
            if kraj:
                user.stanja.append(Stanje(data['valuta'],data['kolicina'],user.id,None))
            
            db.session.commit()
            return jsonify(UserSchema().dump(user))
        else:
            return "Nema dovoljno sredstava!",402
    else:
        return "Korisnik ne postoji ili nije verifikovan",400


@app.route('/zamena', methods=['POST'])
def zamena():
    data = ZamenaSchema().dump(request.get_json()) 
    user = User.query.filter_by(email=data['email']).first()
   
    if user and user.verifikovan:
        stanje_pre = None
        stanje_posle = None
        for s in user.stanja:
            if s.valuta == data['valuta_pre']:
                stanje_pre = s
            
            if s.valuta == data['valuta_posle']:
                stanje_posle = s
        print(data['kolicina'], flush=True)
        print(stanje_pre.stanje, flush=True)
        if stanje_pre:
            if stanje_pre.stanje >= data['kolicina']:
                za_zamenu = data['kolicina'] * data['cena_pre']
                zamenjeno = za_zamenu / data['cena_posle']
                stanje_pre.stanje -= data['kolicina']

                if stanje_posle:
                    stanje_posle.stanje += zamenjeno
                else:
                    user.stanja.append(Stanje(data['valuta_posle'], zamenjeno, user.id, None))

                db.session.commit()
                return jsonify(UserSchema().dump(user))
            else:
                return 'Nemate dovoljno sredstava za zamenu!', 400
        else:
            return 'Nemate zeljeno stanje za zamenu!', 400
    else:
        return "Korisnik ne postoji ili nije verifikovan!", 403
            

            
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

def proces_transakcija(cc):
    while True:
        posiljalac = cc.recv()
        primalac = cc.recv()
        transakcija = cc.recv()
        sleep(300)
        str_za_hash = posiljalac['email'] + primalac['email'] + str(transakcija['iznos']) + str(random())
        k = keccak_256()
        k.update(bytes(str_za_hash, 'utf-8'))
        transakcija['hash_id'] = k.hexdigest()
        stanje = None
        for s in posiljalac['stanja']:
            if s['valuta'] == transakcija['valuta']:
                stanje = s
                break
            
        if stanje:

            if stanje['stanje'] >= (transakcija['iznos'] + transakcija['provizija']):
                transakcija['stanje'] = "OBRADJENO" 
                stanje['stanje'] -= (transakcija['iznos'] + transakcija['provizija'])
                cc.send(stanje)
                kraj = True 
                for s in primalac['stanja']:
                    if s['valuta'] == transakcija['valuta']:
                        s['stanje'] += transakcija['iznos']
                        s = {'stanje':s['stanje'], 'user_id':s['user_id'], 'valuta':s['valuta']}
                        cc.send(s)
                        kraj = False
                
                if kraj:
                    novo_stanje = {'stanje':transakcija['iznos'], 'user_id': primalac['id'], 'valuta':transakcija['valuta']}
                    cc.send(novo_stanje)
                    primalac['stanja'].append(novo_stanje)
            else:
                transakcija['stanje'] = "ODBIJENO"
                novo_stanje = Stanje( stanje=transakcija['iznos'], user_id=primalac['id'], valuta=transakcija['valuta'], id=-1)
                novo_stanje = {'stanje':transakcija['iznos'], 'user_id': primalac['id'], 'valuta':transakcija['valuta'], 'id':-1}
                cc.send(novo_stanje)
                cc.send(novo_stanje)
        else:
            transakcija['stanje'] = "ODBIJENO"
            novo_stanje = Stanje( stanje=transakcija['iznos'], user_id=primalac['id'], valuta=transakcija['valuta'], id=-1)
            cc.send(StanjeSchema().dump(novo_stanje))
            cc.send(StanjeSchema().dump(novo_stanje))

        cc.send(transakcija)
    

if __name__ == "__main__":
    p = Process(target=proces_transakcija, args=(cc,))
    p.start()
    port=int(os.environ.get('PORT',5000))
    app.run(debug=False,port=port,host='0.0.0.0')