import matplotlib.pyplot as plt

def getPointsUpdates(game:dict):
    payouts = {}
    for player in game['teams'][game['winner'].lower()]:
        payouts.update({player: 50})
    for bet in game['bets']:
        if bet['bet_team'].lower() == game['winner'].lower():
            value = bet['winnings']-bet['bet_value']
        else:
            value = -bet['bet_value']
        if bet['user'] in payouts.keys():
            payouts[bet['user']] += value
        else:
            payouts.update({bet['user']: value})
    return payouts

def getPointsData(games, discord_ids:list):
    data = {}
    for user in discord_ids:
        data.update({user: {'games': [],'points': []}})

    for game in games.getCompletedGames():
        payouts = getPointsUpdates(game)
        for user in discord_ids:
            if user not in list(payouts.keys())+game['teams']['radiant']+game['teams']['dire']:
                continue
            data[user]['games'].append(game['id'])
            
            if not data[user]['points']:
                data[user]['points'].append(100)
            else:
                data[user]['points'].append(data[user]['points'][-1])
            
            if user in payouts.keys():
                data[user]['points'][-1] += payouts[user]
                if data[user]['points'][-1] < 10:
                    data[user]['points'][-1] = 10

    return data

def createPointsGraph(games, users, players):
    data = getPointsData(games, players)
    # import json
    # with open('pointsdata.json','w') as output:
    #     json.dump(data,output)
    for p in players:
        plt.plot(data[p]['games'], data[p]['points'], '.-')
    plt.ylim(0,None)
    plt.title(f"{users.getName(players[0])}'s points over time")
    plt.legend([users.getName(p) for p in players])
    plt.xlabel('Game ID')
    plt.ylabel('Points Balance')
    plt.savefig('plot.png')
    plt.clf()

if __name__ == '__main__':
    from users import userTable
    from games import gameManager
    users = userTable("users.json")
    games = gameManager("games.json", users=users)

    players = [266654734633533440, 278980793139724288, 207903578550042626]#, 223161897468428298]
    createPointsGraph(games, users, players)
    
