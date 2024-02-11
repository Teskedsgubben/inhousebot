import json
import discord

with open("creds.json") as infile:
    creds = json.load(infile)

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f"{client.user} är online ffs")

client.run(creds['token'])
