import json
import random
import datetime
import stats
from emojis import emojis

date_format = "%Y-%m-%d %H:%M"

# def getRandomEmoji():
#     return random.choice([
#         '<:Invoker:849442548044660777>',
#         '<:Earthshaker:849443338772152360>',
#         '<:Mars:849444978034737242>',
#         '<:Rapier:850828789947564053>',
#         '<:ClockHead:859597036310233121>',
#         '<:PudgeArcana:849636106383130664>',
#         '<:DChook:848629647116730389>',
#         '<:TechiesMine:843852928351338516>'
#     ])

class gameManager:
    def __init__(self, filename: str = None, users = None):
        self.filename = filename
        self.current_game = None
        self.current_message_ptr = None
        self.users = users
        self.users.setGameManager(self)
        if self.filename:
            self.loadFromJson()
        else:
            self.game_list = []
        try:
            from indicator import indicator
            self.indicator = indicator(red_pin=21, green_pin=26)
        except:
            self.indicator = None
    
    def loadFromJson(self):
        try:
            with open(self.filename) as input:
                self.game_list = json.load(input)
            # for game in self.game_list:
        except:
            self.game_list = []
            print(f"No game json found at: {self.filename}")
    
    def writeToJson(self):
        try:
            with open(self.filename, 'w') as output:
                json.dump(self.game_list, output)
        except:
            print(f"Failed to write json to: {self.filename}")

    def getBlankGame(self):
        return {
            "id": None,
            "name": None,
            "created": None,
            "message_id": None,
            "emoji": emojis.getRandomGameEmoji(),
            "bets": [],
            "teams": {
                "radiant": [],
                "dire": [],
            },
            "winner": None
        }
    
    def getGameOdds(self, requested_team: str = None):
        game = self.getGame()
        avg_odds = 1.8
        if not game:
            return {'radiant': avg_odds, 'dire': avg_odds}
        mmrs = {}
        fallback_mmr = self.users.getBlankUser()['mmr']
        for team in ['radiant', 'dire']:
            mmr_sum = 0
            for player in game['teams'][team]:
                mmr = self.users.getUserMMR(player)
                if mmr:
                    mmr_sum += mmr
                else:
                    mmr_sum += fallback_mmr
            mmr_sum += (5-len(game['teams'][team]))*fallback_mmr
            mmrs.update({team: mmr_sum})
        odds = {}
        tot_mmrs = mmrs['radiant'] + mmrs['dire']
        for team in ['radiant', 'dire']:
            team_odds = round(avg_odds * (2*(tot_mmrs - mmrs[team]) / tot_mmrs)**2,2)
            odds.update({team: team_odds})
        if not requested_team:
            return odds
        else:
            return odds[requested_team.lower()]
    
    def getNewGameId(self):
        if not self.game_list:
            return 1
        return 1+max([game['id'] for game in self.game_list])
    
    def startNewGame(self, name = None):
        if self.getGame():
            return None
        game = self.getBlankGame()
        game['id'] = self.getNewGameId()
        game['name'] = f"Game_{game['id']}" if not name else name
        game['created'] = datetime.datetime.now().strftime(date_format)
        
        self.current_game = game
        if self.indicator:
            self.indicator.setReady()
        return self.showGame()

    def getGame(self, game_id: int = None):
        if not game_id:
            return self.current_game
        else:
            game = [game for game in self.game_list if game["id"] == game_id]
            if not game:
                return None
            return game[0]
        
    def getAllGames(self):
        return self.game_list
    
    def getGameNameAndId(self, game_id: int = None):
        game = self.getGame(game_id)
        if not game:
            return "No game found"
        return f"Game **{game['name']}** with id **{game['id']}**"

    def getGameByMessageId(self, message_id):
        if self.current_game:
            if self.current_game['message_id'] == message_id:
                return self.current_game
        for game in self.game_list:
            if game['message_id'] == message_id:
                return game
        return None
    
    def getPlayersByMessageId(self, message_id):
        game = self.getGameByMessageId(message_id)
        if not game:
            return []
        return game['teams']['radiant'] + game['teams']['dire']

    def getCurrentGameMessageId(self, game_id: int = None):
        game = self.getGame(game_id)
        if not game:
            return None
        return game['message_id']
    
    def addToTeam(self, discord_id, team: str, game_id: int = None):
        game = self.getGame(game_id = game_id)
        if not game:
            return False
        team = team.lower()
        players = game['teams']['radiant']+game['teams']['dire']
        if discord_id in players:
            return False
        if len(game['teams'][team]) >= 5:
            return False
        game['teams'][team].append(discord_id)
        if game_id:
            self.writeToJson()
        if self.indicator and len(players) >= 9:
            self.indicator.setBusy()
        
        return True
    
    def addBet(self, discord_id, bet_value, team: str):
        game = self.getGame()
        if not game:
            return "No active game"
        created = datetime.datetime.strptime(game['created'], date_format)
        now = datetime.datetime.now()
        minutes_since_creation = (now-created).total_seconds()/60
        if minutes_since_creation > 15:
            return "Bets for this game have closed"
        if team.lower() not in [t.lower() for t in self.getBlankGame()['teams'].keys()]:
            return f"{team} is not a valid team?"
        all_in = 0.17*(self.users.getPointsBalance(discord_id) == bet_value)
        winnings = round(self.getGameOdds(team)*bet_value)
        bet = {
            'user': discord_id,
            'bet_value': bet_value,
            'bet_team': team,
            'winnings': winnings
        }
        game['bets'].append(bet)
        return f"{bool(all_in)*'ALL IN BET! '}Bet of {bet_value} placed on the {team.capitalize()}. Potential winnings: {winnings}"

    def getTotalBetValue(self, discord_id = None, game_id: int = None):
        game = self.getGame(game_id)
        if not game:
            return 0
        if not discord_id:
            return sum([bet['bet_winnings'] for bet in game['bets']])
        else:
            return sum([bet['bet_winnings'] for bet in game['bets'] if game['bets'] == discord_id])


    def getPlayerTeam(self, discord_id, game_id: int = None):
        game = self.getGame(game_id)
        if not game:
            return None
        if discord_id in game['teams']['radiant']:
            return "Radiant"
        if discord_id in game['teams']['dire']:
            return "Dire"
        return None
    
    def removeFromTeam(self, discord_id, team: str):
        if not self.getGame():
            return False
        team = team.lower()
        if discord_id not in self.current_game['teams'][team]:
            return False
        self.current_game['teams'][team].remove(discord_id)
        
        if self.indicator:
            self.indicator.setReady()
        return True

    # ╚ ╔ ╝ ╗ ║ ═ ╠ ╣ ╩ ╦ ╬ 
    def showGame(self, game_id: int = None):
        game = self.getGame(game_id)
        if not game:
            return f"No game to show"
        message  = f"# {emojis.getEmoji('dotahouse')}   INHOUSE GAME   {game['emoji']}\n```"
        message += f" - Game ID: {game['id']}\n"
        message += f" - Name:    {game['name']}\n"
        message += f" - Date:    {game['created']}\n"
        message += f" - Winner:  {'Active game!' if not game['winner'] else game['winner']}\n"
        message += f"\n╔{'═'*21}╦{'═'*21}╗\n"
        message += f"║ {'{0:^20}'.format('RADIANT')}║{'{0:^20}'.format('DIRE')} ║\n"
        message += f"╠{'═'*21}╬{'═'*21}╣\n"
        empty = '-empty-'
        radiant = list([self.users.getName(player) for player in game['teams']['radiant']])
        radiant.extend([None]*(5-len(radiant)))
        dire = list([self.users.getName(player) for player in game['teams']['dire']])
        dire.extend([None]*(5-len(dire)))
        for p in range(5):
            radiant_player = '{0:<20}'.format(radiant[p][:20]) if radiant[p] else '{0:^20}'.format(empty)
            dire_player = '{0:>20}'.format(dire[p][:20]) if dire[p] else '{0:^20}'.format(empty)
            message += f"║ {radiant_player}║{dire_player} ║\n"
        message += f"╠{'═'*21}╬{'═'*21}╣\n"
        
        odds = self.getGameOdds()
        message += f"║ {'{0:^20}'.format('Odds: '+str(odds['radiant']))}║{'{0:^20}'.format('Odds: '+str(odds['dire']))} ║\n"
        message += f"╚{'═'*21}╩{'═'*21}╝\n"
        message += f"\n{'{0:<20}'.format('Player bets')}{'{0:>8}'.format('Bet')} {'{0:>8}'.format('Team')} {'{0:>7}'.format('Pot')}\n"
        for bet in game['bets']:
            message += f"{'{0:<20}'.format(self.users.getName(bet['user'])[:20])}{'{0:>8}'.format(bet['bet_value'])} {'{0:>8}'.format(bet['bet_team'].capitalize())} {'{0:>7}'.format(bet['winnings'])}\n"
        message += "\nWhen ready, click on a creep to join that team!```"
        if game['winner'] and game['winner'].lower() != 'none':
            message += '\n## Winner ' + emojis.getEmoji(f"creep_{game['winner'].lower()}")
        return message

    def showUserStats(self, discord_id, args:list = None):
        allowed_args = ['-full', '-me', '-vs']
        if len(args) == 0 or args[0] not in allowed_args:
            return f"Need to specify flags from: {allowed_args}"
        if args[0] == '-me':
            return self.users.showUser(discord_id)
        if args[0] == '-vs':
            return stats.pvpStats(self, self.users, discord_id, args)
        if args[0] == '-full':
            return self.users.showAllUsers()
        return
    

    def setMessagePtr(self, message_ptr, game_id: int = None):
        game = self.getGame(game_id)
        if not game:
            return
        if not game_id:
            self.current_message_ptr = message_ptr
        game['message_id'] = message_ptr.id

    def getMessagePtr(self):
        '''Returns the message pointer to the current game.
        Archived games only store the message id.'''
        return self.current_message_ptr
    
    def setWinner(self, winning_team: str):
        if not self.current_game:
            return "Can't set winner. No ongoing game."
        if winning_team.lower() not in ['radiant','dire','none']:
            return f"{winning_team} isn't a valid winner ffs, use either Radiant, Dire or None"
        self.current_game['winner'] = winning_team.capitalize()
        victory_text = self.showGame()
        self.game_list.append(self.current_game)
        if winning_team.lower() != 'none':
            for team, players in self.current_game['teams'].items():
                for player in players:
                    score = 1 if team == winning_team else -1
                    self.users.addScore(player,score)
                    if team == winning_team:
                        self.users.addPoints(player,50)
            for bet in self.current_game['bets']:
                if winning_team == bet['bet_team']:
                    self.users.addPoints(bet['user'],bet['winnings']-bet['bet_value'])
                else:
                    self.users.addPoints(bet['user'],-bet['bet_value'])
                if self.users.getPointsBalance(bet['user']) < 10:
                    self.users.addPoints(bet['user'],10 - self.users.getPointsBalance(bet['user']))
            self.users.writeToJson()

        self.writeToJson()
        self.current_game = None
        self.current_message_ptr = None
        if self.indicator:
            self.indicator.setOff()
        return victory_text