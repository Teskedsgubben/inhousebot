import json
import discord
from discord.ext import commands    

with open("creds.json") as infile:
    creds = json.load(infile)

with open("config.json") as infile:
    channels = json.load(infile)
    for c, id in channels.items():
        channels[c] = int(id)


intent = discord.Intents.all()


bot = commands.Bot(command_prefix='/', intents=intent)


@bot.command(name='lobby')
async def moveToLobby(ctx):
    if ctx.message.channel.id == channels["Commands"]:
        channel = bot.get_channel(channels["Commands"])
        await channel.send('Lobby command recieved mf')
        users = []
        for c in [channels["Radiant"],channels["Dire"]]:
            channel = bot.get_channel(c)
            users.extend([member.id for member in channel.members])
        members = [member for member in bot.get_all_members() if member.id in users]
        for member in members:
            await member.move_to(bot.get_channel(channels["Lobby"]))

bot.run(creds['token'])

