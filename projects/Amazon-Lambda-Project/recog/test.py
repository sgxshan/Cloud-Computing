import boto3

import urllib
import json
def test():
	rekognition = boto3.client('rekognition')
	bucket = "ece1779-project"
	key = "shanxin/fox.jpg"
	response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})
	#print response['Labels']
	a = []
	b = []
	for i in response['Labels']:
		a.append(i['Confidence'])
		b.append(i['Name'])
	print a[0]




def lambda_handler():
	s3 = boto3.client('s3')
	#print("Received event: " + json.dumps(event, indent=2))
	#Get the object from the event and show its content type
    #bucket = event['Records'][0]['s3']['bucket']['name']
    #key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
	bucket = 'ece1779-project'
	key = 'shanxin/fox.jpg'
	#try:
	response = s3.get_object(Bucket=bucket, Key=key)
	print (response)
	print("CONTENT TYPE: " + response['ContentType'])
	return response['ContentType']
    # except Exception as e:
    #     print(e)
    #     print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
    #     raise e


event={
  "Records": [
    {
      "eventVersion": "2.0",
      "eventTime": "1970-01-01T00:00:00.000Z",
      "requestParameters": {
        "sourceIPAddress": "127.0.0.1"
      },
      "s3": {
        "configurationId": "testConfigRule",
        "object": {
          "eTag": "0123456789abcdef0123456789abcdef",
          "sequencer": "0A1B2C3D4E5F678901",
          "key": "HappyFace.jpg",
          "size": 1024
        },
        "bucket": {
          "arn": "arn:aws:s3:::mybucket",
          "name": "roeyg-oregon-s3-bucket",
          "ownerIdentity": {
            "principalId": "EXAMPLE"
          }
        },
        "s3SchemaVersion": "1.0"
      },
      "responseElements": {
        "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH",
        "x-amz-request-id": "EXAMPLE123456789"
      },
      "awsRegion": "us-east-1",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "EXAMPLE"
      },
      "eventSource": "aws:s3"
    }
  ]
}

record = {
	"s3": [
		{
			"object": {
				"key": "shanxin/coke.jpg",
			},
			"bucket": {
				"name": "ece1779-project",
			},
		}]
}

rekognition = boto3.client('rekognition')
# bucket = "ece1779-project"
# key = "shanxin/fox.jpg"
key = urllib.unquote_plus(record['s3'][0]['object']['key'].encode('utf8'))
bucket = record['s3'][0]['bucket']['name']
#key = record['s3'][0]['object']['key']

print bucket
print key
#test()
#lambda_handler()
