from flask import Flask, render_template, url_for,request, flash, session,redirect,jsonify,g
from forms import ContactForm, RegisterForm, PortfolioCalculationForm, DetailedPortfolioCalculationForm
from function1 import portfolio_one,portfolio_one_b,portfolio_value_ts,portfolio_stats
from flask_mail import Mail,Message
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import datetime as datetime
import time as time
import pandas as pd
import numpy as np
import random
import decimal

sandpfile='^GSPC (2).csv'
vixfile= '^GSPTSE.csv'
tableS= pd.read_csv(sandpfile)
tableV = pd.read_csv(vixfile)
spf= '^GSPC.csv'
tableD = pd.read_csv(spf)

temppin = ''
tempemail=''
input_portfolio=None
output_portfolio=None


riskDefnArr = ['risk averse','risky','very risky','too risky','risk averse','risky','very risky','too risky','risk averse','risky','very risky','too risky','risk averse','risky','very risky','too risky']
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

# @app.route("/simple_chart")
# def chart():
#     labels = tableV['Date'].values.tolist()
#     a = tableS['Close'].values
#     b = tableV['Close'].values
#     ocolumn_divs = (a/a[0])*10000
#     tcolumn_divs = (b/b[0])*10000
#     return render_template('chart.html', tvalues=tcolumn_divs.tolist(), ovalues=ocolumn_divs.tolist(), labels=labels)

@app.route("/about", methods=['GET', 'POST'])
def about():
    form = PortfolioCalculationForm()
    detailedForm=DetailedPortfolioCalculationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            count = 0
            assets=[]
            values=[]
            for fieldname, value in form.data.items():
                if type(value) is type(decimal.Decimal(0)) or type(value)is int:
                    assets.append(fieldname)
                    values.append(float(value))
                    count+=value
                elif value == None:
                    assets.append(fieldname)
                    values.append(0)
            if count == 0:
                form.equities.errors.append('Please enter at least one value.')
                return render_template('about.html', form=form,detailedForm=detailedForm)
            global input_portfolio, output_portfolio
            input_portfolio = portfolio_one(assets,values)
            output_portfolio = portfolio_one_b()
            ED = datetime.datetime.now()
            SD = datetime.datetime.now() - datetime.timedelta(days=5*365)
            tcolumn_divs = portfolio_value_ts(input_portfolio.returns,input_portfolio.initial_value,SD,ED)
            ocolumn_divs = portfolio_value_ts(output_portfolio.returns,input_portfolio.initial_value,SD,ED)
            tstats = portfolio_stats(input_portfolio.returns,SD,ED)
            ostats = portfolio_stats(output_portfolio.returns,SD,ED)
            stats = pd.concat([tstats,ostats],axis=1)
            labels = list(map(np.datetime_as_string,tcolumn_divs.index.values))
            selected=['','selected','','','']
            return render_template('about.html', success = True, tvalues=tcolumn_divs.tolist(),selected=selected,stats=stats, ovalues=ocolumn_divs.tolist(), labels=labels)
        else:
            return render_template('about.html', form=form,detailedForm=detailedForm)
    return render_template("about.html",form=form,detailedForm=detailedForm)
@app.route("/detailedAbout", methods=['POST'])
def detailedAbout():
    form = PortfolioCalculationForm()
    detailedForm=DetailedPortfolioCalculationForm()
    if request.method == 'POST':
        if detailedForm.validate_on_submit():
            count = 0
            assets=[]
            values=[]
            for fieldname, value in detailedForm.data.items():
                if type(value) is type(decimal.Decimal(0)) or type(value)is int:
                    assets.append(fieldname)
                    values.append(float(value))
                    count+=value
                elif value == None:
                    assets.append(fieldname)
                    values.append(0)
            if count == 0:
                detailedForm.SPY.errors.append('Please enter at least one value.')
                return render_template('about.html', form=form,detailedForm=detailedForm)
            global input_portfolio, output_portfolio
            input_portfolio = portfolio_one(assets,values)
            output_portfolio = portfolio_one_b()
            ED = datetime.datetime.now()
            SD = datetime.datetime.now() - datetime.timedelta(days=5*365)
            tcolumn_divs = portfolio_value_ts(input_portfolio.returns,input_portfolio.initial_value,SD,ED)
            ocolumn_divs = portfolio_value_ts(output_portfolio.returns,input_portfolio.initial_value,SD,ED)
            tstats = portfolio_stats(input_portfolio.returns,SD,ED)
            ostats = portfolio_stats(output_portfolio.returns,SD,ED)
            stats = pd.concat([tstats,ostats],axis=1)
            labels = list(map(np.datetime_as_string,tcolumn_divs.index.values))
            selected=['','selected','','','']
            return render_template('about.html', success = True, tvalues=tcolumn_divs.tolist(), stats=stats,selected=selected, ovalues=ocolumn_divs.tolist(), labels=labels)
        else:
            return render_template('about.html', form=form,detailedForm=detailedForm)
    return render_template("about.html",form=form,detailedForm=detailedForm)

@app.route("/recalculateAbout", methods=['POST'])
def recalculateAbout():
    if request.method == 'POST':
        if(request.form['btn']=='3y'):
            selected=['selected','','','','']
            ED = datetime.datetime.now()
            SD = datetime.datetime.now() - datetime.timedelta(days=3*365)
        if(request.form['btn']=='5y'):
            selected=['','selected','','','']
            ED = datetime.datetime.now()
            SD = datetime.datetime.now() - datetime.timedelta(days=5*365)
        if(request.form['btn']=='10y'):
            selected=['','','selected','','']
            ED = datetime.datetime.now()
            SD = datetime.datetime.now() - datetime.timedelta(days=10*365)
        if(request.form['btn']=='crisis'):
            ED=datetime.datetime(2010,1,1)
            SD=datetime.datetime(2008,1,1)
            selected=['','','','selected','']
        if(request.form['btn']=='bull'):
            ED=datetime.datetime(2018,1,1)
            SD=datetime.datetime(2015,1,1)
            selected=['','','','','selected']
        if(request.form['btn']=='custom'):
            selected=['','','','','']
            if(request.form['ED']=='' or request.form['SD'] ==''):
                return render_template('about.html', error = 'Please enter the starting and ending dates for your desired time period.',selected=selected, tvalues=tcolumn_divs.tolist(), ovalues=ocolumn_divs.tolist(), labels=labels)
            SD= datetime.datetime.strptime(request.form['SD'], '%Y-%m-%d')
            ED= datetime.datetime.strptime(request.form['ED'], '%Y-%m-%d')
            if(ED<= SD):
                return render_template('about.html', error = 'Please enter a valid time period.',selected=selected, tvalues=tcolumn_divs.tolist(), ovalues=ocolumn_divs.tolist(), labels=labels)
        global input_portfolio, output_portfolio
        tcolumn_divs = portfolio_value_ts(input_portfolio.returns,input_portfolio.initial_value,SD,ED)
        ocolumn_divs = portfolio_value_ts(output_portfolio.returns,input_portfolio.initial_value,SD,ED)
        tstats = portfolio_stats(input_portfolio.returns,SD,ED)
        ostats = portfolio_stats(output_portfolio.returns,SD,ED)
        stats = pd.concat([tstats,ostats],axis=1)
        labels = list(map(np.datetime_as_string,tcolumn_divs.index.values))
        return render_template('about.html', success = True,selected=selected, stats=stats,tvalues=tcolumn_divs.tolist(), ovalues=ocolumn_divs.tolist(), labels=labels)


@app.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html')

def calculateSomething():
    time.sleep(10)
    return 'This is some elaborate test'
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
        return redirect(url_for('about'))
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

@app.route("/forgotpass", methods=['GET','POST'])
def forgotpass():
    if checkLoggedIn():
        return redirect(url_for('home')) 
    if request.method == 'POST':
        global temppin,tempemail
        if request.form.get('email')!=None:
            users = mongo.db['_Users']
            user = users.find_one({'email' : request.form['email']})
            tempemail=request.form['email']
            if user != None:
                pin = ''.join(random.choice('0123456789') for _ in range(6))
                temppin=pin
                msg = Message('AlphaFactory Password Reset Code.', sender='contact@alphafactory.ca', recipients=[tempemail])
                msg.html = render_template('resetpassword.html',code=temppin)
                mail.send(msg)
                return render_template("forgotpass.html",code=True)
            else:
                return render_template("forgotpass.html",code=None,error='No user with that email was found.')
        elif request.form.get('code')!=None:
            print(tempemail)
            if temppin != request.form.get('code'):
                return render_template("forgotpass.html",code =True, error='Incorrect Code')
            elif len(request.form.get('password')) <8:
                return render_template("forgotpass.html",code =True, error='Your password must be at least 8 characters in length.')
            elif request.form.get('password') != request.form.get('confirmpassword'):
                return render_template("forgotpass.html",code =True, error='Your passwords must match.')
            else:
                #update password and take to login page
                updateuserpassword(request.form.get('password'),tempemail)
                return redirect(url_for('login'))
    return render_template("forgotpass.html",code=None)

def updateuserpassword(password,email):
    users = mongo.db['_Users']
    user = users.find_one({'email' : email})
    user['password']= generate_password_hash(password, method='sha256')
    users.save(user)

@app.route("/questions")
def questions():
    if not checkLoggedIn():
        return redirect(url_for('login'))
    if session['fillQuestions'] == True:
        questionDB = mongo.db['_Questions']
        questions=[]
        for q in questionDB.find({}):
            questions.append(q)
        random.shuffle(questions)
        return render_template('questions.html',questions=questions)
    return redirect(url_for('home'))

@app.route('/check_questions', methods=['POST'])
def check():
    if request.method == 'POST':
	    risk = request.get_json()
    updateuserrisk(risk)
    return jsonify(success=True)

@app.route('/advisor', methods=['GET','POST'])
def advisor():
    if request.method == 'POST':
        return redirect(url_for('home'))
    return render_template('advisor.html')

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
        return redirect(url_for('about'))
    else:
        return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(error):
	return render_template('notfound.html')

if __name__ == '__main__':
    app.run(debug=True)
