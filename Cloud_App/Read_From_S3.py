import os

''' 
def s3listbuckets():
    os.environ['AWS_SHARED_CREDENTIALS_FILE']='./cred' 
    # Above line needs to be here before boto3 to ensure file is read
    import boto3
    s3 = boto3.resource('s3')
    bucketnames=[bucket.name for bucket in s3.buckets.all()]
    return ' '.join(bucketnames)

print(s3listbuckets())

''' 
import json
import boto3

# Rendereing the user selection of the system
s3_client = boto3.client("s3")
S3_BUCKET = 'M_database'
S3_PREFIX = 'prefix'

def lambda_handler(event, context):
    response = s3_client.list_objects_v2(
        Bucket=S3_BUCKET, Prefix=S3_PREFIX, StartAfter=S3_PREFIX,)
    s3_files = response["Contents"]
    for s3_file in s3_files:
        file_content = json.loads(s3_client.get_object(
            Bucket=S3_BUCKET, Key=s3_file["Key"])["Body"].read())
        #print(file_content)
        return doRender('Result.htm', {'AuditBlock': file_content})
