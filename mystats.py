import json
from users import userTable

users = userTable('users.json')
fp = open('games.json')
games = json.load(fp)
fp.close()

def stats(user1,user2):
    playerstats = {
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
            lista.append(stats(user1,user2))
            lista.append(users.getName(user2))
    
    lista2 = [stats(user1,user2) for user2 in users.getAllUserIds() if user2 != user1]
    return lista
print(users.getName(541565507476652032))
print(allstats(541565507476652032)[0:4])
#print(users.getUserMMR(users.getAllUserIds()[3]))
#print(users.getName(users.getAllUserIds()[3]))
#print(users.getAllUserIds()[3])

