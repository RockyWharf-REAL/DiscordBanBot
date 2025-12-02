import datetime
import time

import discord
import re
import os
from discord.ext import commands
from dotenv import load_dotenv
from discord.utils import get
import logging

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!',intents=intents)

### This is for removing characters that are considered "useless"
def string_formater(line = ""):
    new_line = line

    new_line = new_line.lower()
    new_line =re.sub(r'[^a-z]','', new_line)

    #print(f'Line {line} -> {new_line}')
    return new_line

string_formater("--Lest turn THis INTO a *** D325erent S538Tr83822{{i{}ng")

starting_letter = 'a'
current_letter = starting_letter
def abc_sentence_check(line):
    #Checks for an empty string.
    if len(line) < 1:
        return False

    #Check current letter is the same as strings first letter.
    if line[0] == current_letter:
        # Maybe increment current letter, but I might make that outside this function.
        return True
    else:
        # Not same, return false and restart.
        return False

"""
        role_name = "Public Humiliation"
        member = message.author
        role = discord.utils.get(member.guild.roles, name=role_name)
"""

def progress_letter():
    global current_letter
    current_letter = chr(ord(current_letter) + 1)

async def time_out_role_change(message):
    # Message is bad (did not go a-z)
    global current_letter
    current_letter = starting_letter
    await message.channel.send(f"{message.author.mention} has made you reset.")
    await give_member_role(message, "Public Humiliation")

    try:
        # Define the duration using datetime.timedelta
        duration = datetime.timedelta(seconds=15)
        reason = "You entered a invalid input for the rules."
        await message.author.timeout(duration, reason=reason)
        print(f'{message.author} has been timed out for {duration} seconds. Reason: {reason or "None"}')
    except discord.Forbidden:
        print("I do not have permission to time out this user. Please check my role hierarchy and permissions.")
    except Exception as e:
        print(f"An error occurred: {e}")

async def give_member_role(message, role_name):
    member = message.author
    role = discord.utils.get(member.guild.roles, name=role_name)
    await message.author.add_roles(role)

@bot.event
async def on_ready():
    print(f'Bot is ready!')

@bot.event
async def on_message(message):
    global current_letter
    # Return if message is by bot
    #print(f'Found message {message}')
    if message.author == bot.user:
        return

    #Checking if we are in the specific channel.
    channel_id = os.getenv('CHANNEL_ID')
    if message.channel.id != channel_id:
        return

    await bot.process_commands(message)

    #This is to try and stop the "A is a stupid trend." spam
    words = message.content.lower().split()
    if len(words[0]) == 1:
        if current_letter == 'i':
            progress_letter()
            return
        if current_letter == 'a':
            progress_letter()
            return
        await time_out_role_change(message)
        return

    formated_message = string_formater(message.content)
    if abc_sentence_check(formated_message):
        # Message is good
        #await message.channel.send("Your message is valid!")
        print(current_letter)
        if current_letter == 'z':
            role_name = "Bragging Rights"
            try:
                # We should give the player the Z rule
                await give_member_role(message, role_name)
                # Send a congratulations message!
            except Exception as e:
                print(f'Failed to give {message.author.name} role {role_name}: {e}')

            # We should reset the current letter
            current_letter = starting_letter
            print(f'Trying to run clear_messages...')

            await clear_messages(message)
            await message.channel.send(f"Congratulations {message.author}, you figured it out!")
        else:
            progress_letter()
    else:
        # Message is bad (did not go a-z)
        await time_out_role_change(message)


@bot.command()
@commands.has_role('Admin')
async def clear_messages(ctx):
    print(f'Clearing Messages...')
    try:
        await ctx.channel.purge(limit=None)
        await ctx.channel.send('Channel has been wiped.')
        print(f'Messages cleared!')
    except Exception as e:
        await ctx.channel.send(f'Something went wrong with clear_messages: {str(e)}')

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN, log_handler=handler)