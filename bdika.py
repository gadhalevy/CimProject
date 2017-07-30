__author__ = 'gadh'
from flask import Flask, render_template, request, redirect, jsonify, url_for
app = Flask(__name__)



@app.route('/',methods=['GET','POST'])
def nisuy():
    people=['gad','ritzia','li','adi','or']
    if request.method == 'POST':
        name=request.form.getlist('anashim')
        return redirect(url_for('stam',names=name))
    else:
        return render_template('bdika.html',people=people)

@app.route('/stam/<string:names>',methods=['GET','POST'])
def stam(names):
    if request.method == 'GET':
        return names

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)




