import boto3
import csv

def create_table(dynamodb=None, table_name):
    dynamodb = boto3.client('dynamodb')

    response = client.create_table(
      AttributeDefinitions=[
          {
              'AttributeName': 'week',
              'AttributeType': 'N'
          },
          {
              'AttributeName': 'team',
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
              'AttributeName': 'team',
              'KeyType': 'RANGE'
          }
      ]
  )

    return response

def add_sample_data(data, table_name):
    dynamodb = boto3.resource('dynamodb')
    db = dynamodb.Table(table_name)

    items = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data = {}
            data['temp'] = row['temp']
            #populate remaining fields here
            items.append(data)

    for item in items:
        response = db.put_item(Item = item)

if __name__ == '__main__':
    table_name = 'multiplayer_input'


    db_table = create_table(table_name)
    print("Table status:", db_table.table_status)
