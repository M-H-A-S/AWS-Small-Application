import os

os.environ['AWS_SHARED_CREDENTIALS_FILE']='./cred'
# Above line needs to be here before boto3 to ensure cred file is read
# from the right place

import boto3
def User_Service_Select():
	
	service_type = str(event['st'])
	if service_type == 'EC2':
		# Set the user-data we need – use your endpoint
		user_data = """#!/bin/bash
		 	    wget https://var-s-350014.appspot.com/cacheavoid/setup.bash
		  	    bash setup.bash"""

		ec2 = boto3.resource('ec2', region_name='us-east-1')

		instances = ec2.create_instances(
		    ImageId = 'ami-0ed9277fb7eb570c9', # Amzn Lnx 2 AMI - Kernel 5.10
		    MinCount = 1,
		    MaxCount = 1,
		    InstanceType = 't2.micro',
		    KeyName = 'us-east-1kp', # Make sure you have the named us-east-1kp
		    SecurityGroups=['SSH'], # Make sure you have the named SSH
		    BlockDeviceMappings = # extra disk
		    [ {'DeviceName' : '/dev/sdf', 'Ebs' : { 'VolumeSize' : 10 } } ],
		    UserData=user_data # and user-data
		    )
		    
		# Wait for AWS to report instance(s) ready.
		for i in instances:
		    i.wait_until_running()
		    # Reload the instance attributes
		    i.load()
		    print(i.public_dns_name) # ec2 com address
		    # Should add checks here that e.g. hello.py or index.html is responding
		    
        else: 
        	lambda_Handler(event, context)
