import json
import random
import datetime

def getRandomEmoji():
    return random.choice([
        '<:Invoker:849442548044660777>',
        '<:Earthshaker:849443338772152360>',
        '<:Mars:849444978034737242>',
        '<:Rapier:850828789947564053>',
        '<:ClockHead:859597036310233121>',
        '<:PudgeArcana:849636106383130664>',
        '<:DChook:848629647116730389>',
        '<:TechiesMine:843852928351338516>'
    ])

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
            "emoji": getRandomEmoji(),
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
        for team in ['radiant', 'dire']:
            mmr_sum = 0
            fallback_mmr = self.users.getBlankUser()['mmr']
            for player in team:
                user = self.users.getUser(player)
                if user:
                    mmr_sum += user['mmr']
                else:
                    mmr_sum += fallback_mmr

            mmrs.update({team: mmr_sum})
        odds = {}
        for team in ['radiant', 'dire']:
            team_odds = round(avg_odds * 2 * mmrs[team]/ (mmrs['radiant'] + mmrs['dire']),2)
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
        game['created'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        self.current_game = game
        return self.showGame()

    def getGame(self, id: int = None):
        if not id:
            return self.current_game
        else:
            game = [game for game in self.game_list if game["id"] == id]
            if not game:
                return None
            return game[0]
    
    def getGameNameAndId(self, id: int = None):
        game = self.getGame(id)
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

    def getCurrentGameMessageId(self):
        return self.current_game['message_id']
    
    def addToTeam(self, discord_id, team: str):
        if not self.getGame():
            return False
        team = team.lower()
        if discord_id in self.current_game['teams']['radiant']+self.current_game['teams']['dire']:
            return False
        if len(self.current_game['teams'][team]) >= 5:
            return False
        self.current_game['teams'][team].append(discord_id)
        return True
    
    def removeFromTeam(self, discord_id, team: str):
        if not self.getGame():
            return False
        team = team.lower()
        if discord_id not in self.current_game['teams'][team]:
            return False
        self.current_game['teams'][team].remove(discord_id)
        return True

    # ╚ ╔ ╝ ╗ ║ ═ ╠ ╣ ╩ ╦ ╬ 
    def showGame(self, game_id: int = None):
        game = self.getGame(game_id)
        if not game:
            return f"No game to show"
        message  = f"# <a:DotaHouse:849006603663048724>   INHOUSE GAME   {game['emoji']}\n```"
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
            radiant_player = '{0:<20}'.format(radiant[p]) if radiant[p] else '{0:^20}'.format(empty)
            dire_player = '{0:>20}'.format(dire[p]) if dire[p] else '{0:^20}'.format(empty)
            message += f"║ {radiant_player}║{dire_player} ║\n"
        message += f"╠{'═'*21}╬{'═'*21}╣\n"
        
        odds = self.getGameOdds()
        message += f"║ {'{0:^20}'.format('Odds: '+str(odds['radiant']))}║{'{0:^20}'.format('Odds: '+str(odds['dire']))} ║\n"
        message += f"╚{'═'*21}╩{'═'*21}╝\n"
        message += "\nWhen ready, click on a creep to join that team!```"
        return message

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
        self.current_game['winner'] = winning_team.capitalize()
        self.game_list.append(self.current_game)
        for team, players in self.current_game['teams'].items():
            for player in players:
                score = 1 if team == winning_team else -1
                self.users.addScore(player,score)
                if team == winning_team:
                    self.users.addPoints(player,50)
        
        self.users.writeToJson()
        self.writeToJson()

        victory_text = self.showGame()
        self.current_game = None
        self.current_message_ptr = None
        return victory_text