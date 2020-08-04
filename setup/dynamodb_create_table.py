import boto3
import time
import sys
import os
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from config import Config

def create_table(table_name, dynamodb=None):
    client = boto3.client('dynamodb')

    response = client.create_table(
      AttributeDefinitions=[
          {
              'AttributeName': 'week',
              'AttributeType': 'S'
          },
          {
              'AttributeName': 'teamID',
              'AttributeType': 'S'
          }
      ],
      TableName= table_name,
      KeySchema=[
          {
              'AttributeName': 'week',
              'KeyType': 'HASH'
          },
          {
              'AttributeName': 'teamID',
              'KeyType': 'RANGE'
          }
      ],
      BillingMode= 'PAY_PER_REQUEST'
  )

    return response

def add_sample_data(table_name):
    dynamodb = boto3.resource('dynamodb')
    db = dynamodb.Table(table_name)
    # file = multiplayer_table_sample_data.csv

    items = []
    with open(os.path.join(os.path.dirname(__file__), 'multiplayer_table_sample_data.csv'), encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            #create dict to store csv data
            data = {}
            #map csv fields to dict fields
            data['week'] = row['Week']
            data['teamID'] = row['Team']
            data['multiplayer'] = row['Multiplayer']
            # data['seed'] = row['Seed']
            items.append(data)
    # print(items)

    for item in items:
        response = db.put_item(Item = item)

    return response

if __name__ == '__main__':
    table_name = 'multiplayer_input'
    dynamodb = boto3.resource('dynamodb', region_name=Config.region_name)
    dynamodb_client = dynamodb.meta.client

    #create multiplayer_table ONLY RUN THIS FUNCTION ONCE, CHECK CONSOLE TO SEE IF TABLE ALREADY EXISTS
    # db_table = create_multiplayer_table(table_name)
    # print("Table status:", db_table.table_status)
    try:
        db_table = create_table(table_name)
        print('Creating Multiplayer input table')
        print("Table status: {}".format(db_table['TableDescription']['TableStatus']))

    except dynamodb_client.exceptions.ResourceInUseException:
        print('{} already exists'.format(table_name))
        
    #add sample data to existing table
    print('Inserting data into Multiplier table')
    time.sleep(5)
    table = dynamodb.Table(table_name)

    data_add_status = add_sample_data(table_name)
