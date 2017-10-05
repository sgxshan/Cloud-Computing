from flask import render_template, redirect, url_for, request
from app import webapp
@webapp.route('/login',methods=['GET','POST'])
def login():
    return render_template("account/login.html")


@webapp.route('/submit',methods=['POST'])
def submit():
    login = request.form.get('username',"")
    password = request.form.get('password',"")
    error = False
    if login =="" or password == "":
        error = True
        error_msg = "Error, Please fill the form"
    if error:
        return render_template("account/login.html" , error_msg = error_msg)

    if login == 'admin' and password == 'ece1779':
        return render_template("account/function.html")
    else:
        error_msg = "Error!, incorrect password!"
        return render_template("account/login.html" , error_msg = error_msg)