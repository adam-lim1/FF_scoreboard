### CONFIG.PY Definied for use in Input.py web form
# ToDo - merge config.txt into here
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # ESPN Parameters
    leagueID='758108'
    year='2019'
    swid_cookie='263ED77F6718'
    s2_cookie='AEC7ZIkwAaOY6lcDNaV2WiLBRO1oa%2FbycpecaaFmxEhS%2Fdmxnxt7dlaHvCYSLuBXfN1SgO%2F3WX2SQWmeQzBGhj4c5tpNOWaYKfiBv4h4HzT9UGYe72ASsRPbd3GOlRlMeLPjBm20psN8pzxEadVjGd%2F35TshwL7kKnl7VjoZ1axWmuOSjsyGNnX%2Bvq0maO1M5XuWm0UlHtv8EmIClzbGZ02zw5JoMwkQbOFPgKlAtCNnpn7MKYFwvJ6qVLNkS64%2Bl1rxwmhNFUPIqTfSwJRyg%2FPJ'
