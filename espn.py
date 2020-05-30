import requests

class espn:
  def __init__(self, leagueID, year, swid_cookie=None, s2_cookie=None):
      self.leagueID = leagueID
      self.year = year
      self.swid_cookie = swid_cookie
      self.s2_cookie = s2_cookie

  def getCurrentWeek(self):
      '''
      Get current matchup week from ESPN Fantasy Football API.
      :param leagueID (str): ESPN League ID. For further information on ESPN Parameters, see here: https://stmorse.github.io/journal/espn-fantasy-v3.html
      :param year (str): ESPN League Year
      :param swid_cookie (str): ESPN SWID Cookie for private leagues
      :param s2_cookie (str): ESPN S2 Cookie for private leagues
      :return (int): Current matchup week
      '''

      url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{leagueID}?view=modular".format(
      leagueID=self.leagueID,
      year=self.year)

      r = requests.get(url,
               cookies={"swid": "{swid_cookie}".format(swid_cookie=self.swid_cookie),
                        "espn_s2": "{s2_cookie}".format(s2_cookie=self.s2_cookie)})
      response = r.json()

      ## FIND CURRENT WEEK NBR
      matchupPeriodId = response['status']['currentMatchupPeriod']

      return matchupPeriodId
