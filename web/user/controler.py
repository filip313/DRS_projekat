from user import *
from user.forme import RegisterForm
from user.modeli import UserSchema,User
from urllib import request as req, parse 

@user.route("/register",methods=["GET","POST"])

def register():
    form=RegisterForm()
    if request.method=='POST':
        if form.validate_on_submit():
            user=User(form.ime.data,form.prezime.data,form.adresa.data,form.grad.data,form.drzava.data,form.telefon.data,form.email.data,form.password1.data)
            data=UserSchema().dump(user)
            data.pop('id')
            data = jsonify(data).get_data()
            zahtev = req.Request("http://localhost:5000/register")
            zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
            zahtev.add_header('Content-Length', len(data))
            ret = req.urlopen(zahtev, data)
            return ret.read() 
        
        if form.errors != {}:
            for msg in form.errors.values():
                flash(msg.pop(), category='danger')

            return render_template('register.html', form=form)
    else :
        return render_template('register.html', form=form)
