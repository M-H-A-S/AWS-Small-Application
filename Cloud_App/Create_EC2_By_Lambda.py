import json
import boto3
def lambda_handler(event, context):

 # get the number of resources from GAE 
 number_of_resources = float(event['key1'])
 
 # Creation of EC2 Resources.
 for i in number_of_resources:
 
	 ec2 = boto3.resource('ec2', region_name='us-east-1')
	 instances=ec2.create_instances(ImageId='ami-04902260ca3d33422',
	 InstanceType='t2.micro', MinCount=1, MaxCount=number_of_resources)
	 for i in instances:
	 	i.wait_until_running()
	 	# Reload the instance attributes
	 	i.load()
	 	print(i.public_dns_name)
	 	instanceslist = [i.public_dns_name for i in instances]
	 return ("The EC2 resources are created and ready for analysis!")
	 
	 
	 

	
	
  




