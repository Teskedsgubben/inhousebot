import json
from users import userTable

users = userTable('users.json')
fp = open('games.json')
games = json.load(fp)
fp.close()

def stats(user1,user2):
    playerstats = {
        'totalGames': 0,
        'winAlly': 0,
        'winEnemy': 0,
        'winRateAlly':0,
        'lossAlly': 0,
        'lossEnemy': 0,
        'winRateEnemy':0,
    }
    for game in games:
        radiant = game['teams']['radiant']
        dire = game['teams']['dire']
        players = radiant + dire
        if user1 in players and user2 in players:
            playerstats['totalGames'] += 1
            if (game['winner'].lower() == 'dire' and user1 in dire) or (game['winner'].lower() == 'radiant' and user1 in radiant):
                key = 'win'
            else:
                key='loss'

            if (user1 in radiant and user2 in radiant) or (user1 in dire and user2 in dire):
                key += 'Ally'
            else:
                key += 'Enemy'
            playerstats[key] += 1
    
    if (playerstats['winAlly']+playerstats['lossAlly']) != 0:
        playerstats['winRateAlly'] = playerstats['winAlly']/(playerstats['winAlly']+playerstats['lossAlly'])
    if (playerstats['winEnemy']+playerstats['lossEnemy']) != 0:
        playerstats['winRateEnemy'] = playerstats['winEnemy']/(playerstats['winEnemy']+playerstats['lossEnemy'])
    return playerstats

#for user2 in users.getAllUserIds():
#    print(user2)
def allstats(user1):
    lista = []
    for user2 in users.getAllUserIds():
        if user2 != user1:
            lista.append({
                'stats': stats(user1,user2),
                'name': users.getName(user2)
            })
    
    lista2 = [stats(user1,user2) for user2 in users.getAllUserIds() if user2 != user1]

    lista.sort(key= lambda x: x['stats']['totalGames'],reverse=True)
    return lista
rubululu = 541565507476652032

message = ""
for user in allstats(rubululu):
    if(user['stats']['totalGames'] == 0):
        continue
    message_user = f"{user['name']}: "
    message_games = f"Total games: {user['stats']['totalGames']}"
    message_ally = f"As ally: {user['stats']['winAlly']}/{user['stats']['lossAlly']}/{round(user['stats']['winRateAlly']*100)}% "
    message_enemy = f"As enemy: {user['stats']['winEnemy']}/{user['stats']['lossEnemy']}/{round(user['stats']['winRateEnemy']*100)}% \n"

    message += f"{'{0:<20}'.format(message_user[0:20])} "
    message += f"{'{0:<20}'.format(message_games)}"
    message += f"{'{0:<20}'.format(message_ally)}"
    message += f"{message_enemy}"
print(message)

