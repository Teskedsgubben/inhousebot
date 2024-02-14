import json
import discord
import random
from users import userTable
from games import gameManager
from discord.ext import commands


path = '/home/felix/inhousebot/'

with open(path+"creds.json") as infile:
    creds = json.load(infile)

with open(path+"config.json") as infile:
    config = json.load(infile)
    channels = config["channels"]
    emojis = config["emojis"]


intent = discord.Intents.all()


bot = commands.Bot(command_prefix='/', intents=intent)
users = userTable(path+"users.json")
games = gameManager(path+"games.json", users=users)

async def verifyCorrectChannel(message_channel, channel=channels["Commands"]):
    if message_channel.id != channel:
        await message_channel.send("This command only works in the #commands channel")
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
    members = []
    for c in [channels["Radiant"],channels["Dire"]]:
        members.extend(bot.get_channel(c).members)
    for member in members:
        await member.move_to(bot.get_channel(channels["Lobby"]))


@bot.command(name='updateinstructions')
async def updateInstructions(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    with open(path+'README.md') as readme:
        text_blocks = readme.read().split('\n#')
    channel = bot.get_channel(channels["Instructions"])
    await channel.purge()
    for text in text_blocks:
        await channel.send(text)
    await ctx.message.channel.send("Instructions updated, go check'em out")

# ----- GAME MANAGEMENT FUNCTIONS -----
@bot.command(name='newgame')
async def makeMatch(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
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
        await ctx.message.channel.send("Creating new game in #games...")
        game_message = await channel.send(game)
        games.setMessagePtr(game_message)    
        await game_message.add_reaction(bot.get_emoji(emojis["Creep_Radiant"]))
        await game_message.add_reaction(bot.get_emoji(emojis["Creep_Dire"]))
    else:
        await ctx.message.channel.send(f"A game is already in progress: {games.getGameNameAndId()}")

# @bot.command(name='bet')
# async def

@bot.command(name='winner')
async def setWinner(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
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
    game_message = games.getMessagePtr()
    await game_message.edit(content=games.setWinner(winner))
    await ctx.message.channel.send(f"Game ended with winner: {winner}")


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.member.Member):
    if bot.user.id == user.id:
        return
    if not await verifyCorrectChannel(reaction.message.channel, channel = channels['Games']):
        return
    if not 'Dire' in str(reaction.emoji) and not 'Radiant' in str(reaction.emoji):
        return
    current_game = games.getCurrentGameMessageId()
    if current_game == reaction.message.id:
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
    if not await verifyCorrectChannel(reaction.message.channel, channel = channels['Games']):
        return
    current_game = games.getCurrentGameMessageId()
    if current_game == reaction.message.id:
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
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    await ctx.message.channel.send(users.showUser(ctx.message.author.id))

@bot.command(name='scoreboard')
async def displayUser(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
        return
    await ctx.message.channel.send(users.showAllUsers())


@bot.command(name='setname')
async def registerUser(ctx: commands.Context):
    if not await verifyCorrectChannel(ctx.message.channel):
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




# ------------ RUN BOT ------------
bot.run(creds['token'])
