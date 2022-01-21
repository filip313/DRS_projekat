from transakcije import *
from transakcije.forme import UplataForm, PrenosForm,PretragaForm
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


@transakcije.route('/prenos', methods=['GET', 'POST'])
def prenos():
    if 'user' in session:
        form = PrenosForm()
        izbori = []
        for s in session['user']['stanja']:
            izbori.append((s['valuta'],s['valuta']))
        form.valuta.choices = izbori
        if request.method == 'POST':
            if form.validate_on_submit():
                data={"posiljalac":session['user']['email'], "primalac":form.primalac.data, "valuta":form.valuta.data, "iznos":form.iznos.data}
                data = jsonify(data).get_data()
                zahtev = req.Request("http://localhost:5000/prenos")
                zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
                zahtev.add_header('Content-Length', len(data))
                try:
                    ret = req.urlopen(zahtev, data)
                    flash(ret.read().decode(), category='primary')
                    return redirect(url_for('transakcije.prikaz_transakcija'))
                except HTTPError as e:
                    flash(e.read().decode(), category='danger')
                    return render_template('prenos.html', form=form)
            
            if form.errors != {}:
                for msg in form.errors.values():
                    flash(msg.pop(), category='danger')
                return render_template('prenos.html', form=form)
        else:
            return render_template('prenos.html', form=form)
    else:
        redirect(url_for('user.login'))

    
@transakcije.route('/prikaz', methods=['GET','POST'])
def prikaz_transakcija():
    if 'user' in session:
        primljene_form=PretragaForm()
        poslate_form=PretragaForm()
        

        try:
            ret = req.urlopen(f'http://localhost:5000/transakcije/{session["user"]["id"]}')
            user = json.loads(ret.read())
            session['user'] = user
            izbor=[]
            for t in user["primljene_transakcije"]:
                izbor.append((t['valuta'],t['valuta']))

            primljene_form.valuta.choices=izbor
            
            
            return render_template('transakcije.html', poslate=user['poslate_transakcije'], primljene=user['primljene_transakcije'],form=primljene_form)
        except HTTPError as e:
            flash(e.read().decode(), category='danger')
            return redirect(url_for('index'))

    else:
        return redirect(url_for('user.login'))

