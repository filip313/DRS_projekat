from flask import Flask, jsonify, request

from model import db, ma
from model.user import User, UserSchema
from model.stanje import Stanje, StanjeSchema
from model.transakcija import Transakcija, TransakcijaSchema

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
    return user.stanja[0].valuta

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