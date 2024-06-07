import matplotlib.pyplot as plt
import datetime


def getPointsData(games, discord_ids:list):
    data = {}
    for user in discord_ids:
        data.update({user: {'games': [],'points': []}})
    transactions = games.readTransactions()
    
    spends = [{'user':t['user'],      'item_type':t['item_type'], 'item_spec':t['item_spec'], 'cost': int(t['cost']), 'date_time':t['date_time'], 'redeemed': False} for t in transactions if t['user']      in [str(d) for d in discord_ids]]
    tips   = [{'user':t['item_spec'], 'item_type':t['item_type'], 'item_spec':t['item_spec'], 'cost':-int(t['cost']), 'date_time':t['date_time'], 'redeemed': False} for t in transactions if t['item_spec'] in [str(d) for d in discord_ids]]
    transactions = spends + tips

    for user in discord_ids:
        user_spends = [spend for spend in transactions if int(spend['user']) == user]
        for game in games.getCompletedGames():
            if user not in set(game['teams']['radiant'] + game['teams']['dire'] + [bet['user'] for bet in game['bets']]):
                continue
            data[user]['games'].append(game['id'])
            
            if not data[user]['points']:
                data[user]['points'].append(100)
            else:
                data[user]['points'].append(data[user]['points'][-1])
            
            for spend in user_spends:
                game_time = datetime.datetime.strptime(game['created'], '%Y-%m-%d %H:%M')
                spend_time = datetime.datetime.strptime(spend['date_time'], '%Y-%m-%d %H:%M:%S.%f')
                if spend_time <= game_time and not spend['redeemed']:
                    spend['redeemed'] = True
                    data[user]['points'][-1] -= spend['cost']
            perks = [spend['item_spec'] for spend in user_spends if spend['item_type'] == 'perk' and spend['redeemed']]
            payout = games.computeUserPayout(user, game['id'], data[user]['points'][-1], perks=perks)
            data[user]['points'][-1] += payout
    return data

def createPointsGraph(games, users, players):
    data = getPointsData(games, players)
    import json
    with open('pointsdata.json','w') as output:
        json.dump(data,output)
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

    players = [226018564010672128, 123863796316897283, 296612511568887808, 541565507476652032]#[266654734633533440, 278980793139724288, 207903578550042626]#, 223161897468428298]
    createPointsGraph(games, users, players)
    # getPointsData(games, players)
