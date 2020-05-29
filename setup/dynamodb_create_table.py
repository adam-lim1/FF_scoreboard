import boto3


def create_table(dynamodb=None):
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
      TableName='multiplayer_input',
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

    return table


if __name__ == '__main__':
    db_table = create_table()
    print("Table status:", db_table.table_status)
