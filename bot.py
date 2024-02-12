import json
import dota2
import discord
import random
from discord.ext import commands


path = '/home/felix/inhousebot/'

with open(path+"creds.json") as infile:
    creds = json.load(infile)

with open(path+"config.json") as infile:
    channels = json.load(infile)
    for c, id in channels.items():
        channels[c] = int(id)


intent = discord.Intents.all()


bot = commands.Bot(command_prefix='/', intents=intent)

async def verifyCommandsChannel(message_channel):
    if message_channel.id != channels["Commands"]:
        await message_channel.send("This command only works in the #commands channel")
        return False
    return True

@bot.command(name='test')
async def testBot(ctx: commands.Context):
    await ctx.message.channel.send('I\'m awake mf')

@bot.command(name='rollall')
async def rollAll(ctx: commands.Context):
    if not await verifyCommandsChannel(ctx.message.channel):
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
    if not await verifyCommandsChannel(ctx.message.channel):
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
    if not await verifyCommandsChannel(ctx.message.channel):
        return
    with open(path+'README.md') as readme:
        text = readme.read()
    channel = bot.get_channel(channels["Instructions"])
    await channel.purge()
    await channel.send(text)
    await ctx.message.channel.send("Instructions updated, go check'em out")


# ------------ RUN BOT ------------
bot.run(creds['token'])
