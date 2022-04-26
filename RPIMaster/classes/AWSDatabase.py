import boto3


class AWSDatabase:
    
    table_name = None
    database = None
    table = None
    client = None



    def __init__(self, table_name="ForestDataCollection"):
        self.table_name = table_name
        self.database = boto3.resource('dynamodb')
        self.table = self.database.Table(table_name)
        self.client = boto3.client('dynamodb')