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


class Restaurant:
    def __init__(self, name, address, website):
        assert name
        self.name = name
        assert address
        self.address = address
        self.website = website

    def __eq__(self, other):
        return isinstance(other, Restaurant) \
               and self.name == other.name \
               and self.address == other.address \
               and self.website == other.website

    def __hash__(self):
        return hash(self.name, self.address, self.website)

    def __str__(self):
        ret = "{} / {}".format(self.name, self.address)
        if self.website:
            ret += " / <{}>".format(self.website)
        return ret


restaurants = []


@bot.event
async def on_ready():
    print("Logged in as {} ({})".format(bot.user.name, bot.user.id))
    for guild in bot.guilds:
        for channel in guild.text_channels:
            print("Running on {}/{}".format(guild.name, channel.name))


dchar = "$"
@bot.command(name="nominate", help="<name> {} <address> {} <website> (website is optional)".format(dchar, dchar))
async def nominate(ctx, *args):
    if (ctx.message.guild.name, ctx.message.channel.name) != (dinner_organization_guild, dinner_organization_channel):
        return
    if len(restaurants) == len(choice_keys):
        await ctx.send("Cannot nominate restaurant: max limit of {} nominations already reached!".format(len(choice_keys)))
        return
    try:
        restaurant_info_string = " ".join(arg.strip() for arg in args)
        restaurant_info = [info_item.strip() for info_item in restaurant_info_string.split(dchar)]
        assert 0 < len(restaurant_info) <= 3
        restaurant = Restaurant(
            name = restaurant_info[0],
            address = restaurant_info[1],
            website = restaurant_info[2] if len(restaurant_info) > 2 and restaurant_info[2] else None
        )
        if restaurant not in restaurants:
            restaurants.append(restaurant)
        log_message = "Added restaurant: {}".format(restaurant)
        await ctx.send(log_message)
        print(log_message)
    except:
        await ctx.send("Command Failed: Usage is !nominate <name> {} <address> {} <website> (website is optional)".format(dchar, dchar))


@bot.command(name="vote", help="Displays nominations for voting")
async def vote(ctx, *args):
    if (ctx.message.guild.name, ctx.message.channel.name) != (dinner_organization_guild, dinner_organization_channel):
        return
    if not restaurants:
        await ctx.send("No nominated restaurants!")
        return
    try:
        assert not args
        restaurant_vote_strings = []
        for choice_key, restaurant in zip(choice_keys, restaurants):
            restaurant_vote_strings.append(":{}:\t{}".format(choice_key, restaurant))
        await ctx.send("Voting Choices (add a reaction to vote here):\n" + "\n".join(restaurant_vote_strings))
        print("Voted")
    except:
        await ctx.send("Command Failed: Usage is !vote")


@bot.command(name="clear", help="Removes all nominations")
async def clear(ctx, *args):
    if (ctx.message.guild.name, ctx.message.channel.name) != (dinner_organization_guild, dinner_organization_channel):
        return
    try:
        assert not args
        global restaurants
        restaurants = []
        log_message = "Removed all restaurants"
        await ctx.send(log_message)
        print(log_message)
    except:
        await ctx.send("Command Failed: Usage is !clear")


bot.run(token)

