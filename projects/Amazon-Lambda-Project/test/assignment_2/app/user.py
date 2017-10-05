from flask import render_template, redirect, url_for, request, g
from app import webapp
import boto3
from app.config import s3_config
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def create_table():
    table = dynamodb.create_table(
        TableName='Movies',
        KeySchema=[
            {
                'AttributeName': 'year',
                'KeyType': 'HASH'  #Partition key
            },
            {
                'AttributeName': 'title',
                'KeyType': 'RANGE'  #Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'year',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'title',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )


@webapp.route('/login',methods=['GET','POST'])
def login():
    return render_template("user/login.html")

@webapp.route('/submit',methods=['POST','GET'])
def submit():
    table = dynamodb.Table('Users')
    login = request.form.get('username',"")
    password = request.form.get('password',"")
    error = False
    if login =="" or password == "":
        error = True
        error_msg = "Error, Please fill the form"
    if error:
        return render_template("user/login.html" , error_msg = error_msg)

    response = table.query(
        KeyConditionExpression=Key('Username').eq(login)
    )

    for i in response['Items']:
        pass_word = i['Password']
    data = response['Items']
    if pass_word != None:
        if password == pass_word:
            create_folder(login)
            #return render_template("Image/navigate.html", UserId = login)
            return redirect("http://54.226.181.175:5000/"+login)
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

@webapp.route('/create/save')
def user_create_save():
    # login = request.form.get('login')
    # pass_word = request.form.get('password')
    #conform_pass = request.form.get('password')
    table = dynamodb.Table('Users')
    username = request.args.get('login')
    password = request.args.get('password')
    error = False
    if login =="" or password == "":
        error = True
        error_msg = "Error, Please fill the form!"

    if error:
        return render_template("user/new.html", error_msg= error_msg)
    response = table.put_item(
       Item={
            'Username': username,
            'Password': password,
        }
    )

    # query = '''INSERT INTO users (login,password) VALUE (%s, %s)'''
    # try:
    #     cursor.execute(query,(login,password))
    #     cnx.commit()
    # except mysql.connector.errors.IntegrityError:
    #     error_msg = "Error, username exist!"
    #     return render_template("user/new.html",error_msg=error_msg)
    return redirect(url_for('login'))