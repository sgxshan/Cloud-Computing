from flask import render_template, redirect, url_for, request, g
from app import webapp
import boto3
import mysql.connector
from wand.image import Image
import os
from app.config import db_config, s3_config


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

@webapp.route('/user/s3_view/<UserId>',methods=['GET','POST'])
#Display details about a specific bucket.
def s3_view(UserId):
    s3 = boto3.resource('s3')
    bucket_name = s3_config
    bucket = s3.Bucket(bucket_name)
    folder_name = str(UserId) + '/'
    bucket.Object(folder_name).put()
    name = []
    for key in bucket.objects.all():
        name.append(key.key)
    keys =  bucket.objects.all()
    return render_template("Image/upload.html",title="S3 Bucket Contents", UserId = UserId, keys=keys)


@webapp.route('/Image/upload/<int:UserId>',methods=['POST'])
#upload file in s3
def upload(UserId):
    # check if the post request has the file part
    if 'new_file' not in request.files:
        return redirect(url_for('s3_view',UserId = UserId))
    new_file = request.files['new_file']

    if new_file.filename == '':
        return redirect(url_for('s3_view', UserId=UserId))
    s3 = boto3.client('s3')
    bucket_name = s3_config
    filename = str(UserId) + '/' + new_file.filename
    s3.upload_fileobj(new_file, bucket_name, filename)
    cnx = get_db()
    cursor = cnx.cursor()
    cursor.execute('''SELECT key1 FROM images WHERE userId ='%s' '''%(UserId))
    key_value  = cursor.fetchall()
    hit = 0
    for row in key_value:
        if row[0] == new_file.filename:
            hit = 1;
    if(not key_value or hit == 0 ):
        query = '''INSERT INTO images (userId, key1, key2, key3, key4) VALUE (%s, %s, %s, %s, %s)'''
        cursor.execute(query,(UserId, new_file.filename, 'FirstTransform_'+new_file.filename, 'SecondTransform_'+new_file.filename,'ThirdTransform_'+new_file.filename))
        cnx.commit()
    else:
        error_msg = 'Error, this picture already exists!'
        return render_template("Image/upload.html",error_msg=error_msg, UserId = UserId)
    return redirect(url_for('img_display', UserId = UserId))

#define a function to fine the filename
def file_list(UserId):
    s3 = boto3.resource('s3')
    bucket_name = s3_config
    bucket = s3.Bucket(bucket_name)
    name = []
    for file in bucket.objects.filter(Prefix = str(UserId)+'/'):
        if file.key != str(UserId) + '/':
            temp_name = file.key.split('/')
            name.append(temp_name[1])
    return name


@webapp.route('/Image<int:UserId>', methods = ['POST','GET'])
def img_display(UserId):
    all_file = file_list(UserId)
    s3_client = boto3.client ('s3')
    bucket_name = s3_config
    file_path = []
    if not all_file:
        error_msg = "No image, please upload first!"
        return render_template("Image/upload.html",error_msg=error_msg, UserId = UserId)
    for FileName in all_file:
        file_name = os.path.join('app/static',FileName)
        s3_client.download_file(bucket_name, str(UserId) + '/'  + FileName, file_name)
        img = Image(filename = file_name)
        thumb_nail = img.clone()
        thumb_nail_name = os.path.join('app/static','thumb_nail_' + FileName)
        thumb_nail.resize(150,150)
        thumb_nail.save(filename = thumb_nail_name)
        file_path.append(thumb_nail_name[4:])
    return render_template("Image/OriginalView.html", file = file_path, UserId = UserId)


@webapp.route('/img_transform<int:id>_<FileName>',methods=['GET'])
def image_transform(id,FileName):
    UserId = id
    bucket_name = s3_config
    file_name = os.path.join('app/static',FileName)
    img = Image(filename = file_name)
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
    return render_template("Image/view.html", f1 = file_name[4:],
                                             f2 = transform_name_1[4:],
                                             f3 = transform_name_2[4:],
                                             f4 = transform_name_3[4:])
