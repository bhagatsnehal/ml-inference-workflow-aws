### serializeImageData
# Serialized the image input


###########################################################################################################
import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']

    # Download the data from s3 to /tmp/image.png
    with open('/tmp/image.png', 'wb') as f:
        s3.download_fileobj(bucket, key, f)

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }
###########################################################################################################


### classfiyImageData
# Runs the predictions to classify the image input

###########################################################################################################
import json
import base64
import boto3
import ast

runtime = boto3.client('runtime.sagemaker')
# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2022-02-15-18-12-13-227'

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['image_data'])

    # Make a prediction:
    inferences = runtime.invoke_endpoint(EndpointName=ENDPOINT,
                                               ContentType='image/png',
                                               Body=image)
    # We return the data back to the Step Function    
    #event["inferences"] = inferences['Body'].read().decode("utf-8")
    return {
        'statusCode': 200,
        'body': {
            "inferences": ast.literal_eval(inferences['Body'].read().decode("utf-8"))
        }
    }
###########################################################################################################


### inferenceFilter
# Determine success or failure based on a set threshold for the inference values

###########################################################################################################
import json


THRESHOLD = .93


def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event['inferences']
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = [True for x in inferences if x > THRESHOLD]


    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        event["pass"] = "Pass"
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': {
            "inferences": inferences,
            "pass": "Pass"
        }
    }

###########################################################################################################
