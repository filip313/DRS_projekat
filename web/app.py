from flask import Flask
from user.controler import user


app=Flask(__name__)
app.register_blueprint(user,url_prefix="/user")



@app.route("/")

def index():
    return "Uspesno!"

if __name__=="__main__":
    app.run(debug=True,port=5001)