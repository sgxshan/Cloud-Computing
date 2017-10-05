import time
import boto3
from app import config
from datetime import datetime, timedelta
from operator import itemgetter
import mysql.connector
from app.config import db_config
id = 'i-0d947d944fb20cf06'

def connect_to_database():
    return mysql.connector.connect(user = db_config['user'],
                                   password = db_config['password'],
                                   host = db_config['host'],
                                   database = db_config['database'])

def get_db():

    db  = connect_to_database()
    return db

def fetch_parameter():
    parameter = []
    cnx = get_db()
    cursor = cnx.cursor()
    cursor.execute('''SELECT * FROM manager''')
    data = cursor.fetchall()
    for row in data:
         parameter.append(row)
    length = len(parameter)
    threshold_grow = parameter[length-1][1]
    threshold_shrink = parameter[length-1][2]
    ratio_grow = parameter[length-1][3]
    ratio_shrink = parameter[length-1][4]
    return threshold_grow, threshold_shrink, ratio_grow, ratio_shrink

def ec2_create():
    ec2 = boto3.resource('ec2')
    ec2.create_instances(ImageId=config.ami_id, MinCount=1, MaxCount=1, InstanceType='t2.small')

def ec2_stop(id):
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=[id]).stop()

def ec2_destroy(id):
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=[id]).terminate()

def create_register_first_instance():
    ec2 = boto3.resource('ec2')
    first_instance=ec2.create_instances(ImageId=config.ami_id,
                         MinCount=1,
                         MaxCount=1,
                         InstanceType='t2.micro')

    register_instance(first_instance[0].id)

def get_cpu_utilization(id):
    client = boto3.client('cloudwatch')
    metric_name = 'CPUUtilization'
    namespace = 'AWS/EC2'
    statistic = 'Average'  # could be Sum,Maximum,Minimum,SampleCount,Average

    cpu = client.get_metric_statistics(
        Period=300,
        StartTime=datetime.utcnow() - timedelta(minutes=60*60),
        EndTime=datetime.utcnow()- timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )
    datapoints = cpu['Datapoints']
    if(datapoints!=[]):
        last_datapoint = sorted(datapoints, key=itemgetter('Timestamp'))[-1]
        utilization = last_datapoint['Average']
        utilization = round((utilization/100.0), 2)
        print ("CPU Utilization %.2f" % utilization)
    return utilization

def grow_or_remove_instance(threshold_grow, threshold_shrink, ratio_grow, ratio_shrink):
    if get_cpu_utilization(id) > threshold_grow:
        resize_instance('HIGH',ratio_grow, ratio_shrink)
        print("High utilization, grow instances")
    if get_cpu_utilization(id) < threshold_shrink:
        resize_instance('LOW',ratio_grow, ratio_shrink)
        print("Low utilization, remove instances ")

def create_and_register_instance(num):
    ec2 = boto3.resource('ec2')
    print("Need add %d more instance" % num)
    for i in range(0, num):
        new_instances = ec2.create_instances(ImageId=config.ami_id,
                                            MinCount=1,
                                            MaxCount=1,
                                            InstanceType='t2.small',
                                            SecurityGroupIds=[
                                                'sg-21e0185e',
                                            ]
                                             )
        print("Add instance %s to load balancer" % new_instances[0].id)
        register_instance(new_instances[0].id)

def resize_instance(type,ratio_grow, ratio_shrink):
    ec2 = boto3.resource('ec2')
    state = 'running'
    instances = ec2.instances.filter(
        Filters = [{'Name': 'instance-state-name', 'Values': [state],}])
    count = 0
    for instance in instances:
        count += 1
    if count == 0:
        create_register_first_instance()
    if type == 'HIGH':
        if count != 0:
            numInstance = count
            print("%d instances is running now" % numInstance)
            create_and_register_instance(int((ratio_grow-1) *numInstance))
    else:
        state = 'running'
        numInstance = count
        if numInstance > 1:
            stopInstances('running', int(numInstance-(numInstance/ratio_shrink)))

def register_instance(instance_id):
    elb = boto3.client('elb')
    loadbalance_name = config.elb_config
    response = elb.register_instances_with_load_balancer(
        LoadBalancerName=loadbalance_name,
        Instances=[
            {
                'InstanceId': instance_id
            },
        ]
    )

def deregister_instance(instance_id):
    elb = boto3.client('elb')
    loadbalance_name = config.elb_config
    response = elb.deregister_instances_from_load_balancer(
        LoadBalancerName=loadbalance_name,
        Instances=[
            {
                'InstanceId': instance_id
            },
        ]
    )

def stopInstances(state, num_to_stop):
    print ("Need to stop %d instance " % num_to_stop)
    instance_list_1 = []
    instance_list_2 = []
    instance_list = []
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters = [{'Name': 'instance-state-name', 'Values': [state]}])
    for instance in instances:
        instance_list_1.append(instance.id)

    instances = ec2.instances.filter(Filters=[{'Name': 'image-id', 'Values': [config.ami_id]}])
    for instance in instances:
        instance_list_2.append(instance.id)

    for instance in instance_list_1:
        if instance in instance_list_2:
            instance_list.append(instance)

    number = 0
    for instance in instance_list:
        if number < num_to_stop:
            print("stop "+instance)
            ec2_stop(instance)
            deregister_instance(instance)
        number += 1

def auto_scaling():
    elb = boto3.client('elb')
    loadbalance_name = config.elb_config
    elb.register_instances_with_load_balancer(
        LoadBalancerName=loadbalance_name,
        Instances=[
            {
                'InstanceId': id
            },
        ]
    )

    while(1):
        threshold_grow, threshold_shrink, ratio_grow, ratio_shrink = fetch_parameter()
        grow_or_remove_instance(threshold_grow, threshold_shrink, ratio_grow, ratio_shrink)
        time.sleep(60)

auto_scaling()


