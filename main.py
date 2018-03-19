import boto3
import json

creds = {}
with open('aws.config.json') as f:
    creds = json.loads(f.read())

session = boto3.Session(
    aws_access_key_id = creds['access_key'],
    aws_secret_access_key = creds['secret']
)

s3 = session.resource('s3')
bucket = s3.Bucket(creds['bucket'])

filelog_meta = bucket.Object(creds['object_key']).get()
filelog = filelog_meta['Body'].read().decode('utf-8')

lines = filelog.split('\n')
for line in lines[0:10]:
    print line