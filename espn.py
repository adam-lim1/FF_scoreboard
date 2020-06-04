# ToDo - Tabs vs. Spaces Alignment
import requests
import pandas as pd

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

  def getTeamsKey(self):
      '''
      Get list of Teams and Team ID from ESPN Fantasy Football API. Create Team Name as {Location} + {Nickname} + ({Abbreviation})
      :param leagueID (str): ESPN League ID. For further information on ESPN Parameters, see here: https://stmorse.github.io/journal/espn-fantasy-v3.html
      :param year (str): ESPN League Year
      :param swid_cookie (str): ESPN SWID Cookie for private leagues
      :param s2_cookie (str): ESPN S2 Cookie for private leagues
      :return (DataFrame): Nbr Rows = {n Teams}. Cols = [FullTeamName]
      '''
      # ToDo: Complete function docstring

      url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{leagueID}?view=mBoxscore".format(
      leagueID=self.leagueID,
      year=self.year)

      r = requests.get(url,
                       cookies={"swid": "{swid_cookie}".format(swid_cookie=self.swid_cookie),
                                "espn_s2": "{s2_cookie}".format(s2_cookie=self.s2_cookie)})

      teams = pd.DataFrame(r.json()['teams'])
      teams['FullTeamName'] = teams['location'] + " " + teams['nickname'] + " (" + teams['abbrev'] + ")"
      teamsKey = teams[['id', 'FullTeamName']]
      teamsKey = teamsKey.set_index('id')

      ## Error handling for bye's
      teamsKey.loc[-999] = 'BYE'

      return teamsKey


  def getWeekScoreboard(self, viewWeek):
      '''
      Get DataFrame of scores by team for a given matchup week.
      :param leagueID (str): ESPN League ID. For further information on ESPN Parameters, see here: https://stmorse.github.io/journal/espn-fantasy-v3.html
      :param year (str): ESPN League Year
      :param swid_cookie (str): ESPN SWID Cookie for private leagues
      :param s2_cookie (str): ESPN S2 Cookie for private leagues
      :param viewWeek (int): Matchup week to pull scores for
      :return (DataFrame): Nbr Rows = {n Teams}. Cols = [Week, matchupID, teamID, Points, home_away]
      '''

      url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{leagueID}?view=mBoxscore".format(
      leagueID=self.leagueID,
      year=self.year)

      r = requests.get(url,

               cookies={"swid": "{swid_cookie}".format(swid_cookie=self.swid_cookie),
                        "espn_s2": "{s2_cookie}".format(s2_cookie=self.s2_cookie)})
      response = r.json()

      ## FIND CURRENT WEEK NBR
      matchupPeriodId = response['status']['currentMatchupPeriod']

      # GET LIST OF GAMES FOR VIEW WEEK
      response_week = [game for game in response['schedule'] if game['matchupPeriodId'] == viewWeek]

      ## Fill Score data for BYE weeks
      for x in range(0,len(response_week)):
          if 'away' not in response_week[x].keys():
              response_week[x]['away'] = {'teamId': -999, 'totalPoints': 0, 'rosterForCurrentScoringPeriod':{'appliedStatTotal': 0}}
          if 'home' not in response_week[x].keys():
              response_week[x]['home'] = {'teamId': -999, 'totalPoints': 0, 'rosterForCurrentScoringPeriod':{'appliedStatTotal': 0}}

      gameList = []

      for game in response_week:
          gameID = game['id']
          week = game['matchupPeriodId']

          home_teamID = game['home']['teamId']
          away_teamID = game['away']['teamId']

          # JSON output Format depends on Week
          if week < matchupPeriodId: # Past Week
              home_pts = game['home']['totalPoints']
              away_pts = game['away']['totalPoints']
          elif week == matchupPeriodId: # Current Week
              try:
                  home_pts = game['home']['rosterForCurrentScoringPeriod']['appliedStatTotal']
                  away_pts = game['away']['rosterForCurrentScoringPeriod']['appliedStatTotal']
              except KeyError: # Support API after season is over (when scores finalized but matchup week not iterated)
                  home_pts = game['home']['totalPoints']
                  away_pts = game['away']['totalPoints']
          elif week > matchupPeriodId: # Future Week
              home_pts = 0
              away_pts = 0

          gameList.append([gameID, week, home_teamID, away_teamID, home_pts, away_pts])

      scoreboardDF = pd.DataFrame(gameList, columns=['id', 'Week', 'home_teamID', 'away_teamID', 'home_pts', 'away_pts'])
      scoreboardDF['matchupID'] = ((scoreboardDF['id'] % (6)) + 1) # Number of Teams

      ## BREAK OUT HOME/AWAY TEAMS TO SINGLE COLUMN
      home_df = scoreboardDF[['Week', 'matchupID', 'home_teamID', 'home_pts']].copy()
      home_df['home_away'] = 'Home'
      home_df = home_df.rename(columns={'home_teamID':'teamID', 'home_pts':'Points'})

      away_df = scoreboardDF[['Week', 'matchupID', 'away_teamID', 'away_pts']].copy()
      away_df['home_away'] = 'Away'
      away_df = away_df.rename(columns={'away_teamID':'teamID', 'away_pts':'Points'})

      scoreboardDF = home_df.append(away_df)

      return scoreboardDF

  def getWeekPlayerScores(self, viewWeek):
      '''
      Get DataFrame of individual player scores for all rostered players
      :param leagueID (str): ESPN League ID. For further information on ESPN Parameters, see here: https://stmorse.github.io/journal/espn-fantasy-v3.html
      :param year (str): ESPN League Year
      :param swid_cookie (str): ESPN SWID Cookie for private leagues
      :param s2_cookie (str): ESPN S2 Cookie for private leagues
      :param viewWeek (int): Matchup week to pull scores for
      :return (DataFrame): Nbr Rows = {n Teams * nbr Players / Team}. Cols = [Week, Team ID, Player, Slot, Pos, Status, Proj, Actual]
      '''

      ## Define dictionary of lineup slot codes to parse JSON
      slotcodes = {
          0 : 'QB', 2 : 'RB', 4 : 'WR',
          6 : 'TE', 16: 'Def', 17: 'K',
          20: 'Bench', 21: 'IR', 23: 'Flex', 18: 'P'
      }

      url = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{leagueID}?view=mMatchup&view=mMatchupScore'.format(
          year=self.year,
          leagueID=self.leagueID)

      data = []
      print('Week ', end='')
      print(viewWeek, end=' ')

      r = requests.get(url,
                   params={'scoringPeriodId': viewWeek},
                   cookies={"SWID": self.swid_cookie, "espn_s2": self.s2_cookie})
      d = r.json()

      for tm in d['teams']:
          tmid = tm['id']
          for p in tm['roster']['entries']:
              name = p['playerPoolEntry']['player']['fullName']
              slot = p['lineupSlotId']
              pos  = slotcodes[slot]

              # injured status (need try/exc bc of D/ST)
              inj = 'NA'
              try:
                  inj = p['playerPoolEntry']['player']['injuryStatus']
              except:
                  pass

              # projected/actual points
              proj, act = None, None
              for stat in p['playerPoolEntry']['player']['stats']:
                  if stat['scoringPeriodId'] != viewWeek:
                      continue
                  if stat['statSourceId'] == 0:
                      act = stat['appliedTotal']
                  elif stat['statSourceId'] == 1:
                      proj = stat['appliedTotal']

              data.append([
                  viewWeek, tmid, name, slot, pos, inj, proj, act
              ])
      print('\nComplete.')

      data = pd.DataFrame(data,
                          columns=['Week', 'Team ID', 'Player', 'Slot',
                                   'Pos', 'Status', 'Proj', 'Actual'])
      return data

  def getPlayerLockStatus(self, *args):
	  """
	  Function to check if player(s) (specified by args) are locked for given scoringPeriodId
	  NOTE - THIS FUNCTION NEEDS TESTING W/ ESPN API WHILE WEEK IS IN PROGRESS
	  HAS ONLY BEEN TESTED DURING OFF-SEASON
	  """
	  url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{leagueID}?view=mRoster".format(
	  leagueID=self.leagueID,
	  year=self.year)

	  r = requests.get(url,
	  cookies={"swid": "{swid_cookie}".format(swid_cookie=self.swid_cookie),
	  "espn_s2": "{s2_cookie}".format(s2_cookie=self.s2_cookie)})

	  # Iterate through Players for each team, adding current status to dict
	  status_dict = {}
	  for teamID in range(0,12): # ToDo - Dynamically get number of teams
	  	roster = r.json()['teams'][teamID]['roster']['entries']
	  	for player in range(0, 16): # ToDo - Dynamically get number of roster spots per team
	  		status_dict[roster[player]['playerPoolEntry']['player']['fullName']] = roster[player]['playerPoolEntry']['lineupLocked']
	  		# rosterLocked?

	  # Return boolean Lock Status for player in args
	  t = ()
	  for p in args:
		  if len(args) > 1:
			  t += (status_dict.get(p, 'Error'),)
		  else:
			  t = status_dict.get(p, 'Error')

	  return t
