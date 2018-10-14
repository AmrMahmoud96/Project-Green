from flask import Flask, render_template, url_for,request, flash, session,redirect
from forms import ContactForm, RegisterForm
from flask_mail import Mail,Message
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'alphadb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/myDB'

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
def template_test():
    return render_template('base.html', my_string="Wheeeee!", my_list=[0,1,2,3,4,5])

@app.route("/about")
def about():
    print(session)
    return render_template("about.html")

@app.route('/logout')
def logout():
    session['name'] = None
    session['logged_in'] = None
    return redirect(url_for('about'))
    
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


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'email' : request.form['email']})

        if login_user:
            if check_password_hash(login_user['password'], request.form['password']):
                session['name'] = login_user['firstName'] + ' '+ login_user['lastName']
                session['logged_in']= True
                return redirect(url_for('about'))
        return render_template("login.html", error="Invalid Email/Password.")
    return render_template("login.html")

@app.route("/joinus", methods=['GET', 'POST'])
def joinus():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            users = mongo.db.users
            existing_user = users.find_one({'email' : request.form['email']})
            if existing_user is None:
                hashpass = generate_password_hash(form.password.data, method='sha256')
                users.insert({'firstName' : request.form['firstName'].capitalize(),'lastName' : request.form['lastName'].capitalize(),'dob' : request.form['dob'],'email' : request.form['email'], 'password' : hashpass})
                session['name'] = request.form['firstName'] + ' '+ request.form['lastName']
                session['logged_in'] = True
                return redirect(url_for('about'))
            return render_template("joinus.html",form=form,existing=True)
        return render_template("joinus.html",form=form)
    return render_template("joinus.html",form=form)

@app.route("/forgotpass")
def forgotpass():
    return render_template("forgotpass.html")


@app.route("/")
def chart():
    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]
    return render_template('about.html', values=values, labels=labels, legend=legend)
@app.errorhandler(404)
def page_not_found(error):
	return render_template('notfound.html')

if __name__ == '__main__':
    app.run(debug=True)