from flask import Flask, render_template, url_for,request, flash
from forms import ContactForm
from flask_mail import Mail,Message
app = Flask(__name__)

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
    return render_template("about.html")
@app.route("/contactus",methods=['GET', 'POST'])
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


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/joinus")
def joinus():
    return render_template("joinus.html")

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