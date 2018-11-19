from flask import Flask, render_template
import pandas as pd
import numpy as np

sandpfile='^GSPC (2).csv'
vixfile= '^GSPTSE.csv'
tableS= pd.read_csv(sandpfile)
tableV = pd.read_csv(vixfile)

app = Flask(__name__)


@app.route("/")
def template_test():
    return render_template('hello.html', my_string="Wheeeee!", my_list=[0,1,2,3,4,5])
 
@app.route("/simple_chart")
def chart():
    labels = tableV['Date'].values.tolist()
    a = tableS['Close'].values
    b = tableV['Close'].values
    ocolumn_divs = (a/a[0])*10000
    tcolumn_divs = (b/b[0])*10000
    return render_template('chart.html', tvalues=tcolumn_divs.tolist(), ovalues=ocolumn_divs.tolist(), labels=labels)
 

if __name__ == '__main__':
    app.run(debug=True)