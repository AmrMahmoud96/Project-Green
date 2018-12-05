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
 
# Set up DB connection config
app.config['MONGO_DBNAME'] = 'AlphaFactory'
app.config['MONGO_URI'] = 'mongodb://Daniel_Kecman:M$FCapstone2018@alphafactory-shard-00-00-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-01-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-02-y7wfo.gcp.mongodb.net:27017/AlphaFactory?ssl=true&replicaSet=AlphaFactory-shard-0&authSource=admin&retryWrites=true'
mongo = PyMongo(app)

#Set up Bootstrap for use with WTForms
Bootstrap(app)

#secret key for app
app.secret_key = 'this@is!the~secret-Code1221'

#Set up mailing service that is used to send all Emails 
app.config.update(dict(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'Alphafactory.capstone@gmail.com',
    MAIL_PASSWORD = 'amamdast123',
))
mail = Mail(app)

'''
About Page

Routing for the about page that returns the about us page with the Simple and Detailed forms for the user 
to input the parameters for Function 2 and 1 in. Once the parameters are returned (and validated) they are
sent to the backend where they are run through Function 2 to be compared to our portfolios and ultimately
returns a better portfolio measure by a higher Sharpe Ratio. 
'''
@app.route("/about", methods=['GET', 'POST'])
def about():
    #WTForms initialization for the simple form
    form = PortfolioCalculationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            global assets,values
            count = 0
            assets=[]
            values=[]
            #Get assets and allocations from the form
            for fieldname, value in form.data.items():
                if (type(value) is type(decimal.Decimal(0)) or type(value)is int) and value>0:
                    assets.append(fieldname)
                    values.append(float(value))
                    count+=value
            #if there is no values entered, return an error
            if count == 0:
                form.SPY.errors.append('Please enter at least one value.')
                return render_template('about.html', form=form,error_occured=True)
            #default to 10 year horizon and run Function 2 to generate a dominating portfolio
            ED = datetime.datetime.now()
            SD = datetime.datetime.now() - datetime.timedelta(days=10*365)
            comp_portfolio = compare_portfolios(SD,ED,assets,values)
            #tcolumn_divs = their portfolios values and ocolumn_divs = our portfolios values as a time series
            tcolumn_divs = comp_portfolio[1]
            ocolumn_divs = comp_portfolio[4]
            tstats = comp_portfolio[2]
            ostats = comp_portfolio[5]
            stats = pd.concat([tstats,ostats],axis=1)
            #drop treynor and r-squared stats
            stats = stats[(stats.index !=  'Treynor') & (stats.index !=  'R-Squared')]
            #required datatype mapping for Chart.js
            labels = list(map(np.datetime_as_string,tcolumn_divs.index.values))
            selected=['','','selected','','']
            return render_template('about.html', success = True, tvalues=tcolumn_divs.tolist(),selected=selected,stats=stats[0:5],extrastats=stats[5:], ovalues=ocolumn_divs.tolist(), labels=labels)
        else:
            return render_template('about.html', form=form)
    return render_template("about.html",form=form)


'''
Detailed about

Route dedicated to the detailed form post from the about page. Although it returns the exact same thing, the methods 
for gathering data and validation are different as the forms are different. This had to be set up like this in the 
essence of making a very user friendly site.
'''
@app.route("/detailedAbout", methods=['POST'])
def detailedAbout():
    form = PortfolioCalculationForm()
    if request.method == 'POST':
        global assets,values
        count = 0
        assets=[]
        values=[]
        #get the assets and allocations of each ETF
        for x in request.form:
            try:
                if float(request.form[x])>0:
                    assets.append(x)
                    values.append(float(request.form[x]))
                    count+=float(request.form[x])
            except ValueError:
                pass
        #need at least one value
        if count == 0:
            return render_template('about.html', form=form,error='Please enter at least one value.')
        #runs function 2 with a default 10 year horizon
        ED = datetime.datetime.now()
        SD = datetime.datetime.now() - datetime.timedelta(days=10*365)
        comp_portfolio = compare_portfolios(SD,ED,assets,values)
        tcolumn_divs = comp_portfolio[1]
        ocolumn_divs = comp_portfolio[4]
        tstats = comp_portfolio[2]
        ostats = comp_portfolio[5]
        stats = pd.concat([tstats,ostats],axis=1)
        stats = stats[(stats.index !=  'Treynor') & (stats.index !=  'R-Squared')]
        #required datatype mapping for Chart.js
        labels = list(map(np.datetime_as_string,tcolumn_divs.index.values))
        selected=['','','selected','','']
        return render_template('about.html', success = True, tvalues=tcolumn_divs.tolist(), stats=stats[0:5],extrastats=stats[5:],selected=selected, ovalues=ocolumn_divs.tolist(), labels=labels)
    return render_template("about.html",form=form)

'''
Recalculate About

Method called when user wishes to view portfolio comparisons over different time horizons. We take the assets 
and values (stored globally from before) and perform another function 2 call in order to generate a dominating
portfolio each time.
'''
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

'''
Log out

Clears the current session of all variables and logs the user out. No authentication handling required here 
since everything is done through the session variable. Also used to reset the session in the case of testing.
'''
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('about'))

'''
Profile page

Retrieves the information about the currently signed in user and displays it for the user to review.
Changes can not be made to the information (asside from password) on file unless through manual DB 
overwrites.
'''
@app.route('/profile')
def profile():
    # Check if the user is not logged in, redirect them back to the login page if they aren't.
    if not checkLoggedIn():
        return redirect(url_for('login'))
    #if the user doesn't currently have a portfolio, redirect them to Function 3 and have them go through the process
    if session.get('portfolio')==None:
        return redirect(url_for('advisor'))
    #if the user needs to fill their questionnaire, redirect them to the questionnaire page before they can view their profile
    if session.get('fillQuestions')==True:
        return redirect(url_for('questions'))
    # Setup db user collections connection.
    users = mongo.db['_Users']
    # Query for the logged in users profile through their email (email is unique).
    profile = users.find_one({'email' : session.get('email')})
    # collect the information regarding the logged in user and send it to the template for rendering.
    profile['risk'] = profile.get('riskTol')
    profile['riskPortfolio'] = profile.get('portfolio').get('risk')
    profile['riskProfile'] = profile.get('riskProfile')
    return render_template('profile.html',profile=profile)

'''
Change Password

Route that allows users to change their password if they're logged in. They are required to type their old
password in for security purposes and have the same validations performed on their password field (8 character min)
as well as a confirmation check to ensure they typed the right password twice. Once everything is validated,
the new password is encoded and sent to the DB to be stored for later reference.
'''
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    # if the user is not logged in, redirect them to forgot password page (instead of log in)
    if not checkLoggedIn():
        return redirect(url_for('forgotpass'))
    
    # Setup db user collections connection.
    users = mongo.db['_Users']
    # collect the information regarding the logged in user and send it to the template for rendering.
    profile = users.find_one({'email' : session.get('email')})
    if request.method == 'POST':
        #decode the password on file and check if it matches the old password typed by the user, else return error
        if check_password_hash(profile['password'], request.form['password']):
            #confirm that the two passwords typed by the user match, otherwise return error
            if(request.form['newpassword'] == request.form['confirmpassword']):
                #confirm password length is greater than 8 characters, else return error
                if(len(request.form['newpassword'])>=8):
                    #Encode the password and update the user file on the DB. Afterwards, redirect to the home page
                    profile['password']= generate_password_hash(request.form['newpassword'], method='sha256')
                    users.save(profile)
                    return redirect(url_for('home'))
                return render_template('changepassword.html',error="New Password needs to be at least 8 characters.")
            else:
                return render_template('changepassword.html',error="New passwords need to match.")
        else:
            return render_template('changepassword.html',error="Invalid password.")
    return render_template('changepassword.html')


'''
Change Risk

Route design specifically to change the user's risk through the profile page. If the user clicks the change risk
button on the profile page, this method will update the boolean flag on the user's profile in the db which
indicates that they are required to fill out the questionnaire.
'''
@app.route('/change_risk')
def change_risk():
    # if the user is not logged in, redirect them to the log in page
    if not checkLoggedIn():
        return redirect(url_for('login'))
    # Setup db user collections connection.
    users = mongo.db['_Users']
    # collect the information regarding the logged in user and send it to the template for rendering.
    profile = users.find_one({'email' : session.get('email')})
    # Set the fillQuestions flag to true on both the session and the DB and update the Db
    profile['fillQuestions'] = True
    session['fillQuestions'] = True
    users.save(profile)
    #redirect the user to the questions page where they can fill the questionnaire out.
    return redirect(url_for('questions'))

'''
Check Logged In
Simple auxilary/utility function to check if the user is logged in to save on redundent/repeated code.
'''
def checkLoggedIn():
    # if the session is empty, they are not logged in (return false)
    if session==None:
        return False
    # if the logged in flag is None, they are not logged in (return false) [note, entire session is set to none on log out (redundent to check this)]
    elif session.get('logged_in')==None:
        return False
    #else return true.
    return True
    
'''
Contact Us

Page designed for the users to be able to contact us through our gmail account: Alphafactory.capstone@gmail.com.
Page will take in user input on subject, email, name, and message and generate a message to send to our gmail account
where we can review the contents and get back to them.

Fully functional in local and production environments.
'''
@app.route("/contactus", methods=['GET', 'POST'])
def contactus():
    # Initialize contact from from WTForms
    form = ContactForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            #After form validation, compose message with the subject line as user's input, recipient as our own email, and message contents from user inputs as the body
            msg = Message(form.subject.data, sender='contact@alphafactory.ca', recipients=['Alphafactory.capstone@gmail.com'])
            msg.body = """
            From: %s: <%s>
            %s
            """ % (form.name.data, form.email.data, form.message.data)
            #Send the message through the mailing service and let the user know that the message has been sent
            mail.send(msg)
            return render_template('contactus.html', success="True")
        else:
            #if there is an error in validation, return the form with the error message.
            return render_template('contactus.html', form=form)

    elif request.method == 'GET':
        return render_template('contactus.html', form=form)


'''
Home page.

Home page is meant to be a dashboard for logged in and registered users only. Redirect any not logged in users to the about/landing page
if they stumble here. Otherwise, take the user's profile and produce their dashboard with their current portfolio type, weightings,
returns, and stats. Also allow users to download the full PDF tearsheet report of their portfolio through HTML.
'''
@app.route("/home")
def home():
    # if the user is not logged in, redirect them to the about page
    if not checkLoggedIn():
        return redirect(url_for('about'))
    # if the user has no portfolio, send them to function 3 to create a portfolio
    elif session.get('portfolio') == None:
        return redirect(url_for('advisor'))
    # if the user needs to fill their questionnaire, send them to the questionnaire.    
    elif session.get('fillQuestions')==True:
        return redirect(url_for('questions'))
    # if the user hasn't selected the type of portfolio they want, send them to the selection page
    elif session['portfolio'].get('risk',None)==None:
        return redirect(url_for('selection'))
    #initialize portfolio with the user's selection of portfolio risk type
    p = portfolio_one_b(session['portfolio']['risk'])
    #default the time horizon to 15 years for demo purposes (in production we would use portfolio generation date as stored in the db)
    SD= datetime.datetime.now() - datetime.timedelta(days=15*365)
    ED= datetime.datetime.now()
    #Generate portfolio returns and stats through function 1
    tcolumn_divs = portfolio_value_ts(p.returns,session['portfolio']['initial'], SD,ED)
    stats = portfolio_stats(p,SD,ED).to_frame()
    stats = stats[(stats.index !=  'Treynor') & (stats.index !=  'R-Squared')]
    labels = list(map(np.datetime_as_string,tcolumn_divs.index.values))
    return render_template('home.html',tvalues=tcolumn_divs.tolist(), labels=labels,stats=stats)

'''
Log in page

Page dedicated for registered users to log in through. Queries for user file in the db and confirms password. 
Populates the session variable so that user session persists through the site and allows them to navigate to the right pages.
'''
@app.route("/login", methods=['GET', 'POST'])
def login():
    # if the user is logged in, redirect them to the home page
    if checkLoggedIn():
        return redirect(url_for('home'))
    if request.method == 'POST':
        # Setup db user collections connection.
        users = mongo.db['_Users']
        # Retrieve info on login_user through the entered email.
        login_user = users.find_one({'email' : request.form['email']})
        # If the email/user combo exists in the db, continue to check passwords match, else return error
        if login_user:
            # Check the encoded DB password on file actually matches the typed in password, else return error
            if check_password_hash(login_user['password'], request.form['password']):
                #On successful log in store required information in the session variable
                session['name'] = login_user['firstName'] + ' '+ login_user['lastName']
                session['email'] = login_user['email']
                session['logged_in']= True
                session['riskTolNum']=login_user.get('riskTolNum')
                #important for questionnaire and flow
                session['fillQuestions'] = login_user['fillQuestions']
                session['riskTol'] = login_user.get('riskTol')
                #important for home page and general flow
                session['portfolio'] = login_user.get('portfolio')
                session['riskProfile']=login_user.get('riskProfile',None)
                return redirect(url_for('home'))
        return render_template("login.html", error="Invalid Email/Password.")
    return render_template("login.html")

'''
Join us page

Page dedicated for users to join our platform by typing their information in and creating an account.
Users must provide the following information to initialize an account: first name, last name, email, 
date of birth, and password. The user profile and DB entry is created upon successful and validated completion.
'''
@app.route("/joinus", methods=['GET', 'POST'])
def joinus():
    # if user is logged in, redirect them to the home page
    if checkLoggedIn():
        return redirect(url_for('home'))
    # Initialize WTForms register form template
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            #on successful validation of field entries (dob is > 18 years ago, email is valid, password >= 8 characters, all fields filled)
            #initialize db user collections connection.
            users = mongo.db['_Users']
            #Query to see if an existing user already exists with their email
            existing_user = users.find_one({'email' : request.form['email']})
            #if there is no existing user, continue on, else return an error stating the problem.
            if existing_user is None:
                #On validation clear and no user existence, its time to create a new user entry in the db
                #Encode the password for security
                hashpass = generate_password_hash(form.password.data, method='sha256')
                #Update the users db with a new insertion containing all the information provided by the user.
                users.insert({'firstName' : request.form['firstName'].capitalize(),'lastName' : request.form['lastName'].capitalize(),'dob' : request.form['dob'],'email' : request.form['email'], 'password' : hashpass,'fillQuestions':True})
                #set the important session variables
                session['name'] = request.form['firstName'] + ' '+ request.form['lastName']
                session['email'] = request.form['email']
                # set the logged_in to true so that user doesn't need to re-log in
                session['logged_in'] = True
                session['portfolio']=None
                #require the user to fill the questionnaire according to the flag in the DB (which should be true at time of initialization)
                session['fillQuestions']=True
                #Redirect the user to function 3 to create their portfolio and start with us.
                return redirect(url_for('advisor'))
            return render_template("joinus.html",form=form,existing=True)
        return render_template("joinus.html",form=form)
    return render_template("joinus.html",form=form)


'''
Forgot/Reset Password

Page designed for users that forgot their password to be able to reset it. The user is required to enter the email 
associated with their account which we will then send a 6 digit randomly generated pin code. For added security,
we also encode the pin code when we store it in the user session so that it can persist safely and securely 
accross routing calls (GET/POST). If the user is who they say they are (by validation through pin), allow them to 
change and update their password in the db.
'''
@app.route("/forgotpass", methods=['GET','POST'])
def forgotpass(): 
    #note that logged in users are allowed to access this page.
    if request.method == 'POST':
        #manual validation since we opted out of using WTForms for generating these simple forms.
        #if there is an email typed in, continue to check stuff, else if there is a code(they were on the second page) continue
        if request.form.get('email')!=None:
            # Init user db collections connection
            users = mongo.db['_Users']
            #find the email that the user provided
            user = users.find_one({'email' : request.form['email']})
            #if there exists a user with the email provided, generate a pin and send it to them by email, else return error
            if user != None:
                #generate random pin by concating 6 strings from 0-9 together.
                pin = ''.join(random.choice('0123456789') for _ in range(6))
                #Encode the pin and store in the session variable for persistence accross GET/POST method calls.
                session['pin']=generate_password_hash(pin,method='sha256')
                #store user email in sessions variable for persistence accross GET/POST method calls.
                session['email']=request.form['email']
                #Generate user email to send through our resetpassword.html email template and send the email to the typed in users email
                msg = Message('AlphaFactory Password Reset Code.', sender='contact@alphafactory.ca', recipients=[session['email']])
                msg.html = render_template('resetpassword.html',code=pin)
                mail.send(msg)
                #return the next page of the forgot password (reset password) template
                return render_template("forgotpass.html",code=True)
            else:
                return render_template("forgotpass.html",code=None,error='No user with that email was found.')
        elif request.form.get('code')!=None:
            #if the pin the user inputed and the one that we have on session dont match, return error
            if not check_password_hash(session['pin'], request.form.get('code')):
                return render_template("forgotpass.html",code =True, error='Incorrect Code')
            #if the password is not at least 8 characters, return error
            elif len(request.form.get('password')) <8:
                return render_template("forgotpass.html",code =True, error='Your password must be at least 8 characters in length.')
            #if the passwords don't match, return an error
            elif request.form.get('password') != request.form.get('confirmpassword'):
                return render_template("forgotpass.html",code =True, error='Your passwords must match.')
            else:
                #If all validations are clear, update user password on db, reset session info, and take them to login page
                updateuserpassword(request.form.get('password'),session['email'])
                session.clear()
                return redirect(url_for('login'))
    return render_template("forgotpass.html",code=None)

'''
Update user password

Small helper/Util function to be used to update the user's password in the DB. 
Takes in new password and user email as the parameters and updates the assocaited user entry in the db.
'''
def updateuserpassword(password,email):
    users = mongo.db['_Users']
    user = users.find_one({'email' : email})
    user['password']= generate_password_hash(password, method='sha256')
    users.save(user)
'''
Questionnaire

Page is designed to contain all the questions for the risk assessment questionnaire on one page. All
questions are retrieved from the DB and shuffled in both order and option selection so that questions,
risk-averse and risk-seeking options aren't always in the same positions. A different method is called
on questionnaire completion through ajax that updates the user info in db and resets the flag. (see /check_questions)
'''
@app.route("/questions")
def questions():
    # if user is not logged in, redirect them to the log in page
    if not checkLoggedIn():
        return redirect(url_for('login'))
    # if user is has no portfolio or have not completed their previous process, send them back to function 3 to create a portfolio
    if session.get('portfolio')==None or session.get('finishedInit',True)==False:
        return redirect(url_for('advisor'))
    # only if user has their fillQuestions flag set to true should they see this page, else redirect to home page
    if session.get('fillQuestions') == True:
        #initialize questions collection db connection
        questionDB = mongo.db['_Questions']
        questions=[]
        # query for all the questions and individually append them to a questions list.     
        for q in questionDB.find({}):
            questions.append(q)
        #shuffle question order
        random.shuffle(questions)
        #render the questions through JS and display one by one through JS
        return render_template('questions.html',questions=questions)
    return redirect(url_for('home'))

'''
Check questions

Route defined only to check the output of the questionnaire page. Can only be accessed through a POST
method made through an ajax call. Takes in the integer risk-tolerance value as a json request and 
updates the user risk through a function that determines the risk profile and portfolio for each
user based on their portfolio time horizon and risk-tolerance number. (see updateuserrisk)
'''
@app.route('/check_questions', methods=['POST'])
def check():
    #make sure request is post
    if request.method == 'POST':
        # get the request as a json and convert it
	    risk = request.get_json()
    #send the risk number to the update user risk function with the 'selected' portfolio as None yet
    updateuserrisk(risk['risk'],None)
    #return success and continue to the portfolio selection process(done through js)
    return jsonify(success=True)

'''
Advisor page

Set up for users to be able to change their current active portfolios by creating a new portfolio. 
Takes in the user inital capital and time horizon for the portfolio and creates a portfolio object
to store under that user's entry in the db for later retrieval. 
'''
@app.route('/advisor', methods=['GET','POST'])
def advisor():
    #if the user is not logged in, send them to the log in page
    if not checkLoggedIn():
        return redirect(url_for('login'))
    #only if the user has either no portfolio or if they are making a new portfolio will they be able to continue.
    if session.get('portfolio')==None or session.get('newPortfolio',None)==True:
        if request.method == 'POST':
            #on form post:
            #get user db collections connection
            users = mongo.db['_Users']
            #query for the currently signed in user by email
            profile = users.find_one({'email' : session['email']})
            #if they don't currrently have a portfolio, create a new one with NO RISK as of yet (need to fill questionnaire and select portfolio)
            if profile.get('portfolio',None) == None:
                portfolio = {'initial':float(request.form['initial']),'horizon':int(request.form['horizon']),'dateCreated':datetime.datetime.now()}
            #if they currrently have a portfolio, create a new one with risk already assigned but required them to fill out questionnaire regardless
            else:
                portfolio = {'risk':profile['portfolio'].get('risk'),'initial':float(request.form['initial']),'horizon':int(request.form['horizon']),'dateCreated':datetime.datetime.now()}                
            #if they are making a new portfolio (advisor_options process instead of join us process), don't save the portfolio information
            #until the end of the process (post selection of portfolio)           
            if session.get('newPortfolio',None)!=True:
                profile['portfolio']=portfolio
                users.save(profile)
            else:
                # set the selection of their portfolio to None if they are creating a new one from the advisor_options process
                portfolio['risk']=None
            #save portfolio value in session and update flag to say that initialization of portfolio is complete
            session['portfolio']=portfolio
            session['finishedInit']=True
            #take them back to home which should redirect them to fill the questionnaire if they are making a new portfolio
            return redirect(url_for('home'))
        return render_template('advisor.html')
    return redirect(url_for('home'))

'''
Advisor Options

Dedicated to providing the user 3 options to manage their portfolio. They can currently either select a new portfolio type to hold,
create a brand new portfolio, or contact us regarding scheduling a meeting with an advisor.
'''
@app.route('/advisor_options', methods=['GET','POST'])
def advisor_options():
    #if the user is not logged in, send them to the log in page
    if not checkLoggedIn():
        return redirect(url_for('login'))
    #if the user is in a process to make a new portfolio, redirect them to the home page which will redirect them appropriately
    if session.get('newPortfolio')==True:
        return redirect(url_for('home'))
    if request.method == 'POST':
        #on user selection of option (through ajax call), retrieve user selection through json
        resp = request.get_json()
        #if user selected 'Change Portfolio' option, send them to the selection path. (update their portfolio type)
        if resp['selection']=='CP':
            return jsonify(success=True,path='selection')
        #if user selected 'Change Risk' option, send them to function 3 to generate a new protfolio and update the session variables
        #To indicate that the user is currently in a process.
        ## Note: the user can log out and log back in to hard exit this process
        if resp['selection']=='CR':
            #require user to initialize a portfolio
            session['finishedInit']=False
            # user is in a 'new portfolio' generation process
            session['newPortfolio']=True
            # user required to fill questionnaire again
            session['fillQuestions']=True
            #send them on the path of function 3 starting point
            return jsonify(success=True,path='advisor') 
        #if user selected 'Contact Advisor' option, send email to Alphafactory gmail with a request to schedule a
        # meeting on behalf of the client. (use their name and email)
        if resp['selection']=='CA':
            #Form message
            msg = Message('Request for meeting.', sender='contact@alphafactory.ca', recipients=['Alphafactory.capstone@gmail.com'])
            msg.body = """
            From: %s: <%s>
            Hello, I would like to schedule a meeting with an advisor.
            """ % (session.get('name'), session.get('email'))
            # attach name and email ^^ and send message
            mail.send(msg)
            #send them to the completed contact page
            return jsonify(success=True,path='contact_complete')   
    return render_template('advisor_page.html')

'''
Route created simply to reroute the user to the next page of the portfolio creation process after they have completed the
questionnaire. (called by changing window location through JS)
'''
@app.route('/questions/finished')
def finished():
    return redirect(url_for('selection'))

'''
Contact Completed

Simply renders the contact us page 'on completion' message informing the user that we have recieved their message
and we will be in contact shortly.
'''
@app.route('/contact_complete')
def contact_complete():
    return render_template('contactus.html', success="True")

'''
Selection

Page for allowing the user to select the portfolio type that they want. If they choose a selection different from their
risk profile, note it in the portfolio object and update the user db entry.
'''
@app.route('/selection', methods=['GET','POST'])
def selection():
    #if the previous steps have not been complete (no portfolio or risk profile assigned), return them to home page and redirect 
    # (applies for not logged in users as well)
    if session.get('riskProfile') == None or session.get('portfolio')==None:
        return redirect(url_for('home'))
    if request.method=='POST':
        # get the user portfolio selection
        resp = request.get_json()
        #get user from db
        users = mongo.db['_Users']
        profile = users.find_one({'email' : session['email']})
        # set the portfolio to the session portfolio (assigned in previous steps)
        profile['portfolio']=session['portfolio']
        #save the portfolio in this step if it hasn't been done already in the previous steps
        users.save(profile)
        #Update the user risk profile (through helper function) by setting the selection to the user selected profile.
        updateuserrisk(session.get('riskTolNum'),resp['selection'])
        # complete/finish and shut down any processes the user was on prior.
        session['finishedInit']=None
        session['newPortfolio']=None
        return jsonify(success=True)
    # on get (page rendering), retrieve portfolio stats (calculated and stored monthly on the db) and display portfolio stats for user selection
    portfolioStats = mongo.db['Portfolio_Stats']
    # only interested in CAGR, Volatility, and max drawdown.
    ps= pd.DataFrame(list(portfolioStats.find({"Stat":{ '$in' : [ "CAGR","Vol","Max DD"] }})))
    #drop extra columns
    ps=ps.drop(['_id','Stat'],axis=1)
    #sort the values by lowest return so that portfolio order displayed is preservation to aggressive from left to right
    ps=ps.sort_values(ps.first_valid_index(), axis=1)
    return render_template('selection.html',portfolio=session['portfolio'],recommendation=session['riskProfile'],recommended=ps[session['riskProfile']],ps=ps.drop(session['riskProfile'],axis=1))

'''
simple routing created soley for the purpose of redirecting the user home after they have completed the portfolio selection process.
'''
@app.route('/selection/finished')
def selection_complete():
    
    return redirect(url_for('home'))

'''
Auxilary/helper function
Takes in two parameters, risk as an integer number assigned from the questionnaire, and selected portfolio type
from the selection page and uses it to update the user entry in the DB.
'''
def updateuserrisk(risk,selected):
    #user is required to be logged in for this function to be called, can use their session email to acces their file on db
    users = mongo.db['_Users']
    login_user = users.find_one({'email' : session['email']})
    #time horizon of the portfolio
    horizon = session['portfolio']['horizon']
    if horizon>=15:
        #if they have a time horizon greater than 15 years, they are long term investors which have different tolerance levels
        riskProfile = riskDefnArr3[risk]
        tolerance = riskArr3[risk]
    elif horizon>=5:
        #if they have a time horizon greater than 5 years, they are middle term investors which have different tolerance levels
        riskProfile = riskDefnArr2[risk]
        tolerance = riskArr2[risk]
    else:
        #else, they are short term investors which have different tolerance levels
        riskProfile = riskDefnArr1[risk]
        tolerance = riskArr1[risk]
    #assign the user db object the associated risk number, profile, and tolerance 
    login_user['riskProfile'] = riskProfile
    login_user['riskTolNum']= risk
    login_user['riskTol'] = tolerance
    if selected:
        #if there is a selection of the portfolio, save the selected portfolio under the portfolio object
        #(no need to check for existence of portfolio object)
        login_user['portfolio']['risk']= selected
        session['portfolio']['risk']= selected
    #update session variables
    session['riskTol'] = tolerance
    session['riskProfile'] = riskProfile
    session['riskTolNum']= risk
    #required to flip the flag for fillQuestions to false since it is certain that they have completed the questionnaire in getting to this step
    login_user['fillQuestions']= False
    session['fillQuestions']=False
    if session.get('newPortfolio',None)!=True or selected:
        #if they aren't currently in a new process (or they have finally completed the full portfolio generation process), save the info to db
        #Note the importance of this step so that if a user leaves during a generation, they wont have corrupt or incomplete data.
        users.save(login_user)

'''
Base route

If the user access the site through the base url, check to see if they are logged in first. IF they are logged in,
direct them to their home page/dashboard, if they are not logged in, send them to the about page. 
'''
@app.route("/")
def landingpage():
    if session.get('logged_in') == None:
        session['name'] = None
        session['logged_in'] = None
        return redirect(url_for('about'))
    else:
        return redirect(url_for('home'))
'''
Error handler

Error page dedicated to handling errors in the url routing. If an error does occur (user tries to access nonexistent url extension),
an error message should pop up through the notfound.html and redirect them back to the home page.
'''
@app.errorhandler(404)
def page_not_found(error):
	return render_template('notfound.html')

if __name__ == '__main__':
    app.run(debug=True)
