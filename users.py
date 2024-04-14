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
        self.game_manager = game_manager
        if self.filename:
            self.loadFromJson()
        else:
            self.user_list = []

    def loadFromJson(self):
        try:
            with open(self.filename) as input:
                self.user_list = json.load(input)
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
            "other_ids": {
                "steam_id": []
            },
            "stats": {
                "wins": 0,
                "losses": 0
            }
        }
    
    def setGameManager(self, game_manager):
        self.game_manager = game_manager

    def checkValidType(self, id_type: str):
        if id_type not in self.getBlankUser()["other_ids"].keys():
            return False
        return True
    
    def getInvalidTypeError(self, id_type: str):
        return f"{id_type} is not a valid id type. Available types are {list(self.getBlankUser()['other_ids'].keys())}."

    
    def getAllUsersByIdType(self, id_type: str):
        '''Returns a list of all ids of a certain type, such as discord_id or associated steam_id'''
        if id_type == 'discord_id':
            return [user["id"] for user in self.user_list]
        elif not self.checkValidType(id_type):
            return
        return [user["other_ids"][id_type] for user in self.user_list if user["other_ids"][id_type]]
    
    def getUser(self, discord_id):
        user = [user for user in self.user_list if user["id"] == discord_id]
        if not user:
            return None
        return user[0]
    
    def getUserMMR(self, discord_id):
        user = self.getUser(discord_id)
        if not user:
            return None
        return int(user['mmr'])
    
    def getAllUserIds(self):
        return [user['id'] for user in self.user_list]
    
    def getName(self, discord_id):
        user = self.getUser(discord_id)
        if not user:
            return None
        return user['name']
    
    def isUser(self, discord_id):
        user = [user for user in self.user_list if user["id"] == discord_id]
        if not user:
            return False
        return True

    def getPointsBalance(self, discord_id):
        user = self.getUser(discord_id)
        if not user:
            return 0
        return user['points'] - self.game_manager.getTotalBetValue(discord_id)

    
    def getUserByCustomId(self, id_type: str, id):
        if not self.checkValidType(id_type):
            return None
        user = [user for user in self.user_list if id in user["other_ids"][id_type]]
        if not user:
            return None
        return user[0]
    
    # Stats
    def showUser(self, discord_id):
        message = ""
        user = self.getUser(discord_id)
        if not user:
            return "Bruh, you ain't even registered..."
        message += f"```Showing summary for discord id {user['id']}```\n"
        # for id_type, ids in user['other_ids'].items():
        #     if ids:
        #         message += f" - Associated {id_type}s: {ids}\n"
        #     else:
        #         message += f" - No associated {id_type}s\n"
        
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
        
        return message
    
    # └ ┌ ┘ ┐ │ ─ ├ ┤ ┴ ┬ ┼
    # ╚ ╔ ╝ ╗ ║ ═ ╠ ╣ ╩ ╦ ╬ 
    def showAllUsers(self):
        message = f"```┌{20*'─'}─┬─{6*'─'}─┬─{5*'─'}─┬─{4*'─'}─┬─{5*'─'}┐\n"
        message += f"│{'{0:<20}'.format('Name')} │ {'{0:^6}'.format('Points')} │ {'{0:^5}'.format('Games')} │ {'{0:^4}'.format('WR')} │ {'{0:^5}'.format('MMR')}│\n"
        message += f"├{20*'─'}─┼─{6*'─'}─┼─{5*'─'}─┼─{4*'─'}─┼─{5*'─'}┤\n"
        user_list = list(self.user_list)
        user_list.sort(key = lambda u : u['name'])
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
        message = f"# {emojis.getEmoji('dotahouse')} SCOREBOARD {emojis.getEmoji('points')}\n"
        # message += "──────────────\n"
        preview = 6
        length = len(user_list) if full else min(preview, len(user_list))
        for i in range(length):
            ratio = self.getScoreRank(user_list[i]['id'], user_list)

            name = user_list[i]['name'].replace('_','\\_') if user_list[i]['id'] != discord_id else '**__'+user_list[i]['name'].replace('_','\\_')+'__**'
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
    def addUser(self, discord_id, name = None, steam_id=None):
        '''Adds a new user to the table based on their discord id. Other ids may be added by keyworded arguments.'''
        if self.getUser(discord_id):
            return f"Error: User with discord_id {discord_id} already exists. Se instructions to add other ids to your discord account."
        user = self.getBlankUser()
        user["id"] = discord_id
        user["name"] = str(discord_id) if not name else name
        user["joined"] = str(datetime.datetime.today().date())
        self.user_list.append(user)

        suffix = ""
        if steam_id:
            suffix += '\n'+self.addCustomId(discord_id, 'steam_id', steam_id)
        self.writeToJson()
        return f"Welcome {user['name']}, you are now registered. There's no turning back now..."+suffix
        
    def addScore(self, discord_id, score: int):
        user = self.getUser(discord_id)
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

    def addCustomId(self, discord_id, id_type: str, id):
        if not self.checkValidType(id_type):
            return self.getInvalidTypeError(id_type)
        existing_user = self.getUserByCustomId(id_type, id)
        if existing_user:
            return f"Error: {id_type} is already associated with discord user {existing_user['name']}"
        else:
            user = self.getUser(discord_id)
            user["other_ids"][id_type].append(id)
            self.writeToJson()
            return f"Success: {id_type} {id} was added to user {user['name']}"

    def setName(self, discord_id, name: str):
        user = self.getUser(discord_id)
        if not user:
            return f"No account found for discord_id {discord_id}"
        user["name"] = name
        self.writeToJson()
        return f"The name {name} is now associated with your account."
        

if __name__ == "__main__":
    table = userTable(filename = 'users.json')
    discord_id = 186
    print(table.addUser(discord_id, steam_id=982))
    print(table.setName(discord_id, "Felix"))
    print(table.getUserByCustomId("steam_id", 982))

