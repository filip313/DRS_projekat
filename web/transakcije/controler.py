from transakcije import *
from transakcije.forme import UplataForm, PrenosForm,Pretraga1Form,Pretraga2Form
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

def popuni_formu(form,list):
    izbor={}
    for t in list:
         izbor[t['valuta']]=t['valuta']
                
    form.valuta.choices= [(k, v) for k, v in izbor.items()]
    form.valuta.choices.insert(0,("","   "))
    form.stanje.choices=[("","  "),("OBRADA","OBRADA"),("OBRADJENO","OBRADJENO"),("ODBIJENO","ODBIJENO")]  


def pretrazi(form,list,flag):
    pretraga_pr=[]
    for t in list:
        if form.valuta.data != "":
            if form.valuta.data== t['valuta']:
                 pretraga_pr.append(t)
            else:
                    pretraga_pr.append(t)
    if form.stanje.data !="":
        pretraga_pr = [t for t in pretraga_pr if t['stanje'] == form.stanje.data]
    if form.email.data !="":
        if flag:
            pretraga_pr = [t for t in pretraga_pr if form.email.data in t['posiljalac_id']]
        else:
            pretraga_pr = [t for t in pretraga_pr if form.email.data in t['primalac_id']]
    return pretraga_pr

@transakcije.route('/prikaz', methods=['GET','POST'])
def prikaz_transakcija():
    if 'user' in session:
        primljene_form=Pretraga2Form()
        poslate_form=Pretraga1Form()
        
        if request.method=='GET':
            try:
                ret = req.urlopen(f'http://localhost:5000/transakcije/{session["user"]["id"]}')
                user = json.loads(ret.read())
                session['user'] = user
                popuni_formu(primljene_form,user['primljene_transakcije'])
                popuni_formu(poslate_form,user['poslate_transakcije'])
                return render_template('transakcije.html', poslate=user['poslate_transakcije'], primljene=user['primljene_transakcije'],form_pr=primljene_form,form_po=poslate_form)
            except HTTPError as e:
                flash(e.read().decode(), category='danger')
                return redirect(url_for('index'))
        else:
            if primljene_form.submit2.data:
                print(type(primljene_form.valuta.data),flush=True)
                user=session['user']
                pretraga_pr=[]
                for t in user['primljene_transakcije']:
                    if primljene_form.valuta.data != "":
                        if primljene_form.valuta.data== t['valuta']:
                            pretraga_pr.append(t)
                        else:
                                pretraga_pr.append(t)
                if primljene_form.stanje.data !="":
                    pretraga_pr = [t for t in pretraga_pr if t['stanje'] == primljene_form.stanje.data]
                if primljene_form.email.data !="":
                    pretraga_pr = [t for t in pretraga_pr if primljene_form.email.data in t['posiljalac_id']]
                   
                            
                popuni_formu(primljene_form,user['primljene_transakcije'])
                popuni_formu(poslate_form,user['poslate_transakcije'])
                return render_template('transakcije.html', poslate=user['poslate_transakcije'], primljene=pretraga_pr,form_pr=primljene_form,form_po=poslate_form)

            elif poslate_form.submit1.data:
                user=session['user']
                pretraga_pr=pretrazi(poslate_form,user['poslate_transakcije'],False)
                popuni_formu(primljene_form,user['primljene_transakcije'])
                popuni_formu(poslate_form,user['poslate_transakcije'])
                return render_template('transakcije.html', poslate=pretraga_pr, primljene=user['primljene_transakcije'],form_pr=primljene_form,form_po=poslate_form)
    else:
        return redirect(url_for('user.login'))



