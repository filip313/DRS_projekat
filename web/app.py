from flask import Flask, redirect, url_for 
from user.controler import user
from user.modeli import User
from transakcije.controler import transakcije


app=Flask(__name__)
app.register_blueprint(user,url_prefix="/user")
app.register_blueprint(transakcije,url_prefix="/transakcije")
app.config['SECRET_KEY'] = 'asdfasdfasdfsadf'


@app.route("/")
def index():
    return redirect(url_for('user.index'))

if __name__=="__main__":
    app.run(debug=True,port=5001)