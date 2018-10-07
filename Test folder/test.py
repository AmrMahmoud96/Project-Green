from flask import Flask, render_template
app = Flask(__name__)


@app.route("/")
def template_test():
    return render_template('hello.html', my_string="Wheeeee!", my_list=[0,1,2,3,4,5])
 
@app.route("/simple_chart")
def chart():
    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]
    return render_template('chart.html', values=values, labels=labels, legend=legend)
 

if __name__ == '__main__':
    app.run(debug=True)