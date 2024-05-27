import json
import discord
import random
import asyncio
import math
from users import userTable
from games import gameManager
from discord.ext import commands
from emojis import emojis

path = '/home/felix/inhousebot/'

with open(path+"creds.json") as infile:
    creds = json.load(infile)

with open(path+"config.json") as infile:
    config = json.load(infile)
    channels = config["channels"]

game_members = []
force_move = True

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
            await ctx.message.channel.send("Creating new game in #games...")
        game_members = []
        game_message = await channel.send(game)
        games.setMessagePtr(game_message)
        await game_message.add_reaction(bot.get_emoji(emojis.getEmojiId("creep_radiant")))
        await game_message.add_reaction(bot.get_emoji(emojis.getEmojiId("creep_dire")))
        await game_message.add_reaction(bot.get_emoji(emojis.getEmojiId("observer")))
        await moveToLobby(ctx)
    else:
        error_text = f"A game is already in progress: {games.getGameNameAndId()}"
        if ctx.message.channel.id == channels["Games"]:
            await ctx.message.channel.send(error_text, delete_after=delete_delay)
        else:
            await ctx.message.channel.send(error_text)

@bot.command(name='forcemove')
async def toggleForceMove(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return
    args = ctx.message.content.split(' ')
    if len(args) == 1:
        force_move = not force_move
    elif args[1].lower() == 'on':
        force_move = True
    elif args[1].lower() == 'off':
        force_move = False
    else:
        await ctx.message.channel.send(f"Usage: \"/forcemove\" to toggle on/off, or specify state with \"/forcemove on\" or \"/forcemove off\".")
        return
    
    if force_move:
        await ctx.message.channel.send(f"Force move ON. Players now have to use the game message reactions to change channel.")
    else:
        await ctx.message.channel.send(f"Force move OFF. Players can now move freely between inhouse voice channels.")



@bot.command(name='bet')
async def placeBet(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel, user=ctx.message.author.id):
        return
    if not games.getGame():
        await ctx.message.channel.send("No active game found")
        return

    args = ctx.message.content.split(' ')
    if len(args) == 1:
        await ctx.message.channel.send(f"Usage: /bet XXX [team]")
        return
    all_in = 'all'
    if not args[1].isnumeric() and args[1] != all_in:
        await ctx.message.channel.send(f"Usage: /bet XXX [team]")
        return

    balance = users.getPointsBalance(ctx.message.author.id)
    bet_value = balance if args[1] == all_in else abs(int(args[1])) 
    if bet_value > balance:
        await ctx.message.channel.send(f"Bet too big, you ain't that packed. You have {balance} {emojis.getEmoji('points')}")
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
    if len(args) != 2:
        quant = "few" if len(args) < 2 else "many"
        await ctx.message.channel.send(f"Too {quant} arguments. Usage: `/winner radiant/dire/none`")
        return
    winner = args[1].lower()
    if winner not in ['radiant', 'dire', 'none']:
        await ctx.message.channel.send(f"Invalid winner. Must be **radiant**, **dire** or **none**")
        return
    await ctx.message.channel.send(f"Game ended with winner: {winner}")
    game_message = games.getMessagePtr()
    await game_message.edit(content=games.setWinner(winner))
    await moveToLobby(ctx)
    await updateLeaderboard()

async def updateLeaderboard():
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
    # if member.id in banished_users:
    #     banishMove(member)
    #     return
    # if not force_move:
    #     return
    
    if after.channel.id not in [channels['Radiant'], channels['Dire']]:
        return
    if member.id in game_members:
        return
    

    # game_message = games.getMessagePtr()
    # if not game_message:
    #     return

    players = games.getPlayers()
    if member.id in players or len(players) >= 10:
        return

    
    # cache_message = discord.utils.get(bot.cached_messages, id=game_message.id)
    # for reaction in [r for r in cache_message.reactions if 'Radiant' in str(r.emoji) or 'Dire' in str(r.emoji) or 'Observer' in str(r.emoji)]:
    #     async for user in reaction.users():
    #         if user.id == member.id:
    #             return
        
    # print(f"Moving {member.id} because not in {players} or observer")
    # if member.id not in players and member.id not in game_members:
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
        if 'Observer' in str(reaction.emoji):
            game_members.append(user.id)
        return
    game_members.append(user.id)
    current_game = games.getCurrentGameMessageId()
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
    current_game = games.getCurrentGameMessageId()
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

@bot.command(name='addid')
async def addId(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    args = ctx.message.content.split(' ')
    if len(args) != 3:
        quant = "few" if len(args) < 3 else "many"
        await ctx.message.channel.send(f"Too {quant} arguments. Usage: `/addid id_type id_value`")
    else:
        await ctx.message.channel.send(users.addCustomId(ctx.message.author.id,args[1],args[2]))

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

    game_message_id = games.getCurrentGameMessageId(game_id)

    if not games.addToTeam(user_id, team_id, game_id=game_id):
        await ctx.message.channel.send(f"Failed to add user retroactively, player already in game or team full?")
        return
    game_message = bot.get_channel(channels['Games']).fetch_message(game_message_id)
    await game_message.edit(content=games.showGame(game_id))



# ------------ RUN BOT ------------
bot.run(creds['token'])
