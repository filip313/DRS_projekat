from flask import Flask, sessions,session
from user.controler import user
from user.modeli import User


app=Flask(__name__)
app.register_blueprint(user,url_prefix="/user")
app.config['SECRET_KEY'] = 'asdfasdfasdfsadf'


@app.route("/")

def index():
    if "user" in session:
        user=session["user"]
        return str(user['verifikovan'])
    else:
        return "index"

if __name__=="__main__":
    app.run(debug=True,port=5001)