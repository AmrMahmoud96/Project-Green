from flask import Flask, render_template, url_for
app = Flask(__name__)


@app.route("/simple_chart")
def template_test():
    return render_template('base.html', my_string="Wheeeee!", my_list=[0,1,2,3,4,5])

@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/contactus")
def contactus():
    return render_template("contactus.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/joinus")
def joinus():
    return render_template("joinus.html")

@app.route("/")
def chart():
    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]
    return render_template('chart.html', values=values, labels=labels, legend=legend)
@app.errorhandler(404)
def page_not_found(error):
	return render_template('notfound.html')

if __name__ == '__main__':
    app.run(debug=True)