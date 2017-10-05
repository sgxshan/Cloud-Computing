from flask import render_template, redirect, url_for, request, g
from app import webapp
import boto3
import os
from app.config import s3_config
from boto3.dynamodb.conditions import Key

@webapp.route('/upload_<UserId>_', methods = ['GET','POST'])
def file_upload(UserId):
    return render_template("Image/upload.html",UserId = UserId)

@webapp.route('/navigate_<UserId>_<input_file>', methods = ['GET','POST'])
def navigate(UserId,input_file):
    return render_template("Image/navigate.html",UserId = UserId, input_file=input_file)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
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


@webapp.route('/Image/upload/<UserId>',methods=['POST'])
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

    table = dynamodb.Table('Images')
    response = table.put_item(
       Item={
            'UserId': UserId,
            'Image': new_file.filename,
        }
    )
    return render_template("Image/navigate.html", UserId=UserId)



    # cnx = get_db()
    # cursor = cnx.cursor()
    # cursor.execute('''SELECT key1 FROM images WHERE userId ='%s' '''%(UserId))
    # key_value  = cursor.fetchall()
    # hit = 0
    # for row in key_value:
    #     if row[0] == new_file.filename:
    #         hit = 1;
    # if(not key_value or hit == 0 ):
    #     query = '''INSERT INTO images (userId, key1, key2, key3, key4) VALUE (%s, %s, %s, %s, %s)'''
    #     cursor.execute(query,(UserId, new_file.filename, 'FirstTransform_'+new_file.filename, 'SecondTransform_'+new_file.filename,'ThirdTransform_'+new_file.filename))
    #     cnx.commit()
    # else:
    #     error_msg = 'Error, this picture already exists!'
    #     return render_template("Image/upload.html",error_msg=error_msg, UserId = UserId)
    #return redirect(url_for('img_display', UserId = UserId))

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

@webapp.route('/Img_display<UserId>_<Input_File>', methods = ['POST','GET'])
def img_display(UserId,Input_File):
    folder = 'style'
    all_file = file_list(folder)
    s3_client = boto3.client ('s3')
    bucket_name = s3_config
    file_path = []
    work_name = []
    for FileName in all_file:
        file_name = os.path.join('app/static', FileName)
        s3_client.download_file(bucket_name, folder + '/' + FileName, file_name)
        file_path.append(file_name[4:])
        work_name.append(os.path.splitext(FileName)[0])
    return render_template("Image/feature.html", file = file_path, name=work_name, original=Input_File)


#
@webapp.route('/Image_Select_<UserId>', methods = ['POST','GET'])
def img_select(UserId):
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
        file_path.append(file_name[4:])
    return render_template("Image/original.html", file = file_path, UserId = UserId)


@webapp.route('/classification_<UserId>_<file>', methods = ['POST','GET'])
def classification(UserId,file):
    # record = {
    #     "s3": [
    #         {
    #             "object": {
    #                 "key": "shanxin/Eiffel.jpg",
    #             },
    #             "bucket": {
    #                 "name": "ece1779-project",
    #             },
    #         }]
    # }
    print (file)
    rekognition = boto3.client('rekognition')
    bucket = "ece1779-project"
    key = UserId+"/"+file

    # bucket = record['s3'][0]['bucket']['name']
    # key = urllib.unquote_plus(record['s3'][0]['object']['key'].encode('utf8'))
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    # print response['Labels']
    probability = []
    name = []
    max_index=0
    max = 0
    for i in response['Labels']:
        probability.append(i['Confidence'])
        name.append(i['Name'])
    for j in range(0,len(probability)):
        if (probability[j]>=max):
            max=probability[j]
            max_index = j
    msg = "Maximum probability to be %s, "%name[max_index] + "with possibility: %s"%probability[max_index]
    file_path = 'static/'+file
    return render_template("Image/predict.html", probability = probability, name=name, f= file_path,msg=msg)

#
# @webapp.route('/img_transform<id>_<FileName>',methods=['GET'])
# def image_transform(id,FileName):
#     UserId = id
#     bucket_name = s3_config
#     file_name = os.path.join('app/static',FileName)
#     img = Image(filename = file_name)
#     transform_1 =img.clone()
#     transform_1.rotate(90)
#     transform_name_1 = os.path.join('app/static',  'FirstTransform_' + FileName)
#     transform_1.save(filename = transform_name_1)
#     s3_upload = boto3.client('s3')
#     s3_upload.upload_file(transform_name_1, bucket_name, str(UserId) + '/FirstTransform_' + FileName)
#
#     transform_2 =img.clone()
#     transform_2.rotate(180)
#     transform_name_2 = os.path.join('app/static','SecondTransform_' + FileName)
#     transform_2.save(filename = transform_name_2)
#     s3_upload.upload_file(transform_name_2, bucket_name, str(UserId) + '/SecondTransform_' + FileName)
#
#     transform_3 =img.clone()
#     transform_3.rotate(300)
#     transform_name_3 = os.path.join('app/static','ThirdTransform_' + FileName)
#     transform_3.save(filename = transform_name_3)
#     s3_upload.upload_file(transform_name_3, bucket_name, str(UserId) + '/ThirdTransform_' + FileName)
#     return render_template("Image/view.html", f1 = file_name[4:],
#                                              f2 = transform_name_1[4:],
#                                              f3 = transform_name_2[4:],
#                                              f4 = transform_name_3[4:])
