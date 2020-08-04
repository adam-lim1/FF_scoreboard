import os

class Config(object):
    # Flask parameters
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # General league parameters
    version = '0.1'
    multiplierList = [-1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 3]

    # ESPN Parameters
    leagueID='758108'
    year='2019'
    swid_cookie='263ED77F6718'
    s2_cookie='AEC7ZIkwAaOY6lcDNaV2WiLBRO1oa%2FbycpecaaFmxEhS%2Fdmxnxt7dlaHvCYSLuBXfN1SgO%2F3WX2SQWmeQzBGhj4c5tpNOWaYKfiBv4h4HzT9UGYe72ASsRPbd3GOlRlMeLPjBm20psN8pzxEadVjGd%2F35TshwL7kKnl7VjoZ1axWmuOSjsyGNnX%2Bvq0maO1M5XuWm0UlHtv8EmIClzbGZ02zw5JoMwkQbOFPgKlAtCNnpn7MKYFwvJ6qVLNkS64%2Bl1rxwmhNFUPIqTfSwJRyg%2FPJ'

    # AWS Cognito Parameters
    region_name="us-east-2"

    cognito_url='https://ffl.auth.us-east-2.amazoncognito.com'
    app_client_id='6n7h391ts8jlt89pied1milh5a'
    redirect_uri='http://localhost:5000/input_form_cognito' # Ensure this matches value in console
