from flask import Flask, redirect, url_for 
from user.controler import user
from transakcije.controler import transakcije
import os


app=Flask(__name__)
app.register_blueprint(user,url_prefix="/user")
app.register_blueprint(transakcije,url_prefix="/transakcije")
app.config['SECRET_KEY'] = 'asdfasdfasdfsadf'


@app.route("/")
def index():
    return redirect(url_for('user.index'))

if __name__=="__main__":
    port=int(os.environ.get('PORT',5001))
    app.run(debug=False,port=port,host='0.0.0.0')