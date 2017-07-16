from flask import request,g, render_template
import mysql.connector
from app import webapp
import boto3
from wand.image import Image
from app.config import s3_config, db_config
import os

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

@webapp.route('/test/FileUpload',methods=['GET','POST'])
def file_upload():
    if request.method == 'POST':
        userid = request.form.get("userID")
        password = request.form.get("password")

        # check if the post request has the file part
        if 'uploadedfile' not in request.files:
            return render_template("test.html")

        new_file = request.files['uploadedfile']

        # if user does not select file, browser also
        # submit a empty part without filename
        if new_file.filename == '':
            return 'Missing file name'
        fname = os.path.join('app/static',new_file.filename)
        new_file.save(fname)
        s3 = boto3.client('s3')
        bucket_name = s3_config
        cnx = get_db()
        cursor = cnx.cursor()
        cursor.execute('''SELECT password FROM users WHERE login = '%s' '''%(userid))
        pass_word = cursor.fetchone()
        cursor.execute('''SELECT id FROM users WHERE login ='%s' '''%(userid))
        user_id = cursor.fetchone()
        cnx.commit()
        if password == pass_word[0]:
            create_folder(user_id[0])
            UserId = user_id[0]
            filename = str(UserId) + '/' + new_file.filename
            with open(fname, "rb") as file_upload_s3:
                s3.upload_fileobj(file_upload_s3, bucket_name, filename)
            store_db(UserId, new_file.filename)
            img = Image(filename = fname)
            FileName = new_file.filename
            transform_1 =img.clone()
            transform_1.rotate(90)
            transform_name_1 = os.path.join('app/static',  'FirstTransform_' + FileName)
            transform_1.save(filename = transform_name_1)
            s3_upload = boto3.client('s3')
            s3_upload.upload_file(transform_name_1, bucket_name, str(UserId) + '/FirstTransform_' + FileName)

            transform_2 =img.clone()
            transform_2.rotate(180)
            transform_name_2 = os.path.join('app/static','SecondTransform_' + FileName)
            transform_2.save(filename = transform_name_2)
            s3_upload.upload_file(transform_name_2, bucket_name, str(UserId) + '/SecondTransform_' + FileName)

            transform_3 =img.clone()
            transform_3.rotate(300)
            transform_name_3 = os.path.join('app/static','ThirdTransform_' + FileName)
            transform_3.save(filename = transform_name_3)
            s3_upload.upload_file(transform_name_3, bucket_name, str(UserId) + '/ThirdTransform_' + FileName)
            # with open(transform_name_1, "rb") as file_upload_s3_trans1:
            #     s3.upload_fileobj(file_upload_s3_trans1, bucket_name, str(UserId) + '/First_Transform_' + filename)
            #
            # transform_2 =img.clone()
            # transform_2.rotate(180)
            # transform_name_2 = os.path.join('app/static','SecondTransform_' + FileName)
            # transform_2.save(filename = transform_name_2)
            # with open(transform_name_2, "rb") as file_upload_s3_trans2:
            #     s3.upload_fileobj(file_upload_s3_trans2, bucket_name, str(UserId) + '/Second_Transform_' + filename)
            #
            # transform_3 =img.clone()
            # transform_3.rotate(300)
            # transform_name_3 = os.path.join('app/static','ThirdTransform_' + FileName)
            # transform_3.save(filename = transform_name_3)
            # with open(transform_name_3, "rb") as file_upload_s3_trans3:
            #     s3.upload_fileobj(file_upload_s3_trans3, bucket_name, str(UserId) + '/Third_Transform_' + filename)
            return "success"
    else:
        return render_template("/test.html")

def store_db(UserId, filename):
    cnx = get_db()
    cursor = cnx.cursor()
    cursor.execute('''SELECT key1 FROM images WHERE userId ='%s' '''%(UserId))
    key_value  = cursor.fetchall()
    hit = 0
    for row in key_value:
        if row[0] == filename:
            hit = 1;
    if(not key_value or hit == 0 ):
        query = '''INSERT INTO images (userId, key1, key2, key3, key4) VALUE (%s, %s, %s, %s, %s)'''
        cursor.execute(query,(UserId, filename, 'FirstTransform_'+filename, 'SecondTransform_'+filename,'ThirdTransform_'+filename))
        cnx.commit()
    else:
        error_msg = 'Error, this picture already exists!'


def create_folder(UserId):
    s3 = boto3.resource('s3')
    bucket_name = s3_config
    bucket = s3.Bucket(bucket_name)
    folder_name = str(UserId) + '/'
    bucket.Object(folder_name).put()
