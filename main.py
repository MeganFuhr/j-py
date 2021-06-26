import requests
import json
import os
import discord
import random
import pymongo
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand , SlashCommandOptionType , SlashContext
from discord_slash.utils.manage_commands import create_option

load_dotenv()
giphy = os.environ.get('GIPHY_API')
discordToken = os.environ.get('DISCORD_TOKEN')
jid = os.environ.get('DISCORD_ID')
gid = [int(os.environ.get('GUILDS_ID'))]
secretWord = os.environ.get('SECRET_WORD')

mongo = pymongo.MongoClient(os.environ.get('MONGOURI'))

insultsCol = mongo["BingaBonga"]["insults"]
quotesCol = mongo["BingaBonga"]["quotes"]
praisesCol = mongo["BingaBonga"]["praises"]
jgifsCol = mongo["BingaBonga"]["jgifs"]

insultsCount = insultsCol.count_documents({})
quotesCount = quotesCol.count_documents({})
praisesCount = praisesCol.count_documents({})
jgifsCount = jgifsCol.count_documents({})

squote = ["Gabagool over here. :spaghetti: "]

url = "http://api.giphy.com/v1/gifs/random"
stparams = {
    "tag": "swear trek",
    "api_key": giphy,
    "limit": "1"
    }

client = commands.Bot(command_prefix='!')
slash = SlashCommand(client , sync_commands=True)

options= [{
    "name": "ZilloBot",
    "description": "Tell ZilloBot what to do.",
    "options": [
        {
            "name": "insult",
            "description": "insult j",
            "type": 3,
            "required": True
        },
        {
            "name": "quote",
            "description": "quote j",
            "type": 3,
            "required": True

        },
        {
            "name": "praise",
            "description": "praise j",
            "type": 3,
            "required": True
        },
                {
            "name": "gif",
            "description": "random J gif",
            "type": 3,
            "required": True
        }
    ]
}]
async def addinsult(newInsult):
    insultsCol.insert_one(newInsult)

async def addQuote(newQuote):
    quotesCol.insert_one(newQuote)

async def addPraise(newPraise):
    praisesCol.insert_one(newPraise)

@client.event
async def on_ready():
    print("Bot is logged in as {0.user}".format(client))

@slash.slash(name = 'st', guild_ids=gid, description="Return a random Swear Trek gif.")
async def st(ctx : SlashCommand ):
    r = requests.get(url, stparams)
    rJson = json.loads(r.text)
    embedUrl = (rJson['data']['images']['downsized']['url'])
    embed = discord.Embed(
        title="Swear Trek!",
        color=discord.Colour.purple())
    embed.set_image(url=embedUrl)
    await ctx.send(embed=embed)

@slash.slash(name = 'j', guild_ids=gid, description="OPTIONS: Insult, Quote, Praise, Gif")
async def j(ctx : SlashCommand , options = options):
    if (options.lower() == "insult"):
        doc = insultsCol.find()[random.randrange(insultsCount)]
        await ctx.send(" <@{}>, ".format(jid) + doc["insult"] + " :middle_finger:")
    elif (options.lower() == "quote"):
        doc = quotesCol.find()[random.randrange(quotesCount)]
        await ctx.send(doc["quote"] + " -<@{}>".format(jid))
    elif (options.lower() == "praise"):
        doc = praisesCol.find()[random.randrange(praisesCount)]
        await ctx.send("<@{}>, ".format(jid) + doc["praise"] + " :heartpulse:")
    elif (options.lower() == "gif"):
        embedUrl = jgifsCol.find()[random.randrange(jgifsCount)]['jgifs']
        embed = discord.Embed(
            title="J!",
            color=discord.Colour.dark_teal())
        embed.set_image(url=embedUrl)
        await ctx.send(embed=embed)
    else:
        return

@slash.slash(name = 'sopranos', guild_ids=gid, description="Heeeyyyy I'm walkin' here.")
async def sopranos(ctx : SlashCommand):
    await ctx.send(squote[0])

@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    if secretWord in message.content:
        embed = discord.Embed(
        title="SECRET WORD!!!!!",
        color=discord.Colour.red(),
        description = "You used the SECRET WORD :confetti_ball: :tada:   " + secretWord.upper() + "!!!!!!"
        )
        embed.set_image(url="https://media.giphy.com/media/NvXLlQvvXSmQM/giphy.gif")
        await message.channel.send(embed=embed)
    if message.content.startswith('!add-insult'):
        if message.author.id == int(jid):
            await message.channel.send(" <@{}>".format(jid) + ", you are not authorized to add insults.")
        else:
            insult = message.content.split("!add-insult").pop()
            insult = insult.strip()
            insert = { "insult" : "{}".format(insult) }       

            await addinsult(insert)
            await message.channel.send('The insult "{}" has been added.'.format(insult))
    elif message.content.startswith('!add-quote'):
        if message.author.id != int(jid):
            await message.channel.send("<@{}>".format(message.author.id) + ", you are not authorized to add quotes.")
        else:
            quote = message.content.split("!add-quote").pop()
            quote = quote.strip()
            insert = { "quote" : "{}".format(quote) }       

            await addQuote(insert)
            await message.channel.send('The quote "{}" has been added.'.format(quote))
    elif message.content.startswith('!add-praise'):
            praise = message.content.split("!add-praise").pop()
            praise = praise.strip()
            insert = { "praise" : "{}".format(praise) }       

            await addPraise(insert)
            await message.channel.send('The praise "{}" has been added.'.format(praise))   

client.run(discordToken)