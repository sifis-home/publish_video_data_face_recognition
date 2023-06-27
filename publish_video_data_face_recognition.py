# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 15:56:22 2022

@author: wisam
"""

import websocket
import time
import json
import os
import subprocess
import _thread
import rel
import re
import argparse
import platform
import datetime
import hashlib

parser = argparse.ArgumentParser(description='')
parser.add_argument('--file_name', help='File Name', required=True, type=str)
parser.add_argument('--database_path', help='database path', required=True, type=str)
parser.add_argument('--requestor_type', help='Requestor Type', required=True, type=str)
parser.add_argument('--privacy_parameter', help='privacy parameter', required=True, type=int)

args = parser.parse_args()
file_name = args.file_name
database_path = args.database_path
requestor_type = args.requestor_type
privacy_parameter = args.privacy_parameter

def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### Connection closed ###")


def on_open(ws):
    print("### Connection established ###")

def publish(file_name,database_path,requestor_type,privacy_parameter):
    requestor_id = platform.node()

    # Get current date and time
    now = datetime.datetime.now()

    # Generate a random hash using SHA-256 algorithm
    hash_object = hashlib.sha256()
    hash_object.update(bytes(str(now), 'utf-8'))
    hash_value = hash_object.hexdigest()

    # Concatenate the time and the hash
    request_id = str(requestor_id) + str(now) + hash_value
    request_id = re.sub('[^a-zA-Z0-9\n\.]', '', request_id).replace('\n', '').replace(' ', '')

    ws = websocket.WebSocketApp("ws://localhost:3000/ws",
                                on_open=on_open,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    
    
    ws_req = {
            "RequestPostTopicUUID": {
                "topic_name": "SIFIS:Privacy_Aware_Face_Recognition",
                "topic_uuid": "Face_Recognition",
                "value": {
                    "description": "Face Recognition",
                    "requestor_id": str(requestor_id),
                    "requestor_type": str(requestor_type),
                    "request_id": str(request_id),
                    "Type": "Video_file",
                    "file_name": str(file_name),
                    "database_path": str(database_path),
                    "privacy_parameter": int(privacy_parameter)
                }
            }
        }
    ws.send(json.dumps(ws_req))

publish(file_name,database_path,requestor_type,privacy_parameter)