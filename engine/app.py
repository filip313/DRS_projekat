from flask import Flask, jsonify, request

from model import db, ma
from model.user import User, UserSchema

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:flask@0.0.0.0/baza'
db.init_app(app)
ma.init_app(app)

@app.route('/')
def index():
    users = User.query.all()
    shema = UserSchema(many=True)
    dump = shema.dump(users)
    return jsonify(dump)

if __name__ == "__main__":
    app.run(debug=True)