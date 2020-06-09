import boto3
import time

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
    client = boto3.client('dynamodb')

    # Create table if doesn't exist
    # https://stackoverflow.com/questions/42485616/how-to-check-if-dynamodb-table-exists
    try:
        db_table = create_table(table_name)
        print('Creating Teams table')
        print("Table status: {}".format(db_table['TableDescription']['TableStatus']))

    except client.exceptions.ResourceInUseException:
        print('{} already exists'.format(table_name))

    # Insert data
    # ToDo - check affect if table (and data) exists
    print('Inserting data into Teams table')
    time.sleep(15)
    dynamodb = boto3.resource('dynamodb', region_name="us-east-2")
    table = dynamodb.Table(table_name)
    table.put_item(Item={'teamID':str(8), 'username':'adam'})
