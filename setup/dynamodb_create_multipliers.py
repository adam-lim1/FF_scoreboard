import boto3
import time
import sys
import os
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from config import Config

# ToDo - Replace prints with logger

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

    items = []
    with open(os.path.join(os.path.dirname(__file__), 'multipliers.csv'), encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            #create dict to store csv data
            data = {}
            #map csv fields to dict fields
            data['week'] = row['Week']
            data['teamID'] = row['TeamID']
            data['Multiplier'] = row['Multiplier']
            data['Available Multipliers'] = row['Available Multipliers']
            items.append(data)
    # print(items)

    for item in items:
        response = db.put_item(Item = item)

    return response

if __name__ == '__main__':

    table_name = 'multiplier_input'
    dynamodb = boto3.resource('dynamodb', region_name=Config.region_name)
    dynamodb_client = dynamodb.meta.client

    # Create table if doesn't exist
    # https://stackoverflow.com/questions/42485616/how-to-check-if-dynamodb-table-exists
    try:
        db_table = create_table(table_name)
        print('Creating Multiplier table')
        print("Table status: {}".format(db_table['TableDescription']['TableStatus']))

    except dynamodb_client.exceptions.ResourceInUseException:
        print('{} already exists'.format(table_name))

    # Insert data
    print('Inserting data into Multiplier table')
    time.sleep(5)
    table = dynamodb.Table(table_name)

    data_add_status = add_sample_data(table_name)
