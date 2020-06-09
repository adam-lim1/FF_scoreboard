import boto3
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from config import Config

# ToDo - Replace prints with logger

def create_table(table_name, dynamodb=None):
    client = boto3.client('dynamodb')

    response = client.create_table(
      AttributeDefinitions=[
          {
              'AttributeName': 'teamID',
              'AttributeType': 'S'
          }
      ],
      TableName= table_name,
      KeySchema=[
          {
              'AttributeName': 'teamID',
              'KeyType': 'HASH'
          }
      ],
      BillingMode= 'PAY_PER_REQUEST'
  )

    return response

if __name__ == '__main__':

    table_name = 'teams'
    dynamodb = boto3.resource('dynamodb', region_name=Config.region_name)
    dynamodb_client = dynamodb.meta.client

    # Create table if doesn't exist
    # https://stackoverflow.com/questions/42485616/how-to-check-if-dynamodb-table-exists
    try:
        db_table = create_table(table_name)
        print('Creating Teams table')
        print("Table status: {}".format(db_table['TableDescription']['TableStatus']))

    except dynamodb_client.exceptions.ResourceInUseException:
        print('{} already exists'.format(table_name))

    # Insert data
    # ToDo - check affect if table (and data) exists
    print('Inserting data into Teams table')
    time.sleep(5)
    table = dynamodb.Table(table_name)
    table.put_item(Item={'teamID':str(8), 'username':'adam'})
