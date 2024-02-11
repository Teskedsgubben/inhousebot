import json
import discord
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


@bot.command(name='lobby')
async def moveToLobby(ctx):
    if ctx.message.channel.id == channels["Commands"]:
        channel = bot.get_channel(channels["Commands"])
        await channel.send('Moving dogs to Lobby...')
        members = []
        for c in [channels["Radiant"],channels["Dire"]]:
            members.extend(bot.get_channel(c).members)
        for member in members:
            await member.move_to(bot.get_channel(channels["Lobby"]))

@bot.command(name='test')
async def testBot(ctx):
    if ctx.message.channel.id == channels["Commands"]:
        await ctx.message.channel.send('I\'m awake mf')

bot.run(creds['token'])

