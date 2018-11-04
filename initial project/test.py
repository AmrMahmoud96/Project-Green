from flask import Flask, render_template, url_for,request, flash, session,redirect,jsonify
from forms import ContactForm, RegisterForm, PortfolioCalculationForm
from flask_mail import Mail,Message
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import datetime,time
import pandas as pd
import numpy as np

sandpfile='^GSPC (2).csv'
vixfile= '^GSPTSE.csv'
tableS= pd.read_csv(sandpfile)
tableV = pd.read_csv(vixfile)
spf= '^GSPC.csv'
tableD = pd.read_csv(spf)


riskDefnArr = ['risk averse','risky','very risky','too risky']
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'AlphaFactory'
app.config['MONGO_URI'] = 'mongodb://Daniel_Kecman:M$FCapstone2018@alphafactory-shard-00-00-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-01-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-02-y7wfo.gcp.mongodb.net:27017/AlphaFactory?ssl=true&replicaSet=AlphaFactory-shard-0&authSource=admin&retryWrites=true'

mongo = PyMongo(app)

Bootstrap(app)

app.secret_key = 'this@is!the~secret-Code1221'

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'Alphafactory.capstone@gmail.com'
app.config["MAIL_PASSWORD"] = 'amamdast123'

mail = Mail()
mail.init_app(app)

@app.route("/simple_chart")
def chart():
    labels = tableV['Date'].values.tolist()
    a = tableS['Close'].values
    b = tableV['Close'].values
    ocolumn_divs = (a/a[0])*10000
    tcolumn_divs = (b/b[0])*10000
    return render_template('chart.html', tvalues=tcolumn_divs.tolist(), ovalues=ocolumn_divs.tolist(), labels=labels)

@app.route("/about", methods=['GET', 'POST'])
def about():
    form = PortfolioCalculationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            count = 0
            for d in form:
                if type(d.data) is int:
                    count+= d.data
            if count == 0:
                form.equities.errors.append('Please enter at least one value.')
                return render_template('about.html', form=form)
            labels = tableV['Date'].values.tolist()
            a = tableS['Close'].values
            b = tableV['Close'].values
            ocolumn_divs = (a/a[0])*10000
            tcolumn_divs = (b/b[0])*10000
            return render_template('about.html', success = True, tvalues=tcolumn_divs.tolist(), ovalues=ocolumn_divs.tolist(), labels=labels)
        else:
            return render_template('about.html', form=form)
    return render_template("about.html",form=form)

@app.route('/logout')
def logout():
    session['name'] = None
    session['email']=None
    session['logged_in'] = None
    return redirect(url_for('about'))

@app.route('/profile')
def profile():
    if not checkLoggedIn():
        return redirect(url_for('login'))
    users = mongo.db['_Users']
    profile = users.find_one({'email' : session['email']})
    profile['risk'] = riskDefnArr[profile.get('riskTol')]
    return render_template('profile.html',profile=profile)
def checkLoggedIn():
    if session==None:
        return False
    elif session['logged_in']==None:
        return False
    return True

@app.route("/contactus", methods=['GET', 'POST'])
def contactus():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            msg = Message(form.subject.data, sender='contact@alphafactory.ca', recipients=['Alphafactory.capstone@gmail.com'])
            msg.body = """
            From: %s: <%s>
            %s
            """ % (form.name.data, form.email.data, form.message.data)
            mail.send(msg)
            return render_template('contactus.html', success="True")
        else:
            return render_template('contactus.html', form=form)

    elif request.method == 'GET':
        return render_template('contactus.html', form=form)

@app.route("/home")
def home():
    if not checkLoggedIn():
        return redirect(url_for('login'))
    elif session['fillQuestions']==True:
        return redirect(url_for('questions'))
    labels = tableD['Date'].values.tolist()
    b = tableD['Close'].values
    tcolumn_divs = (b/b[0])*15000
    return render_template('home.html',tvalues=tcolumn_divs.tolist(), labels=labels)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if checkLoggedIn():
        return redirect(url_for('home'))
    if request.method == 'POST':
        users = mongo.db['_Users']
        login_user = users.find_one({'email' : request.form['email']})

        if login_user:
            if check_password_hash(login_user['password'], request.form['password']):
                session['name'] = login_user['firstName'] + ' '+ login_user['lastName']
                session['email'] = login_user['email']
                session['logged_in']= True
                session['fillQuestions'] = login_user['fillQuestions']
                session['riskTol'] = login_user.get('riskTol')
                return redirect(url_for('home'))
        return render_template("login.html", error="Invalid Email/Password.")
    return render_template("login.html")

@app.route("/joinus", methods=['GET', 'POST'])
def joinus():
    if checkLoggedIn():
        return redirect(url_for('home'))
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            users = mongo.db['_Users']
            existing_user = users.find_one({'email' : request.form['email']})
            if existing_user is None:
                hashpass = generate_password_hash(form.password.data, method='sha256')
                users.insert({'firstName' : request.form['firstName'].capitalize(),'lastName' : request.form['lastName'].capitalize(),'dob' : request.form['dob'],'email' : request.form['email'], 'password' : hashpass,'fillQuestions':True})
                session['name'] = request.form['firstName'] + ' '+ request.form['lastName']
                session['email'] = request.form['email']
                session['logged_in'] = True
                session['fillQuestions']=True
                return redirect(url_for('questions'))
            return render_template("joinus.html",form=form,existing=True)
        return render_template("joinus.html",form=form)
    return render_template("joinus.html",form=form)

@app.route("/forgotpass")
def forgotpass():
    if checkLoggedIn():
        return redirect(url_for('home'))
    return render_template("forgotpass.html")

@app.route("/questions")
def questions():
    if not checkLoggedIn():
        return redirect(url_for('login'))
    if session['fillQuestions'] == True:
        questionDB = mongo.db['_Questions']
        questions=[]
        for q in questionDB.find({}):
            questions.append(q)#questions = [{'qid':'1','optiona': 'option a', 'optionb':'option b'},{'qid':'2','optiona': 'THis is a super long test option to find out how it would look', 'optionb':'option b1'},{'qid':'3','optiona': 'option a2', 'optionb':'option b2'}]
        return render_template('questions.html',questions=questions)
    return redirect(url_for('home'))

@app.route('/check_questions', methods=['POST'])
def check():
    if request.method == 'POST':
	    risk = request.get_json()
    updateuserrisk(risk)
    return jsonify(success=True)

@app.route('/questions/finished')
def finished():
    #print(finished)
    return redirect(url_for('home'))

def updateuserrisk(risk):
    users = mongo.db['_Users']
    login_user = users.find_one({'email' : session['email']})
    login_user['riskTol'] =int(risk['risk'])
    session['riskTol'] = int(risk['risk'])
    login_user['fillQuestions']= False
    session['fillQuestions']=False
    users.save(login_user)

@app.route("/")
def landingpage():
    if session.get('logged_in') == None:
        session['name'] = None
        session['logged_in'] = None
        return render_template('about.html')
    else:
        return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(error):
	return render_template('notfound.html')

if __name__ == '__main__':
    app.run(debug=True)
