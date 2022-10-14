import json
import random


def lambda_handler(event, context):
        
        # Getting the input for calculation from GAE 
        mean = float(event['key1'])
        std = float(event['key2'])
        len_of_price_history = int(event['key3'])
        num_of_shots = int(event['key4'])
        data_len = int(event['key5'])
        s3 = boto3.client('s3')
      
      	# Calculating the value at risk 
        for i in range(len_of_price_history, data_len): 
               # generate rather larger (simulated) series with same broad characteristics 
               simulated = [random.gauss(mean,std) for x in range(num_of_shots)]
               # sort, and pick 95% and 99% losses (not distinguishing any trading position)
               simulated.sort(reverse=True)
               var95 = simulated[int(len(simulated)*0.95)]
               var99 = simulated[int(len(simulated)*0.99)]
               #result.append([var95,var99])
               return (var95,var99) # so you can see what is being produced
        
        
        
	# Uploading the var95, var99, and user selection parameters 
	''
	try:
	       s3.upload_file(local_file, os.environ['M_database'], s3_file)
	       url = s3.generate_presigned_url(
		    ClientMethod='get_object',
		    Params={
		        'Bucket': os.environ['M_database'],
		        'Key': s3_file,
		        'var95': var95,
		        'var99': var99,
		        'mean' : mean,
		        'std': std,
		        'len_of_price_history': len_of_price_history,
		        'num_of_shots': num_of_shots,
		        'data_len': data_len
		    },
		    ExpiresIn=24 * 3600
		)

		print("Upload Successful", url)
		return url
	except FileNotFoundError:
		print("The file was not found")
		return None
	except NoCredentialsError:
		print("Credentials not available")
		return None       
               
       '''
        
  
