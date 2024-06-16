import os
import csv
import json
import datetime
from emojis import emojis

medals = {
    'herald': '<:Herald:843856608353845269>',
    'guardian': '<:Guardian:843856608831995964>',
    'crusader': '<:Crusader:843856608471941173>',
    'archon': '<:Archon:843856608815087626>',
    'legend': '<:Legend:843856608785858601>',
    'ancient': '<:Ancient:843856608882589747>',
    'divine': '<:Divine:843856608609828865>',
    'immortal': '<:Immortal:843856609477787719>'
}

class userTable:
    def __init__(self, filename: str = None, game_manager = None):
        self.filename = filename
        self.transactions_file = 'transactions.csv'
        self.game_manager = game_manager
        if self.filename:
            self.loadFromJson()
        else:
            self.user_list = []

    def loadFromJson(self):
        try:
            with open(self.filename) as input:
                self.user_list = json.load(input)
                for user in self.user_list:
                    if 'other_ids' in user.keys():
                        del user['other_ids']
                    if 'perks' not in user.keys():
                        user.update({'perks': []})
                    elif type(user['perks']) == dict:
                        user['perks'] = list(user['perks'].keys())
        except:
            self.user_list = []
            print(f"No user json found at: {self.filename}")
    
    def writeToJson(self):
        try:
            with open(self.filename, 'w') as output:
                json.dump(self.user_list, output)
        except:
            print(f"Failed to write json to: {self.filename}")

    def getBlankUser(self):
        return {
            "id": None,
            "name": None,
            "joined": None,
            "points": 100,
            "mmr": 3000,
            "perks": [],
            "stats": {
                "wins": 0,
                "losses": 0
            }
        }
    
    def setGameManager(self, game_manager):
        self.game_manager = game_manager

    def getUser(self, discord_id):
        user = [user for user in self.user_list if user["id"] == discord_id]
        if not user:
            return None
        return user[0]
    
    def getUserFromName(self, name:str):
        user = [user for user in self.user_list if user["name"] == name]
        if not user:
            return None
        return user[0]
    
    def getUserMMR(self, discord_id):
        user = self.getUser(discord_id)
        if not user:
            return None
        return int(user['mmr'])
    
    def getUserPerks(self, discord_id):
        user = self.getUser(discord_id)
        if not user:
            return []
        return user['perks']
    
    def hasPerk(self, discord_id, perk_name):
        '''Returns True if the user has specified perk, otherwise False'''
        user = self.getUser(discord_id)
        if not user:
            return False
        return perk_name in user['perks']
    
    def getAllUserIds(self):
        return [user['id'] for user in self.user_list]
    
    def getName(self, discord_id):
        user = self.getUser(discord_id)
        if not user:
            return '- Unknown plebian -'
        return user['name']
    
    def isUser(self, discord_id):
        users = [user["id"] for user in self.user_list]
        if discord_id in users:
            return True
        return False

    def getPointsBalance(self, discord_id, include_bets = True):
        user = self.getUser(discord_id)
        if not user:
            return 0
        return user['points'] - include_bets*self.game_manager.getTotalBetValue(discord_id)

    def getUserByCustomId(self, id_type: str, id):
        if not self.checkValidType(id_type):
            return None
        user = [user for user in self.user_list if id in user["other_ids"][id_type]]
        if not user:
            return None
        return user[0]
    
    def getUserByName(self, name: str, return_only_id: bool = False):
        user = [user for user in self.user_list if name == user['name']]
        if not user:
            return None
        if return_only_id:
            return user[0]['id']
        else:
            return user[0]
    
    # Stats
    def showUser(self, discord_id):
        message = ""
        user = self.getUser(discord_id)
        if not user:
            return "Bruh, you ain't even registered..."
        message += f"```Showing summary for discord id {user['id']}```\n"
        
        w = user['stats']['wins'];   l = user['stats']['losses']
        wr = 0 if w+l == 0 else round(100*w/(w+l))
        mmr = user['mmr'] if w+l >= 10 else f"Uncalibrated ({10-w-l} games left)"
        medal = emojis.medal(ratio=self.getScoreRank(discord_id))

        message += f"# {medal} {user['name']}\n" 
        message += f"## {emojis.getEmoji('points')} Points: **{user['points']}**\n\n"
        message += f">>> Joined on: **{user['joined']}**\n"
        message += f"Inhouse MMR: **{mmr}**\n"
        message += f"Lifetime games: **{w+l}**\n"
        message += f"Lifetime winrate: **{wr}%**\n"
        message += f"Unlocked perks: {len(user['perks'])}\n"
        for perk in user['perks']:
            message += f"- {perk.capitalize()}\n"

        
        return message
    
    # └ ┌ ┘ ┐ │ ─ ├ ┤ ┴ ┬ ┼
    # ╚ ╔ ╝ ╗ ║ ═ ╠ ╣ ╩ ╦ ╬ 
    def showAllUsers(self, sort_by: str = 'name'):
        message = f"```┌{20*'─'}─┬─{6*'─'}─┬─{5*'─'}─┬─{4*'─'}─┬─{5*'─'}┐\n"
        message += f"│{'{0:<20}'.format('Name')} │ {'{0:^6}'.format('Points')} │ {'{0:^5}'.format('Games')} │ {'{0:^4}'.format('WR')} │ {'{0:^5}'.format('MMR')}│\n"
        message += f"├{20*'─'}─┼─{6*'─'}─┼─{5*'─'}─┼─{4*'─'}─┼─{5*'─'}┤\n"
        user_list = list(self.user_list)
        
        # "id": None, "name": None, "joined": None, "points": 100, "mmr": 3000, "stats": {"wins": 0, "losses": 0}
        if sort_by.lower() == 'name':
            user_list.sort(key = lambda u : u['name'].lower())
        elif sort_by.lower() == 'mmr':
            user_list.sort(key = lambda u : u['mmr'], reverse=True)
        elif sort_by.lower() == 'games':
            user_list.sort(key = lambda u : u['wins']+u['losses'], reverse=True)
        elif sort_by.lower() == 'wins':
            user_list.sort(key = lambda u : u['wins'], reverse=True)
        elif sort_by.lower() == 'losses':
            user_list.sort(key = lambda u : u['losses'], reverse=True)
        elif sort_by.lower() == 'wr':
            user_list.sort(key = lambda u : u['wins']/(u['wins']+u['losses']), reverse=True)
        else:
            user_list.sort(key = lambda u : u['name'].lower())

        for user in user_list:
            w = user['stats']['wins']
            l = user['stats']['losses']
            wr = 0 if w+l == 0 else round(100*w/(w+l))
            message += f"│{'{0:<20}'.format(user['name'][:20])} │ {'{0:>6}'.format(user['points'])} │ {'{0:>5}'.format(w+l)} │ {'{0:>4}'.format(str(wr)+'%')} │ {'{0:>5}'.format(user['mmr'] if w+l>= 10 else '-')}│\n"
        message += f"└{20*'─'}─┴─{6*'─'}─┴─{5*'─'}─┴─{4*'─'}─┴─{5*'─'}┘```"
        return message



    def showScoreboard(self, discord_id = None, full = False):
        user_list = self.getScoreList()
        if not user_list:
            return "No players yet"
        message = f"# {emojis.getEmoji('dotahouse')} LEADERBOARD {emojis.getEmoji('points')}\n"
        # message += "──────────────\n"
        preview = 6
        length = len(user_list) if full else min(preview, len(user_list))
        for i in range(length):
            ratio = self.getScoreRank(user_list[i]['id'], user_list)
            name = user_list[i]['name'].replace('_','\\_').replace('*','\\*') 
            if discord_id is not None and user_list[i]['id'] == discord_id:
                name = f"**__{name}__**"
            message += f"{'## '*(ratio == 1.0)}{emojis.medal(ratio=ratio)} {i+1}. {name}: **{user_list[i]['points']}**\n"

        if not full and len(user_list) > preview:
            message += '`...`\n'
            i = len(user_list)-1
            message += f"{emojis.medal(ratio=0)} {i+1}. {user_list[i]['name']}: **{user_list[i]['points']}**\n"

        return message

    def getScoreList(self):
        user_list = list(self.user_list)
        user_list.sort(key = lambda u : u['points'], reverse=True)
        return user_list

    def getScoreRank(self, discord_id, user_list: list = None):
        if not user_list:
            user_list = self.getScoreList()
        if len(user_list) < 2:
            return 0
        user = self.getUser(discord_id)
        if not user:
            return 0
        
        max_p = user_list[0]['points']
        min_p = user_list[-1]['points']
        
        return round((user['points']-min_p)/(max_p-min_p),4)
    

    # Adders, Setters and Removers
    def addUser(self, discord_id, name = None):
        '''Adds a new user to the table based on their discord id. Other ids may be added by keyworded arguments.'''
        if self.getUser(discord_id):
            return f"Error: User with discord_id {discord_id} already exists. Se instructions to add other ids to your discord account."
        user = self.getBlankUser()
        user["id"] = discord_id
        user["name"] = str(discord_id) if not name else name
        user["joined"] = str(datetime.datetime.today().date())
        self.user_list.append(user)

        self.writeToJson()
        return f"Welcome {user['name']}, you are now registered. There's no turning back now..."
        
    def addScore(self, discord_id, score: int):
        user = self.getUser(discord_id)
        if not user:
            return
        w = user['stats']['wins'];   l = user['stats']['losses']
        mmr_delta = score * (25 + (w+l < 10)*(10-w-l)*25)
        user['mmr'] = round(user['mmr'] + mmr_delta)
        if score == 1:
            user['stats']['wins'] += 1
        elif score == -1:
            user['stats']['losses'] += 1
    
    def addPoints(self, discord_id, points):
        user = self.getUser(discord_id)
        if not user:
            return
        user['points'] += points

    def tipUser(self, source_user, target_user, tip_value):
        if not self.isUser(source_user) or not self.isUser(target_user):
            return f"Couldn't locate users for tipping"
        
        if tip_value > -10+self.getPointsBalance(source_user, include_bets=True):
            return f"You're trying to tip more than you can afford, you can't tip below 10 points..."
        
        self.addPoints(source_user, -tip_value)
        self.addPoints(target_user, tip_value)
        self.writeTransaction(source_user, 'tip', target_user, tip_value)
        self.writeToJson()
        return f"**{self.getName(source_user)}** tipped **{self.getName(target_user)}** with **{tip_value}** points!"


    def getAllPerks(self):
        return {
            'win-win': {
                'cost': 1500,
                'desc': "Losses also give +10 points"
            },
            'cheerleader': {
                'cost': 2000,
                'desc': "Spectator bets give 50% win/loss points *(for bets above 10 on 1 team)*"
            },
            'inflation': {
                'cost': 3000,
                'desc': "Wins give an additional +20 points"
            },
            'hedged': {
                'cost': 5000,
                'desc': "Lost bets return 10% of the points"
            },
            'midas': {
                'cost': 5000,
                'desc': "Gives 5% increase to bet winnings *(does not work with random bets)*"
            }
        }

    def addPerk(self, discord_id, perk_name):
        user = self.getUser(discord_id)
        if not user:
            return "Couldn't add perk, not registered or something?"
        perk_name = perk_name.lower()
        if perk_name not in self.getAllPerks().keys():
            return f"**{perk_name.capitalize()}** is not a valid perk"
        
        perk = self.getAllPerks()[perk_name]
        if perk['cost'] > self.getPointsBalance(discord_id,include_bets=True):
            return f"You're too poor for this perk, you need another {perk['cost'] - self.getPointsBalance(discord_id,include_bets=True)} points to unlock {perk_name.capitalize()}."
        
        if perk_name in user['perks']:
            return f"{user.getName()} already has {perk_name.capitalize()}."
        
        user['perks'].append(perk_name.lower())
        self.addPoints(discord_id, -perk['cost'])
        self.writeTransaction(user['id'], 'perk', perk_name, perk['cost'])
        self.writeToJson()
        return f"{self.getName(discord_id)} successfully unlocked the {perk_name.capitalize()} perk!"

    def writeTransaction(self, discord_id, item_type, item_spec, cost, date_time:datetime.datetime = datetime.datetime.now()):
        '''Writes a transaction to file
        discord_id = discord_id of buyer
        item_type = perk, tip etc
        item_spec = specific perk name, target player etc
        cost = points spent by buyer
        date_time = optional, uses datetime.datetime.now() if not specified'''
        
        if not os.path.isfile(self.transactions_file):
            fp = open(self.transactions_file, 'w+')
            fp.write('user,item_type,item_spec,cost,date_time\n')
        else:
            fp = open(self.transactions_file, 'a+')
        fp.write(','.join([str(discord_id), str(item_type), str(item_spec), str(cost), str(date_time)])+'\n')
        fp.close()

    def readTransactions(self):
        if os.path.isfile(self.transactions_file):
            with open(self.transactions_file,'r') as input:
                reader = csv.DictReader(input)
                transactions = [row for row in reader]
        else:
            transactions = []
        return transactions

    def setName(self, discord_id, name: str):
        user = self.getUser(discord_id)
        if not user:
            return f"No account found for discord_id {discord_id}"
        if self.getUserByName(name) is not None:
            return f"The name {name} is already taken... gosh darn it"
        user["name"] = name
        self.writeToJson()
        return f"The name {name} is now associated with your account."
        

if __name__ == "__main__":
    users = userTable(filename = 'users.json')
    name = 'Feediot player'
    print(f"ID of {name} is: {users.getUserFromName('Feediot player')}")

