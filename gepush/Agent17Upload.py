'''
/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import logging
import time
import argparse
import json
import boto3
import uuid
import os
import threading


def s3_tag_generator(metadata):

	tags = '' 

	for key in metadata.keys():
		tags += key + '=' + metadata[key] + '&'

	tags = tags[:-1]

	logger.debug( "tags %s ",tags)

	return tags

# Custom MQTT message callback
def ping_callback(client, userdata, message):

	logger.debug( "Received a new message: %s", message.payload )

	logger.debug( "Hellloooo")


def terminate_agent17():
	global terminate_flag
	logger.debug( "Shutting down agent17 after downloading the files.")
	terminate_flag = True


# Custom MQTT message callback
def upload_callback(client, userdata, message):

	logger.debug( "Received a new message: %s",message.payload)

	logger.debug("input directory is %s ",input_directory)

	msg = json.loads(message.payload.decode())


	s3_bucket = msg['params']['token']['bucket']
	space_id = msg['params']['token']['key']
	try:
		session = boto3.session.Session(aws_access_key_id=msg['params']['token']['accessKey'], aws_secret_access_key=msg['params']['token']['secretKey'], aws_session_token=msg['params']['token']['sessionToken'], region_name=msg['params']['token']['region'])
		s3 = session.client('s3')
		tags = s3_tag_generator(metadata)
		kms_key = msg['params']['token']['kmsKey']
		if os.path.isfile(input_directory):
			print("started uploading ", input_directory)
			s3_path = space_id + '/'+ os.path.basename(input_directory)
			res = s3.put_object(Body=input_directory, Bucket=s3_bucket, ServerSideEncryption='aws:kms', SSEKMSKeyId=kms_key, Key=s3_path, Tagging=tags, ContentType=content_type)
			logger.debug( str(res))
			print("file uploaded to ",s3_path)
		else:
			for root, dirs, files in os.walk(input_directory):
				for filename in files:
					print("started uploading ", filename)
					local_path = os.path.join(root, filename)
					logger.debug( "local_path %s ", local_path)
					relative_path = os.path.relpath(local_path, input_directory)
					logger.debug( "relative_path %s ", relative_path)
					s3_path = os.path.join(space_id, relative_path)
					logger.debug( "s3_path %s ", s3_path)
					res = s3.put_object(Body=local_path, Bucket=s3_bucket, ServerSideEncryption='aws:kms', SSEKMSKeyId=kms_key, Key=s3_path, Tagging=tags, ContentType=content_type)
					logger.debug(str(res))
					print(filename, "uploaded to s3.")
			print("files uploaded to ", space_id) 
	except Exception as e:
		logger.error(str(e))

	time.sleep(2)

	terminate_agent17()
	
	

# Configure logging

logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.ERROR)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)



# Read in command-line parameters
parser = argparse.ArgumentParser()

parser.add_argument("-c", "--config", action="store", required=True, dest="config", help="Device Config file")
parser.add_argument("-i", "--input", action="store", required=True, dest="input_directory", help="Input directory which has file for uploading to healthcloud")
parser.add_argument("-p", "--prefix", action="store", required=False, dest="prefix", help="upload prefix")
parser.add_argument("-t", "--contentType", action="store", required=True, dest="content_type" , help="Contnet Type for the files. Please refer http://www.iana.org/assignments/media-types/media-types.xhtml")
parser.add_argument("-m", "--metadata", action="store", required=False, dest="meta_data", type=json.loads , help="Meta data for cataloging as dict")

args,unknown = parser.parse_known_args()


config_file = args.config

input_directory = args.input_directory

content_type = args.content_type

prefix = args.prefix


global terminate_flag

terminate_flag = False

device_config = {}

with open(config_file, 'r') as f:
	device_config = json.load(f)

logger.debug( "device_config is %s ", json.dumps(device_config))

host = device_config['endpoint']
rootCAPath = device_config['rootCertificate']
certificatePath = device_config['deviceCertificate']
privateKeyPath = device_config['devicePrivateKey']
device_id = device_config['id']
thing_name =  device_config['thingName']
metadata = device_config['metadata']


if args.meta_data is not None:
	logger.debug( "Metatda is not none")
	metadata_new = metadata.copy()
	metadata_new.update(args.meta_data)
	metadata = metadata_new.copy()


logger.debug( "Metadata is %s ", str(metadata))



# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None

myAWSIoTMQTTClient = AWSIoTMQTTClient(device_id)
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()


request_topic = 'gehc/request/'

request_body = {}

request_id = str(uuid.uuid4())

request_body['requestId'] = request_id
request_body['action'] = 'UPLOAD_TOKEN_REQUEST'
request_body['params'] = {'input_directory':input_directory,'metadata':metadata}

if prefix:
	request_body['params']['prefix'] = prefix

logger.debug("Upload request is %s",request_body)

response_topic = 'gehc/response/' + device_id + '/' + request_id + '/'

logger.debug( "response topic is %s", response_topic)

ping_request_topic = 'gehc/ping/'
ping_response_topic = 'gehc/pong/' + device_id + '/'

myAWSIoTMQTTClient.subscribe(str(ping_response_topic), 1, ping_callback)

myAWSIoTMQTTClient.subscribe(str(response_topic), 0, upload_callback)

time.sleep(2)

myAWSIoTMQTTClient.publish(ping_request_topic, json.dumps({"message":"hello"}), 1)

elapsed_time = 0
myAWSIoTMQTTClient.publish(request_topic, json.dumps(request_body), 1)
while not terminate_flag :
	time.sleep(5)
	elapsed_time += 5
	logger.debug( "elapsed  %s secs", elapsed_time )
	#break
sys.exit(0)
