import os
import sys
import random
from datetime import datetime
import time
import boto3
import threading


class AWSDatabase():

    def __init__(self, table_name):
        self._table_name = table_name

        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table(table_name)
        self.client = boto3.client('dynamodb')


    def put(self, node_id='', Temperature='', Humidity='', Moisture='', Pressure='', Light='', Latitude='', Longitude=''):
        self.table.put_item(
            Item={
                'node_id': node_id,
                'timestamp': int(datetime.now().timestamp()),
                'Temperature': Temperature,
                'Humidity': Humidity,
		'Moisture': Moisture,
		'Pressure': Pressure,
		'Light': Light,
                'Latitude': Latitude,
                'Longitude': Longitude
            }
        )
