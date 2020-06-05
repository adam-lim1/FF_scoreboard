import boto3
import csv

def create_multiplayer_table(table_name, dynamodb=None):
    dynamodb = boto3.client('dynamodb')

    response = dynamodb.create_table(
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
      ],
      BillingMode= 'PAY_PER_REQUEST'
  )

    return response

def add_sample_data(table_name):
    dynamodb = boto3.resource('dynamodb')
    db = dynamodb.Table(table_name)
    # file = multiplayer_table_sample_data.csv

    items = []
    with open('multiplayer_table_sample_data.csv') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            #create dict to store csv data
            data = {}
            #map csv fields to dict fields
            data['week'] = int(row['Week'])
            data['team'] = row['Team']
            data['multiplayer'] = row['Multiplayer']
            data['seed'] = row['Seed']
            items.append(data)
    # print(items)

    for item in items:
        response = db.put_item(Item = item)

    return response

if __name__ == '__main__':
    table_name = 'multiplayer_input'

    #create multiplayer_table ONLY RUN THIS FUNCTION ONCE, CHECK CONSOLE TO SEE IF TABLE ALREADY EXISTS
    # db_table = create_multiplayer_table(table_name)
    # print("Table status:", db_table.table_status)

    #add sample data to existing table
    data_add_status = add_sample_data(table_name)
