from flask import render_template, redirect, url_for, request,g
from app import webapp
import boto3
import mysql.connector
from app import config
from datetime import datetime, timedelta
from operator import itemgetter
from app.config import db_config
id = 'i-02e07a29d536460de'


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


@webapp.route('/manage',methods=['GET'])
# Display an HTML list of all ec2 instances
def ec2_list():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=[{'Name': 'image-id', 'Values': [config.ami_id]}])
    return render_template("ec2_manage/list.html",title="EC2 Instances",instances=instances)

@webapp.route('/ec2_examples/<id>',methods=['GET'])
#Display details about a specific instance.
def ec2_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'

    namespace = 'AWS/EC2'
    statistic = 'Average'                   # could be Sum,Maximum,Minimum,SampleCount,Average



    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    cpu_stats = []


    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))


    statistic = 'Sum'  # could be Sum,Maximum,Minimum,SampleCount,Average

    network_in = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkIn',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    net_in_stats = []

    for point in network_in['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_in_stats.append([time,point['Sum']])

    net_in_stats = sorted(net_in_stats, key=itemgetter(0))



    network_out = client.get_metric_statistics(
        Period=5 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkOut',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )


    net_out_stats = []

    for point in network_out['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_out_stats.append([time,point['Sum']])

        net_out_stats = sorted(net_out_stats, key=itemgetter(0))


    return render_template("ec2_manage/view.html",title="Instance Info",
                           instance=instance,
                           cpu_stats=cpu_stats,
                           net_in_stats=net_in_stats,
                           net_out_stats=net_out_stats)


@webapp.route('/ec2_manage/create',methods=['GET', 'POST'])
# Start a new EC2 instance
def ec2_create():

    ec2 = boto3.resource('ec2')

    ec2.create_instances(ImageId=config.ami_id,
                         MinCount=1,
                         MaxCount=1,
                         InstanceType='t2.small')

    return redirect(url_for('ec2_list'))

@webapp.route('/ec2_manage/stop/<id>',methods=['POST'])
# Terminate a EC2 instance
def ec2_stop(id):
    # create connection to ec2
    ec2 = boto3.resource('ec2')

    ec2.instances.filter(InstanceIds=[id]).stop()

    return redirect(url_for('ec2_list'))


def ec2stop(id):
    # create connection to ec2
    ec2 = boto3.resource('ec2')

    ec2.instances.filter(InstanceIds=[id]).stop()

    return redirect(url_for('ec2_list'))

@webapp.route('/ec2_manage/delete/<id>',methods=['POST'])
# Terminate a EC2 instance
def ec2_destroy(id):
    # create connection to ec2
    ec2 = boto3.resource('ec2')

    ec2.instances.filter(InstanceIds=[id]).terminate()

    return redirect(url_for('ec2_list'))

@webapp.route('/parameter', methods = ['GET','POST'])
def parameter():
    return render_template("ec2_manage/parameter.html")


@webapp.route('/auto_scaling', methods = ['POST'])
def auto_scaling():
    threshold_grow = request.form.get("threshold_grow","")
    threshold_shrink = request.form.get("threshold_shrink","")
    ratio_grow = request.form.get("ratio_grow","")
    ratio_shrink = request.form.get("ratio_shrink","")
    cnx = get_db()
    cursor = cnx.cursor()
    query = '''INSERT INTO manager (threshold_grow, threshold_shrink, ratio_grow, ratio_shrink) VALUE (%s, %s, %s, %s)'''
    try:
        cursor.execute(query, (threshold_grow, threshold_shrink, ratio_grow, ratio_shrink))
        cnx.commit()
    except mysql.connector.errors.IntegrityError:
        error_msg = "Error, Please fill the form"
        return render_template("ec2_manage/list.html",error_msg=error_msg)
    return redirect(url_for('ec2_list'))




