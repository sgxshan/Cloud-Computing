from flask import render_template, g
from app import webapp
import mysql.connector
import boto3
from app.config import s3_config, db_config

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

def database():
    cnx = get_db()
    cursor = cnx.cursor()
    query = '''TRUNCATE TABLE images'''
    cursor.execute(query)
    query = '''TRUNCATE TABLE users'''
    cursor.execute(query)
    cnx.commit()

def s3():
    s3 = boto3.resource('s3')
    bucket_name = s3_config
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter():
        s3.Object(bucket.name, obj.key).delete()

@webapp.route('/delete',methods=['GET'])
def delete():
    database()
    s3()
    return render_template("account/function.html", msg = 'delete successfully!')




