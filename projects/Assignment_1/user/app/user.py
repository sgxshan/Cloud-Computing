from flask import render_template, redirect, url_for, request, g
from app import webapp
import mysql.connector
import boto3
from app.config import s3_config
from app.config import db_config
def connect_to_database():
    return mysql.connector.connect(user = db_config['user'],
                                   password = db_config['password'],
                                   host = db_config['host'],
                                   database = db_config['database'])
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@webapp.route('/login',methods=['GET','POST'])
def login():
    return render_template("user/login.html")

@webapp.route('/submit',methods=['POST'])
def submit():
    login = request.form.get('username',"")
    password = request.form.get('password',"")
    error = False
    if login =="" or password == "":
        error = True
        error_msg = "Error, Please fill the form"
    if error:
        return render_template("user/login.html" , error_msg = error_msg)
    cnx = get_db()
    cursor = cnx.cursor()
    cursor.execute('''SELECT password FROM users WHERE login = '%s' '''%(login))
    pass_word = cursor.fetchone()
    cursor.execute('''SELECT id FROM users WHERE login ='%s' '''%(login))
    user_id = cursor.fetchone()
    cnx.commit()
    if pass_word != None:
        if password == pass_word[0]:
            create_folder(user_id[0])
            return render_template("Image/upload.html", UserId = user_id[0])
        else:
            error_msg = "Error!, incorrect password!"
            return render_template("user/login.html" , error_msg = error_msg)
    else:
        error_msg = "Error! Invalid username!"
        return render_template("user/login.html" , error_msg = error_msg)

#define a function to create folder in bucket
def create_folder(UserId):
    s3 = boto3.resource('s3')
    bucket_name = s3_config
    bucket = s3.Bucket(bucket_name)
    folder_name = str(UserId) + '/'
    bucket.Object(folder_name).put()

@webapp.route('/create', methods = ['GET','POST'])
def user_create():
    return render_template("user/new.html")

@webapp.route('/create/save', methods = ['POST'])
def user_create_save():

    login = request.form.get('login')
    password = request.form.get('password')
    conform_pass = request.form.get('conform_password')
    error = False
    if login =="" or password == "":
        error = True
        error_msg = "Error, Please fill the form!"

    if password != conform_pass:
        error = True
        error_msg = "Error, password is not consistent!"

    if error:
        return render_template("user/new.html", error_msg= error_msg)
    cnx = get_db()
    cursor = cnx.cursor()
    query = '''INSERT INTO users (login,password) VALUE (%s, %s)'''
    try:
        cursor.execute(query,(login,password))
        cnx.commit()
    except mysql.connector.errors.IntegrityError:
        error_msg = "Error, username exist!"
        return render_template("user/new.html",error_msg=error_msg)
    return redirect(url_for('login'))