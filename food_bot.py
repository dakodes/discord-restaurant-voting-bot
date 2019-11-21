#!/usr/bin/env python3

import os
import string
import inflect
from discord.ext import commands
from dotenv import load_dotenv

# Boilerplate setup
inflect_engine = inflect.engine()
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')

# Parameters
dinner_organization_guild = os.getenv("GUILD")
dinner_organization_channel = os.getenv("CHANNEL")
choice_keys = ["regional_indicator_{}".format(letter) for letter in list(string.ascii_lowercase)] \
            + [inflect_engine.number_to_words(number) for number in range(0, 10)]


restaurants = []


@bot.event
async def on_ready():
    print("Logged in as {} ({})".format(bot.user.name, bot.user.id))
    for guild in bot.guilds:
        for channel in guild.text_channels:
            print("Running on {}/{}".format(guild.name, channel.name))


@bot.command(name="nominate", help="<restaurant>")
async def nominate(ctx, *args):
    if (ctx.message.guild.name, ctx.message.channel.name) != (dinner_organization_guild, dinner_organization_channel):
        return
    if not args:
        await ctx.send("Command Failed: Usage is !nominate <restaurant>")
        return
    if len(restaurants) == len(choice_keys):
        await ctx.send("Cannot nominate restaurant: max limit of {} nominations already reached!".format(len(choice_keys)))
        return
    restaurant = " ".join(arg.strip() for arg in args)
    if restaurant not in restaurants:
        restaurants.append(restaurant)
    log_message = "Added restaurant: {}".format(restaurant)
    await ctx.send(log_message)
    print(log_message)


@bot.command(name="vote", help="Displays nominations for voting")
async def vote(ctx, *args):
    if (ctx.message.guild.name, ctx.message.channel.name) != (dinner_organization_guild, dinner_organization_channel):
        return
    if args:
        await ctx.send("Command Failed: Usage is !vote")
        return
    if not restaurants:
        await ctx.send("No nominated restaurants!")
        return
    restaurant_vote_strings = [":{}:\t{}".format(choice_key, restaurant) for choice_key, restaurant in zip(choice_keys, restaurants)]
    await ctx.send("Voting Choices (add a reaction to vote here):\n" + "\n".join(restaurant_vote_strings))
    print("Voted")


@bot.command(name="clear", help="Removes all nominations")
async def clear(ctx, *args):
    if (ctx.message.guild.name, ctx.message.channel.name) != (dinner_organization_guild, dinner_organization_channel):
        return
    if args:
        await ctx.send("Command Failed: Usage is !clear")
        return
    global restaurants
    restaurants = []
    log_message = "Removed all restaurants"
    await ctx.send(log_message)
    print(log_message)


bot.run(token)

