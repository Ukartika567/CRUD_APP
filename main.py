from io import BytesIO
from logging import debug
from flask import Flask, render_template, redirect, flash, session
from flask.globals import request
from flask.helpers import send_file, url_for
from flask_sqlalchemy import SQLAlchemy
import json
from werkzeug.utils import secure_filename
import os

with open('config.json', 'r') as f:
    params=json.load(f)['params']

local_server=True
app=Flask(__name__)
app.config['SECRET_KEY']="pythoncoder"
app.config['UPLOAD_FOLDER']=params['upload_location']
app.config['MAX_CONTENT_LENGTH']=16 * 1024 * 1024

ALLOWED_EXTENSIONS=set(['jpg','jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI']=params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI']=params['prod_uri']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    
db=SQLAlchemy(app)




class Employeelist(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    emp_name=db.Column(db.String(80), nullable=False)
    img_file=db.Column(db.String(50), nullable=False, default='default.jpg')
    emp_email=db.Column(db.String(80), nullable=True)
    emp_phone=db.Column(db.String(80), nullable=False)
    

@app.route('/')
def home():
    emplists=Employeelist.query.filter_by().all()
    return render_template('index.html', params=params, emplists=emplists)

@app.route('/insert', methods=['GET','POST'])
def addemp():
    if request.method=='POST':
        empname=request.form.get('name')
        empemail=request.form.get('email')
        empphone=request.form.get('phone')
        file=request.files['image_file']
        filename=secure_filename(file.filename)

        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            emps=Employeelist(emp_name=empname, img_file=file.filename , emp_email=empemail, emp_phone=empphone)
            db.session.add(emps)
            db.session.commit()
            flash('Successfully added!')
            return redirect('/')
    return render_template('index.html', params=params)    
        

@app.route('/update', methods = ['GET', 'POST'])
def update():

    if request.method == 'POST':
        my_data = Employeelist.query.get(request.form.get('sno'))
        my_data.emp_name = request.form['name']
        my_data.emp_email = request.form['email']
        my_data.emp_phone = request.form['phone']
        file=request.files['image_file']
        filename=secure_filename(file.filename)
        my_data.img_file=file.filename

        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            db.session.commit()
            flash("Employee Updated Successfully!")
            return redirect('/')
        
    return render_template('index.html', params=params)    


@app.route('/delete/<string:sno>', methods=['GET','POST'])
def delete(sno):
    emp_del=Employeelist.query.filter_by(sno=sno).first()
    db.session.delete(emp_del)
    db.session.commit()
    flash('Employee deleted successfully!')
    return redirect('/')


app.run(debug=True)
