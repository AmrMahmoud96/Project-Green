from flask import Flask, render_template, url_for,request, flash, session,redirect,jsonify,g
from forms import ContactForm, RegisterForm, PortfolioCalculationForm
from function_1_2 import portfolio_stats, portfolio_value_ts, compare_portfolios, portfolio_one_b
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


#variables for multi-page functions
assets =[]
values=[]

#define risk tolerance by number and time horizon
riskDefnArr1 = ['Aggressive','Aggressive','Adventurous','Adventurous','Adventurous','Balanced','Balanced','Balanced','Balanced','Conservative','Conservative','Conservative','Preservation','Preservation','Preservation','Preservation']
riskDefnArr2 = ['Aggressive','Aggressive','Aggressive','Adventurous','Adventurous','Adventurous','Balanced','Balanced','Balanced','Balanced','Conservative','Conservative','Conservative','Preservation','Preservation','Preservation']
riskDefnArr3 = ['Aggressive','Aggressive','Aggressive','Aggressive','Adventurous','Adventurous','Adventurous','Adventurous','Balanced','Balanced','Balanced','Conservative','Conservative','Conservative','Preservation','Preservation']
riskArr1 = ['Extremely Risk-Seeking','Extremely Risk-Seeking','Risk-Seeking','Risk-Seeking','Risk-Seeking','','Neutral','Neutral','Neutral','Risk-Averse','Risk-Averse','Risk-Averse','Extremely Risk-Averse','Extremely Risk-Averse','Extremely Risk-Averse','Extremely Risk-Averse']
riskArr2 = ['Extremely Risk-Seeking','Extremely Risk-Seeking','Extremely Risk-Seeking','Risk-Seeking','Risk-Seeking','Risk-Seeking','Neutral','Neutral','Neutral','Neutral','Risk-Averse','Risk-Averse','Risk-Averse','Extremely Risk-Averse','Extremely Risk-Averse','Extremely Risk-Averse']
riskArr3 = ['Extremely Risk-Seeking','Extremely Risk-Seeking','Extremely Risk-Seeking','Extremely Risk-Seeking','Risk-Seeking','Risk-Seeking','Risk-Seeking','Risk-Seeking','Neutral','Neutral','Neutral','Risk-Averse','Risk-Averse','Risk-Averse','Extremely Risk-Averse','Extremely Risk-Averse']


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'AlphaFactory'
app.config['MONGO_URI'] = 'mongodb://Daniel_Kecman:M$FCapstone2018@alphafactory-shard-00-00-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-01-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-02-y7wfo.gcp.mongodb.net:27017/AlphaFactory?ssl=true&replicaSet=AlphaFactory-shard-0&authSource=admin&retryWrites=true'

mongo = PyMongo(app)

Bootstrap(app)

app.secret_key = 'this@is!the~secret-Code1221'

app.config.update(dict(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'Alphafactory.capstone@gmail.com',
    MAIL_PASSWORD = 'amamdast123',
))
mail = Mail(app)
@app.route("/about", methods=['GET', 'POST'])
def about():
    form = PortfolioCalculationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            global assets,values
            count = 0
            assets=[]
            values=[]
            for fieldname, value in form.data.items():
                if (type(value) is type(decimal.Decimal(0)) or type(value)is int) and value>0:
                    assets.append(fieldname)
                    values.append(float(value))
                    count+=value
            if count == 0:
                form.SPY.errors.append('Please enter at least one value.')
                return render_template('about.html', form=form,error_occured=True)
            print(assets)
            print(values)
            ED = datetime.datetime.now()
            SD = datetime.datetime.now() - datetime.timedelta(days=10*365)
            comp_portfolio = compare_portfolios(SD,ED,assets,values)
            tcolumn_divs = comp_portfolio[1]
            ocolumn_divs = comp_portfolio[4]
            tstats = comp_portfolio[2]
            ostats = comp_portfolio[5]
            stats = pd.concat([tstats,ostats],axis=1)
            stats = stats[(stats.index !=  'Treynor') & (stats.index !=  'R-Squared')]
            labels = list(map(np.datetime_as_string,tcolumn_divs.index.values))
            selected=['','','selected','','']
            return render_template('about.html', success = True, tvalues=tcolumn_divs.tolist(),selected=selected,stats=stats[0:5],extrastats=stats[5:], ovalues=ocolumn_divs.tolist(), labels=labels)
        else:
            return render_template('about.html', form=form)
    return render_template("about.html",form=form)
@app.route("/detailedAbout", methods=['POST'])
def detailedAbout():
    form = PortfolioCalculationForm()
    if request.method == 'POST':
        global assets,values
        count = 0
        assets=[]
        values=[]
        for x in request.form:
            try:
                if float(request.form[x])>0:
                    assets.append(x)
                    values.append(float(request.form[x]))
                    count+=float(request.form[x])
            except ValueError:
                pass
        if count == 0:
            return render_template('about.html', form=form,error='Please enter at least one value.')
        print(assets)
        print(values)
        ED = datetime.datetime.now()
        SD = datetime.datetime.now() - datetime.timedelta(days=10*365)
        comp_portfolio = compare_portfolios(SD,ED,assets,values)
        tcolumn_divs = comp_portfolio[1]
        ocolumn_divs = comp_portfolio[4]
        tstats = comp_portfolio[2]
        ostats = comp_portfolio[5]
        stats = pd.concat([tstats,ostats],axis=1)
        stats = stats[(stats.index !=  'Treynor') & (stats.index !=  'R-Squared')]
        labels = list(map(np.datetime_as_string,tcolumn_divs.index.values))
        selected=['','','selected','','']
        return render_template('about.html', success = True, tvalues=tcolumn_divs.tolist(), stats=stats[0:5],extrastats=stats[5:],selected=selected, ovalues=ocolumn_divs.tolist(), labels=labels)
    return render_template("about.html",form=form)

@app.route("/recalculateAbout", methods=['POST'])
def recalculateAbout():
    if request.method == 'POST':
        global assets,values
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
        comp_portfolio = compare_portfolios(SD,ED,assets,values)
        tcolumn_divs = comp_portfolio[1]
        ocolumn_divs = comp_portfolio[4]
        tstats = comp_portfolio[2]
        ostats = comp_portfolio[5]
        stats = pd.concat([tstats,ostats],axis=1)
        stats = stats[(stats.index !=  'Treynor') & (stats.index !=  'R-Squared')]
        labels = list(map(np.datetime_as_string,tcolumn_divs.index.values))
        return render_template('about.html', success = True,selected=selected, stats=stats[0:5],extrastats=stats[5:],tvalues=tcolumn_divs.tolist(), ovalues=ocolumn_divs.tolist(), labels=labels)


@app.route('/test', methods=['GET', 'POST'])
def test():
    time.sleep(5)
    return render_template('test.html')

def calculateSomething():
    time.sleep(10)
    return 'This is some elaborate test'
@app.route('/logout')
def logout():
    session = None
    return redirect(url_for('about'))

@app.route('/profile')
def profile():
    if not checkLoggedIn():
        return redirect(url_for('login'))
    if session.get('portfolio')==None:
        return redirect(url_for('advisor'))
    if session.get('fillQuestions')==True:
        return redirect(url_for('questions'))
    users = mongo.db['_Users']
    profile = users.find_one({'email' : session['email']})
    profile['risk'] = profile.get('riskTol')
    profile['riskPortfolio'] = profile.get('portfolio').get('risk')
    profile['riskProfile'] = profile.get('riskProfile')
    return render_template('profile.html',profile=profile)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if not checkLoggedIn():
        return redirect(url_for('forgotpass'))
    users = mongo.db['_Users']
    profile = users.find_one({'email' : session['email']})
    if request.method == 'POST':
        if check_password_hash(profile['password'], request.form['password']):
            if(request.form['newpassword'] == request.form['confirmpassword']):
                if(len(request.form['newpassword'])>=8):
                    profile['password']= generate_password_hash(request.form['newpassword'], method='sha256')
                    users.save(profile)
                    return redirect(url_for('home'))
                return render_template('changepassword.html',error="New Password needs to be at least 8 characters.")
            else:
                return render_template('changepassword.html',error="New passwords need to match.")
        else:
            return render_template('changepassword.html',error="Invalid password.")
    return render_template('changepassword.html')


@app.route('/change_risk')
def change_risk():
    if not checkLoggedIn():
        return redirect(url_for('login'))
    users = mongo.db['_Users']
    profile = users.find_one({'email' : session['email']})
    profile['fillQuestions'] = True
    session['fillQuestions'] = True
    users.save(profile)
    return redirect(url_for('questions'))

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
    elif session.get('portfolio') == None:
        return redirect(url_for('advisor'))
    elif session['fillQuestions']==True:
        return redirect(url_for('questions'))
    elif session['portfolio'].get('risk',None)==None:
        return redirect(url_for('selection'))
    p = portfolio_one_b(session['portfolio']['risk'])
    #SD= datetime.datetime.now() - datetime.timedelta(days=3*365)
    SD= datetime.datetime.now() - datetime.timedelta(days=15*365)
    ED= datetime.datetime.now()
    tcolumn_divs = portfolio_value_ts(p.returns,session['portfolio']['initial'], SD,ED)
    stats = portfolio_stats(p,SD,ED).to_frame()
    stats = stats[(stats.index !=  'Treynor') & (stats.index !=  'R-Squared')]
    labels = list(map(np.datetime_as_string,tcolumn_divs.index.values))
    return render_template('home.html',tvalues=tcolumn_divs.tolist(), labels=labels,stats=stats)

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
                session['riskTolNum']=login_user.get('riskTolNum')
                session['fillQuestions'] = login_user['fillQuestions']
                session['riskTol'] = login_user.get('riskTol')
                session['portfolio'] = login_user.get('portfolio')
                session['riskProfile']=login_user.get('riskProfile',None)
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
                session['portfolio']=None
                session['fillQuestions']=True
                return redirect(url_for('advisor'))
            return render_template("joinus.html",form=form,existing=True)
        return render_template("joinus.html",form=form)
    return render_template("joinus.html",form=form)

@app.route("/forgotpass", methods=['GET','POST'])
def forgotpass(): 
    if request.method == 'POST':
        if request.form.get('email')!=None:
            users = mongo.db['_Users']
            user = users.find_one({'email' : request.form['email']})
            if user != None:
                pin = ''.join(random.choice('0123456789') for _ in range(6))
                session['pin']=generate_password_hash(pin,method='sha256')
                session['email']=request.form['email']
                msg = Message('AlphaFactory Password Reset Code.', sender='contact@alphafactory.ca', recipients=[session['email']])
                msg.html = render_template('resetpassword.html',code=pin)
                mail.send(msg)
                return render_template("forgotpass.html",code=True)
            else:
                return render_template("forgotpass.html",code=None,error='No user with that email was found.')
        elif request.form.get('code')!=None:
            if not check_password_hash(session['pin'], request.form.get('code')):
                return render_template("forgotpass.html",code =True, error='Incorrect Code')
            elif len(request.form.get('password')) <8:
                return render_template("forgotpass.html",code =True, error='Your password must be at least 8 characters in length.')
            elif request.form.get('password') != request.form.get('confirmpassword'):
                return render_template("forgotpass.html",code =True, error='Your passwords must match.')
            else:
                #update password and take to login page
                updateuserpassword(request.form.get('password'),session['email'])
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
    if session.get('portfolio')==None or session.get('finishedInit',True)==False:
        return redirect(url_for('advisor'))
    if session.get('fillQuestions') == True:
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
    updateuserrisk(risk['risk'],None)
    return jsonify(success=True)

@app.route('/advisor', methods=['GET','POST'])
def advisor():
    if not checkLoggedIn():
        return redirect(url_for('login'))
    if session.get('fillQuestions')==False or session.get('portfolio')==None or session.get('newPortfolio',None)==True:
        if request.method == 'POST':
            users = mongo.db['_Users']
            profile = users.find_one({'email' : session['email']})
            if profile.get('portfolio',None) == None:
                portfolio = {'initial':float(request.form['initial']),'horizon':int(request.form['horizon']),'dateCreated':datetime.datetime.now()}
            else:
                portfolio = {'risk':profile['portfolio'].get('risk'),'initial':float(request.form['initial']),'horizon':int(request.form['horizon']),'dateCreated':datetime.datetime.now()}                
            if session.get('newPortfolio',None)!=True:
                profile['portfolio']=portfolio
                users.save(profile)
            else:
                portfolio['risk']=None
            session['portfolio']=portfolio
            session['finishedInit']=True
            return redirect(url_for('home'))
        return render_template('advisor.html')
    return redirect(url_for('home'))

@app.route('/advisor_options', methods=['GET','POST'])
def advisor_options():
    if not checkLoggedIn():
        return redirect(url_for('login'))
    if session.get('newPortfolio')==True:
        return redirect(url_for('home'))
    if request.method == 'POST':
        resp = request.get_json()
        if resp['selection']=='CP':
            return jsonify(success=True,path='selection')
        if resp['selection']=='CR':
            session['finishedInit']=False
            session['newPortfolio']=True
            session['fillQuestions']=True
            return jsonify(success=True,path='advisor') 
        if resp['selection']=='CA':
            msg = Message('Request for meeting.', sender='contact@alphafactory.ca', recipients=['Alphafactory.capstone@gmail.com'])
            msg.body = """
            From: %s: <%s>
            Hello, I would like to schedule a meeting with an advisor.
            """ % (session['name'], session['email'])
            mail.send(msg)
            return jsonify(success=True,path='contact_complete')   
    return render_template('advisor_page.html')

@app.route('/questions/finished')
def finished():
    return redirect(url_for('selection'))

@app.route('/contact_complete')
def contact_complete():
    return render_template('contactus.html', success="True")

@app.route('/selection', methods=['GET','POST'])
def selection():
    if session.get('riskProfile') == None or session.get('portfolio')==None:
        return redirect(url_for('home'))
    if request.method=='POST':
        resp = request.get_json()
        users = mongo.db['_Users']
        profile = users.find_one({'email' : session['email']})
        profile['portfolio']=session['portfolio']
        users.save(profile)
        updateuserrisk(session.get('riskTolNum'),resp['selection'])
        session['finishedInit']=None
        session['newPortfolio']=None
        return jsonify(success=True)
    portfolioStats = mongo.db['Portfolio_Stats']
    ps= pd.DataFrame(list(portfolioStats.find({"Stat":{ '$in' : [ "CAGR","Vol","Max DD"] }})))
    ps=ps.drop(['_id','Stat'],axis=1)
    ps=ps.sort_values(ps.first_valid_index(), axis=1)
    return render_template('selection.html',portfolio=session['portfolio'],recommendation=session['riskProfile'],recommended=ps[session['riskProfile']],ps=ps.drop(session['riskProfile'],axis=1))

@app.route('/selection/finished')
def selection_complete():
    
    return redirect(url_for('home'))

def updateuserrisk(risk,selected):
    users = mongo.db['_Users']
    login_user = users.find_one({'email' : session['email']})
    horizon = session['portfolio']['horizon']
    if horizon>=15:
        riskProfile = riskDefnArr3[risk]
        tolerance = riskArr3[risk]
    elif horizon>=5:
        riskProfile = riskDefnArr2[risk]
        tolerance = riskArr2[risk]
    else:
        riskProfile = riskDefnArr1[risk]
        tolerance = riskArr1[risk]

    login_user['riskProfile'] = riskProfile
    login_user['riskTolNum']= risk
    login_user['riskTol'] = tolerance
    if selected:
        login_user['portfolio']['risk']= selected
        session['portfolio']['risk']= selected
    session['riskTol'] = tolerance
    session['riskProfile'] = riskProfile
    session['riskTolNum']= risk
    login_user['fillQuestions']= False
    session['fillQuestions']=False
    if session.get('newPortfolio',None)!=True or selected:
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
