from transakcije import *
from transakcije.forme import UplataForm
from urllib import request as req
from urllib.error import HTTPError
import json


@transakcije.route("/uplata",methods=["GET","POST"])
def uplata():
    form=UplataForm()
    if "user" in session:
        if request.method=='POST':
            if form.validate_on_submit():
                data={"ime":form.ime.data,"brojKartice":form.brojKartice.data,"datumIsteka":form.datumIsteka.data,"kod":form.kod.data,"email":session["user"]['email'],"stanje":form.stanje.data} 
                data = jsonify(data).get_data()
                zahtev = req.Request("http://localhost:5000/uplata")
                zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
                zahtev.add_header('Content-Length', len(data))
                try:
                    ret = req.urlopen(zahtev, data)
                    stanja=json.loads(ret.read())
                    session['user']['stanja']=stanja
                    flash(f"Uspesno ste uplatili iznos od {form.stanje.data}!",category='primary')
                    return redirect(url_for("user.stanja"))
                except HTTPError as e:
                    flash(e.read().decode(),category='danger')
                    return render_template("uplata.html",form=form)
            
            if form.errors != {}:
                for msg in form.errors.values():
                    flash(msg.pop(), category='danger')

                return render_template('uplata.html', form=form)
        else:
            return render_template("uplata.html",form=form)
    else:
        return redirect(url_for("user.login"))
