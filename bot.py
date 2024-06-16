import json
import discord
import random
import asyncio
import math
from users import userTable
from games import gameManager
from discord.ext import commands
from emojis import emojis
import plotter

path = '/home/felix/inhousebot/'

with open(path+"creds.json") as infile:
    creds = json.load(infile)

with open(path+"config.json") as infile:
    config = json.load(infile)
    channels = config["channels"]

intent = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intent)
users = userTable(path+"users.json")
games = gameManager(path+"games.json", users=users)

async def verifyCorrectChannel(message_channel, channel=channels["Commands"], user=None):
    if message_channel.id != channel:
        await message_channel.send("This command only works in the #commands channel")
        return False
    if user and not users.isUser(user):
        await message_channel.send("Registered users only command. Use /register or see *#instructions* for details.")
        return False
    return True

@bot.command(name='test')
async def testBot(ctx: commands.Context):
    await ctx.message.channel.send('I\'m awake mf')

@bot.command(name='rollall')
async def rollAll(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    
    rollers = []
    for member in bot.get_channel(channels["Lobby"]).members:
        number = random.randint(0,100)
        rollers.append({"Name": member.name, "Number": number})
    if not rollers:
        ctx.message.channel.send("No users in Lobby")
        return
    rollers.sort(key = lambda member : member["Number"], reverse=True)
    text = [f"{'{0:<20}'.format(roller['Name'][:20])} rolled {roller['Number']}" for roller in rollers]
    if len(text) > 10:
        text.insert(10,'---------- Animals! ----------')
    response = '```'+'\n'.join(text)+'```'
    await ctx.message.channel.send(response)


@bot.command(name='roll')
async def rollNumber(ctx: commands.Context):
    number = random.randint(0,100)
    suffix = ''
    if number == 0:
        suffix = "It is literally impossible to be worse at this than you..."
    elif number < 20:
        suffix = "That was pathetic"
    elif number < 40:
        suffix = "Could have been worse I guess"
    elif number < 60:
        suffix = "Mhmm, looking impressive.. or average"
    elif number < 80:
        suffix = "Gang, we got ourselves a high roller"
    elif number < 100:
        suffix = "Amazing, almost perfect!"
    elif number == 100:
        suffix = "OMG OMG OMG OMG OMG!!!!"
    await ctx.message.channel.send(f"{ctx.message.author.name} rolled {number}! {suffix}")

@bot.command(name='lobby')
async def moveToLobby(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    channel = bot.get_channel(channels["Commands"])
    await channel.send('Moving dogs to Lobby...')
    
    move_channels = list({channels["Radiant"],channels["Dire"],ctx.author.voice.channel.id})
    if channels["Lobby"] in move_channels:
        move_channels.remove(channels["Lobby"])
    for _ in range(3):
        for c in move_channels:
            for member in bot.get_channel(c).members:
                await member.move_to(bot.get_channel(channels["Lobby"]))
                await asyncio.sleep(5e-3)
        await asyncio.sleep(2e-2)


@bot.command(name='updateleaderboard')
async def updateLeaderboard(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return
    await updateLeaderboardChannel()

@bot.command(name='updateinstructions')
async def updateInstructions(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return
    with open(path+'README.md') as readme:
        text_blocks = readme.read().split('\n#')
    channel = bot.get_channel(channels["Instructions"])
    await channel.purge()
    for text in text_blocks:
        await channel.send(text)
    await ctx.message.channel.send("Instructions updated, go check'em out")




@bot.command(name='commands')
async def seeCommands(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    await ctx.message.channel.send("See the text channel *#instructions* for a list of commands")



# ----- GAME MANAGEMENT FUNCTIONS -----
@bot.command(name='newgame')
async def makeMatch(ctx: commands.Context):
    if ctx.message.channel.id not in [channels["Games"], channels["Commands"]]:
        await ctx.message.channel.send("This command only works in the #commands and #games channels")
        return
    delete_delay = 12        
    if ctx.message.channel.id == channels["Games"]:
        ctx.message.delete(delay=delete_delay)

    if not users.isUser(ctx.message.author.id):
        error_text = "Only registered users can start games. See *#instructions* for details."
        if ctx.message.channel.id == channels["Games"]:
            await ctx.message.channel.send(error_text, delete_after=delete_delay)
        else:
            await ctx.message.channel.send(error_text)
        return

    channel = bot.get_channel(channels["Games"])
    args = ctx.message.content.split(' ')
    if len(args) > 1:
        name = ' '.join(args[1:])
    else:
        name = users.getName(ctx.message.author.id)
        if name:
            name += "'s game"
    game = games.startNewGame(name)
    if game:
        if ctx.message.channel.id != channels["Games"]:
            await ctx.message.channel.send(f"{users.getName(ctx.message.author.id)} created {games.getGameNameAndId()} in #games...")
        game_message = await channel.send(game)
        games.setMessagePtr(game_message)
        await game_message.add_reaction(bot.get_emoji(emojis.getEmojiId("creep_radiant")))
        await game_message.add_reaction(bot.get_emoji(emojis.getEmojiId("creep_dire")))
        await game_message.add_reaction(bot.get_emoji(emojis.getEmojiId("observer")))
        # await moveToLobby(ctx)
    else:
        error_text = f"A game is already in progress: {games.getGameNameAndId()}"
        if ctx.message.channel.id == channels["Games"]:
            await ctx.message.channel.send(error_text, delete_after=delete_delay)
        else:
            await ctx.message.channel.send(error_text)


@bot.command(name='tip')
async def tipUser(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return

    if not users.isUser(ctx.message.author.id):
        await ctx.message.channel.send("User not registered")
        return

    args = ctx.message.content.split(' ')
    if len(args) < 3:
        await ctx.message.channel.send("Too few arguments. Usage: /tip XXX username")
        return
    
    if not args[1].isnumeric():
        await ctx.message.channel.send("Second argument needs to be numeric")
        return
    value = int(abs(round(float(args[1]))))
    source_user = ctx.message.author.id
    target_user = users.getUserByName(' '.join(args[2:]), return_only_id=True)
    if not target_user:
        await ctx.message.channel.send(f"Couldn't find user {' '.join(args[2:])} to tip")
        return
    if value > -10+users.getPointsBalance(source_user, include_bets=True):
        await ctx.message.channel.send(f"You're trying to tip more than you can afford, you can't tip below 10 points...")
        return
    
    await ctx.message.channel.send(users.tipUser(source_user, target_user, value))
    await updateLeaderboardChannel()


@bot.command(name='bet')
async def placeBet(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return
    if not games.getGame():
        await ctx.message.channel.send("No active game found")
        return

    args = ctx.message.content.split(' ')
    if len(args) == 1:
        await ctx.message.channel.send(f"Usage: /bet XXX team")
        return
    all_in = 'all'
    balance = users.getPointsBalance(ctx.message.author.id)

    if args[1][-1] == '%' and args[1].strip('%').isnumeric():
        args[1] = str(round(balance*abs(int(args[1].strip('%')))/100))

    if not args[1].isnumeric() and args[1] != all_in:
        await ctx.message.channel.send(f"Usage: /bet XXX team")
        return

    bet_value = balance if args[1] == all_in else abs(int(args[1]))
    if bet_value < 0:
        await ctx.message.channel.send(f"Bet is negative... That makes no sense...?")
        return
    if bet_value > balance:
        await ctx.message.channel.send(f"Bet too big, you ain't that packed. You only have {balance} {emojis.getEmoji('points')} to spend")
        return

    player_team = games.getPlayerTeam(ctx.message.author.id)
    if len(args) == 2 and not player_team:
        await ctx.message.channel.send(f"Need to specify team if not joined")
        return
    if len(args) >= 3:
        bet_team = args[2].lower()
    else:
        bet_team = player_team.lower()

    if player_team:
        player_team = player_team.lower()
        if bet_team != player_team:
            await ctx.message.channel.send(f"We got a 322, bro tryin'a bet against his team! Bet ignored, you immoral little bogger!")
            return
    await ctx.message.channel.send(games.addBet(ctx.message.author.id, bet_value, bet_team))
    game_message = games.getMessagePtr()
    await game_message.edit(content=games.showGame())

@bot.command(name='winner')
async def setWinner(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return
    if not games.getGame():
        await ctx.message.channel.send("No active game found")
        return
    args = ctx.message.content.split(' ')
    if len(args) < 2:
        await ctx.message.channel.send(f"Too few arguments. Usage: `/winner radiant/dire/none optional comment`")
        return
    winner = args[1].lower()
    if winner not in ['radiant', 'dire', 'none']:
        await ctx.message.channel.send(f"Invalid winner. Must be **radiant**, **dire** or **none**")
        return
    comment = ' '.join(args[2:])

    await ctx.message.channel.send(f"Game ended with winner: {winner.capitalize()}")
    game_message = games.getMessagePtr()
    await game_message.edit(content=games.setWinner(winner, comment=comment))
    await moveToLobby(ctx)
    await updateLeaderboardChannel()

async def updateLeaderboardChannel():
    channel = bot.get_channel(channels["Leaderboard"])
    await channel.purge()
    message = users.showScoreboard(full=True)
    for submessage in limitSplit(message):
        await channel.send(submessage)


# ----- BOT EVENTS -----
@bot.event
async def on_voice_state_update(member: discord.member.Member, before: discord.VoiceState, after: discord.VoiceState):
    if not after:
        return
    if not after.channel:
        return
    if member.voice.channel is None:
        return
    if after.channel.id not in [channels['Radiant'], channels['Dire']]:
        return    
    
    game_message = games.getMessagePtr()
    if not game_message:
        return
    
    players = games.getPlayers()
    if member.id in players or len(players) >= 10:
        return

    
    
    cache_message = discord.utils.get(bot.cached_messages, id=game_message.id)
    for reaction in [r for r in cache_message.reactions if 'Observer' in str(r.emoji)]:
        async for user in reaction.users():
            if user.id == member.id:
                return
        
    delete_delay = 150
    channel = bot.get_channel(channels["Games"])
    message_text = f"{member.mention} click on your team here, or the observer emoji to spectate!"
    await channel.send(message_text, delete_after=delete_delay)
    await member.move_to(bot.get_channel(channels["Lobby"]))


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.member.Member):
    if bot.user.id == user.id or reaction.message.channel.id != channels['Games']:
        return
    if not 'Dire' in str(reaction.emoji) and not 'Radiant' in str(reaction.emoji):
        return
    current_game = games.getGameMessageId()
    if current_game and current_game == reaction.message.id:
        if not users.isUser(discord_id=user.id):
            channel = bot.get_channel(channels["Commands"])
            await channel.send(users.addUser(user.id, name=user.name))
        team = 'Dire' if 'Dire' in str(reaction.emoji) else 'Radiant'
        if not games.addToTeam(user.id, team):
            await reaction.remove(user)
            return
        game_message = games.getMessagePtr()
        await game_message.edit(content=games.showGame())
        # Add check to see if user is connected, triggers errors in the lgo otherwise.
        # await user.voice.
        await user.move_to(bot.get_channel(channels[team]))
    else:
        if user.id not in games.getPlayersByMessageId(reaction.message.id):
            await reaction.remove(user)

@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: discord.member.Member):
    if reaction.message.channel.id != channels['Games']:
        return
    if 'Dire' not in str(reaction.emoji) and 'Radiant' not in str(reaction.emoji):
        return
    current_game = games.getGameMessageId()
    if current_game and current_game == reaction.message.id:
        team = 'Dire' if 'Dire' in str(reaction.emoji) else 'Radiant'
        games.removeFromTeam(user.id, team)
        game_message = games.getMessagePtr()
        await game_message.edit(content=games.showGame())

# ----- USER MANAGEMENT COMMANDS -----
@bot.command(name='register')
async def registerUser(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    if not users.isUser(discord_id=ctx.message.author.id):
        await ctx.message.channel.send(users.addUser(ctx.message.author.id, name=ctx.message.author.name))
    else:
        await ctx.message.channel.send(f"User already registered")


@bot.command(name='mystats')
async def displayUser(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return
    await ctx.message.channel.send(games.showUserStats(ctx.message.author.id, ['-me']))

def limitSplit(message, limit=2000):
    rows = message.split('\n')
    message_list = []
    submessage=""
    monospace = False
    for row in [r+'\n' for r in rows]:
        if len(submessage)+len(row) > limit-3*monospace: # -3 for potential ```
            message_list.append(submessage+'```'*monospace)
            submessage = '```'*monospace+row
        else:
            if '```' in row:
                monospace = not monospace
            submessage += row
    message_list.append(submessage)
    return message_list

@bot.command(name='stats')
async def displayStats(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return
    args = ctx.message.content.split(' ')[1:]
    message = games.showUserStats(ctx.message.author.id, args)
    for submessage in limitSplit(message):
        await ctx.message.channel.send(submessage)
    return

@bot.command(name='pointsgraph')
async def displayPointsGraph(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return
    args = ctx.message.content.split(' ')
    players = [ctx.message.author.id]
    if len(args)>1:
        other_players = json.loads(' '.join(args[1:]))
        if type(other_players) == list:
            other_players = filter(lambda user: user is not None, [users.getUserFromName(p) for p in other_players])
            players += [p['id'] for p in other_players]
    plotter.createPointsGraph(games, users, players)
    await ctx.channel.send(file=discord.File('plot.png'))

@bot.command(name='scoreboard')
async def displayScoreboard(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    full = False
    args = ctx.message.content.split(' ')
    if len(args) > 1:
        if args[1] == '-full':
            full = True
    message = users.showScoreboard(discord_id = ctx.message.author.id, full=full)
    for submessage in limitSplit(message):
        await ctx.message.channel.send(submessage)

@bot.command(name='leaderboard')
async def displayLeaderboard(ctx: commands.Context):
    await displayScoreboard(ctx)


@bot.command(name='setname')
async def renameUser(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return

    if ' ' not in ctx.message.content:
        await ctx.message.channel.send("Usage: `/setname _yourname_`")
        return
    name = ' '.join(ctx.message.content.split(' ')[1:])
    await ctx.message.channel.send(users.setName(ctx.message.author.id, name))


@bot.command(name='showperks')
async def showPerks(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    message = ""
    for perk, meta in users.getAllPerks().items():
        message += f"## {perk.capitalize()}\n- **Cost:** {meta['cost']}\n- **Perk:** {meta['desc']}\n- **Buy:** /buyperk {perk.lower()}\n"
    await ctx.message.channel.send(message)


@bot.command(name='buyperk')
async def addPerk(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    args = ctx.message.content.split(' ')
    if len(args) != 2:
        quant = "few" if len(args) < 2 else "many"
        await ctx.message.channel.send(f"Too {quant} arguments. Usage: `/buyperk perk_name`")
    else:
        await ctx.message.channel.send(users.addPerk(ctx.message.author.id,args[1].lower()))

### ADMIN COMMANDS ###
banished_users=[]
@bot.command(name='banish')
async def banishUser(ctx: commands.Context):
    if ctx.message.author.id not in config['admins'].values():
        await ctx.message.channel.send("The banish command can only be used by admins, respect authority")
        return
    args = ctx.message.content.split(' ')
    if '-r' in args:
        if args[2] in banished_users:
            banished_users.remove(args[2])
            await ctx.message.channel.send(f"Heroically saved {args[2]}")
        else:
            await ctx.message.channel.send(f"Dafaq? {args[2]} isn't even banned")
    elif '-a' in args:
        banished_users.append(args[2])
        await ctx.message.channel.send(f"User {args[2]} is now banished into eternal exile")
    print(f"Banished users updated: {banished_users}")


async def banishMove(member):
    # == 224608707231744000:
    if not member:
        print(f"Couldn't find member: {member.id}")
        return
    await member.move_to(bot.get_channel(1233755145884663880))
    await bot.get_channel(842045131301060619).send(f"{member.mention} tried to move, but is pathetically banished. Shame, shaaaame, SHAAAAAME!!")


@bot.command(name='purge')
async def purgeChannel(ctx: commands.Context):
    if ctx.message.author.id not in config['admins'].values():
        await ctx.message.channel.send("The purge command can only be used by admins")
        return
    args = ctx.message.content.split(' ')
    if len(args) != 3:
        await ctx.message.channel.send("Incorrect usage")
        return
    if args[1] != '-f' or args[2] != ctx.message.channel.name:
        await ctx.message.channel.send("Incorrect arguments")
        return
    await ctx.message.channel.purge()

@bot.command(name='retroadd')
async def retroAddUser(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    if ctx.message.author.id not in config['admins'].values():
        await ctx.message.channel.send("retroadd is currently admin only")
        return
    args = ctx.message.content.split(' ')
    user_flag = '-user'
    team_flag = '-team'
    game_flag = '-game'

    if (user_flag not in args) or (team_flag not in args) or (game_flag not in args):
        await ctx.message.channel.send(f"This commands need flags for: *{user_flag}*, *{team_flag}* and *{game_flag}*")
        return
    if args[-1] == user_flag or args[-1] == team_flag or args[-1] == game_flag:
        await ctx.message.channel.send(f"retroadd incorrectly parsed, cannot end with flag")
        return
    user_id = args[args.index(user_flag)+1]
    team_id = args[args.index(team_flag)+1].lower()
    game_id = args[args.index(game_flag)+1]
    if not users.isUser(user_id):
        await ctx.message.channel.send(f"Invalid player")
        return
    if team_id not in ['radiant','dire']:
        await ctx.message.channel.send(f"Invalid team")
        return
    if not games.getGame(game_id):
        await ctx.message.channel.send(f"Invalid game")
        return

    game_message_id = games.getGameMessageId(game_id)

    if not games.addToTeam(user_id, team_id, game_id=game_id):
        await ctx.message.channel.send(f"Failed to add user retroactively, player already in game or team full?")
        return
    game_message = await bot.get_channel(channels['Games']).fetch_message(game_message_id)
    await game_message.edit(content=games.showGame(game_id))


@bot.command(name='forceadd')
async def forceAddUser(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    if ctx.message.author.id not in config['admins'].values():
        await ctx.message.channel.send("forceadd is currently admin only")
        return
    

    args = ctx.message.content.split(' ')
    if len(args) < 4:
        await ctx.message.channel.send("Usage: /forceadd game_id team [\"player1_id\",\"player2_id\"]")
        return
    
    # radiant: ["291610583210393604","121279392273006595","291610583210393604","257170522654113792","240529541993332737"]
    # dire: ["154675853064667136","123863796316897283","207903578550042626","170515240184840196","171321137551114240",]

    # RANDOM SHIT FROM HERE DOWN
    if not args[1].isnumeric():
        await ctx.message.channel.send("First argument of forceadd needs to be a numeric game id")
        return
    if not args[2].lower() in ['radiant','dire']:
        await ctx.message.channel.send("Second argument of forceadd needs to be a valid team (radiant or dire)")
        return
    
    try:
        players = json.loads(' '.join(args[3:]),parse_int=True)
    except:
        await ctx.message.channel.send("Third argument of forceadd needs to be a list of players' discord_ids")
        return

    game_id = int(args[1])
    team = args[2].lower()
    game = games.getGame(game_id)
    if not game:
        await ctx.message.channel.send(f"Couldn't find a game with ID \"{args[1]}\"")
        return


    for player in [int(p) for p in players]:
        # addToTeam(self, discord_id, team: str, game_id: int = None):
        if not users.isUser(player):
            await ctx.message.channel.send(f"Player {player} was not found as a registered player")
        elif not games.addToTeam(player, team, game_id):
            await ctx.message.channel.send(f"Couldn't add {player} to the {team} in game {game_id}")
        else:
            await ctx.message.channel.send(f"Added {player} to the {team} in game {game_id}!")

    game_message_id = games.getGameMessageId(game_id)
    game_message = await bot.get_channel(channels['Games']).fetch_message(game_message_id)
    await game_message.edit(content=games.showGame(game_id))


@bot.command(name='changewinner')
async def changeWinner(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return
    if ctx.message.author.id not in config['admins'].values():
        await ctx.message.channel.send("changewinner is only available to admins")
        return
    
    args = ctx.message.content.split(' ')
    if len(args) != 3:
        quant = "few" if len(args) < 3 else "many"
        await ctx.message.channel.send(f"Too {quant} arguments. Usage: `/changewinner game_id team`")
        return
    game_id = args[1]
    if not game_id.isnumeric():
        await ctx.message.channel.send(f"Second argument needs to be numeric game id")
        return
    game_id = int(game_id)
    winner = args[2].lower()
    if winner not in ['radiant','dire']:
        await ctx.message.channel.send(f"Team {winner} is not radiant or dire")
        return


    if not games.getGame(game_id):
        await ctx.message.channel.send(f"No game with id {game_id} found")
        return

    await ctx.message.channel.send(f"Game {game_id} set winner to: {winner.capitalize()}")

    game_message_id = games.getGameMessageId(game_id)
    game_message = await bot.get_channel(channels['Games']).fetch_message(game_message_id)
    await game_message.edit(content=games.setWinner(winner, game_id))
    await updateLeaderboardChannel()


@bot.command(name='updategame')
async def updateGameMessage(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return
    if ctx.message.author.id not in config['admins'].values():
        await ctx.message.channel.send("updategame is only available to admins")
        return
    
    args = ctx.message.content.split(' ')
    if len(args) != 2:
        quant = "few" if len(args) < 2 else "many"
        await ctx.message.channel.send(f"Too {quant} arguments. Usage: `/updategame game_id`")
        return
    game_id = args[1]
    if not game_id.isnumeric():
        await ctx.message.channel.send(f"Second argument needs to be numeric game id")
        return
    game_id = int(game_id)

    if not games.getGame(game_id):
        await ctx.message.channel.send(f"No game with id {game_id} found")
        return

    await ctx.message.channel.send(f"Game {game_id} updated in #games")

    game_message_id = games.getGameMessageId(game_id)
    game_message = await bot.get_channel(channels['Games']).fetch_message(game_message_id)
    await game_message.edit(content=games.showGame(game_id))
    # await updateLeaderboardChannel()


# ------------ RUN BOT ------------
bot.run(creds['token'])
