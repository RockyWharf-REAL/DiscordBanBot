import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
import time

user_kick_counter_dict = {}
json_file = '../user_kick_counter.json'

try:
    with open(json_file, 'r', encoding='utf-8') as file:
        print(f"Found {json_file}. Loading...")
        user_kick_counter_dict = json.load(file)
        print(f"Loaded {json_file}.")
except:
    print("NO USER JSON FILE, MAKING NOW...")
    with open(json_file, 'w', encoding='utf-8') as file:
        # Use json.dump() to write the Python dictionary to the file in JSON format.
        json.dump(user_kick_counter_dict, file)  # indent for pretty printing

    print(f"Data successfully written to '{json_file}'.")


load_dotenv()
token = os.getenv('DISCORD_TOKEN')
channel_id = os.getenv('CHANNEL_ID')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True
intents.moderation = True

bot = commands.Bot(command_prefix='!', intents=intents)

#Formats strings way they can be compared later.
def string_formater(input):
    input = input.lower()
    input = input.replace(' ', '')
    input = input.replace('\n', '')
    input = input.replace('\\', '')
    input = input.replace('&', '')
    input = input.replace(';', '')
    input = input.replace('-', '')
    input = input.replace('_', '')
    #Spamming punctuations fix.
    input = input.replace(',,', '')
    input = input.replace('..', '')
    input = input.replace('.,', '')
    input = input.replace('~~', '')
    input = input.replace('!!', '')
    input = input.replace('****', '')
    input = input.replace('|||', '')
    input = input.replace('<<<', '')
    input = input.replace('>>>', '')
    input = input.replace('??', '')
    input = input.replace('!?', '')
    return input

def write_dict_to_file(diction, file_name):
    print("Trying to write in dict to file...")
    try:
        with open(file_name, 'w') as file:
            json.dump(diction, file)
        print(f'Was able to write to {file_name}.')
    except:
        print(f'Failed to write to {file_name}.')

def user_kick_and_write(message, diction, file_name):
    print(f"Trying to write in user kick and write... {diction[message.author.name]}")
    diction[message.author.name] += 1
    print("Added to user_kick_counter_dict.")
    write_dict_to_file(diction, file_name)

async def role_giver(author, formated_message, condition_word, role_name):
    give_role = discord.utils.get(author.guild.roles, name=role_name)
    if condition_word in formated_message:
        print(f"{role_name} in:{formated_message}")
        print(f"Giving {author.name} role {give_role.name}")
        await author.add_roles(give_role)
        print(f"Gave {author.name} role {give_role.name}")
    else:
        print(f"{condition_word} not in:{formated_message}")


@bot.event
async def on_ready():
    print(f'Logged on as {bot.user.name}!')

@bot.event
async def on_member_join(member):
    global user_kick_counter_dict
    print(f'Member joined {member.name}')
    #Getting our roles
    role_good = discord.utils.get(member.guild.roles, name='Good')
    role_failed = discord.utils.get(member.guild.roles, name='Failed')

    # Assigning role, and join count
    # Have they joined before?
    print(f'Checking if {member.name} is in user dict.')
    print(f'keys {user_kick_counter_dict.keys()}')
    if member.name in user_kick_counter_dict.keys():
        # They have joined before, but have they been kicked before?
        if user_kick_counter_dict[member.name] > 0:
            # They have been kicked
            print(f'{member.name} has been kicked before.')
            await member.add_roles(role_failed)
        else:
            # They have not been kicked
            print(f'{member.name} has not kicked before. Adding good role')
            await member.add_roles(role_good)
    else:
        #They are new, they could never have been kicked
        print(f'{member.name} has joined before. Adding good role')
        await member.add_roles(role_good)
        user_kick_counter_dict[member.name] = 0
        print(f'Trying to write {member.name}, to {json_file}')
        write_dict_to_file(user_kick_counter_dict, file_name)



@bot.event
async def on_message_edit(before, after):
    #print("RAN")
    if before.author == bot.user:
        print(f'Bot Return Triggered')
        return

    if message.channel.id != channel_id:
        return

    print(f"Message edited from {before.content} to {after.content} by {after.author.name}")
    if before.content != after.content:
        await after.channel.send(f"{after.author.display_name} edited their message from[{before.content}] -> [{after.content}] and has been punished.")
        user_kick_and_write(before, user_kick_counter_dict, json_file)
        await after.author.kick(reason="You edited your message! History stays where it is!")

@bot.event
async def on_message(message):
    #global user_kick_counter_dict
    #print(f'Received message from {message.author}: {message.content}')
    #Return if it's the bot
    if message.author == bot.user:
        print(f'Bot Return Triggered')
        return

    if message.channel.id != channel_id:
        return


    good_role = discord.utils.get(message.guild.roles, name='Good')
    failed_role = discord.utils.get(message.guild.roles, name='Failed')
    if not good_role in message.author.roles and not failed_role in message.author.roles:
        try:
            await message.channel.send(f'{message.author.mention} does not have a role. KICK')
            user_kick_and_write(message, user_kick_counter_dict, json_file)
            await message.author.kick(reason="Bro, keep your role.")
        except:
            print(f'Failed to do {message.author} in has role checker.')
        return

    await bot.process_commands(message)

    start_time = time.perf_counter()
    # Needs to be before checking empty.
    messages_to_check = []
    if message.attachments:
        for attachment in message.attachments:
            messages_to_check.append(string_formater(str(attachment.filename)))
            messages_to_check.append(string_formater(str(attachment.url)))
            print(f'attachment name : {attachment.filename}')
            print(f'attachment name : {attachment.url}')
    if message.stickers:
        for sticker in message.stickers:
            messages_to_check.append(string_formater(str(sticker.url)))
    messages_to_check.append(string_formater(str(message.content)))

    for item in messages_to_check:
        await role_giver(message.author, item, "bluey", "?")
        await role_giver(message.author, item, "mresistance", "RESIST")

    found = False
    print('Opening Messages list...')
    with open("messages.txt", 'r', encoding='utf-8') as file:
        for line in file:
            line = string_formater(str(line))
            #print(line,message.content)
            if len(line) < 1:
                continue

            if line in messages_to_check:
                found = True
                print(f"Banning {message.author.display_name}")
                try:
                    await message.channel.send(f"{message.author.display_name} has failed the challenge [{user_kick_counter_dict[message.author.name] + 1}]. They said [{line}].")
                    # increase the number of times they have been kicked.
                    print(f'Author : {message.author.name}')
                    print(f'keys : {user_kick_counter_dict.keys()}')
                    if message.author.name in user_kick_counter_dict.keys():
                        print(f"Adding 1 to {message.author.name} kick counter. their counter is now [{user_kick_counter_dict[message.author.name]}].")
                        user_kick_and_write(message, user_kick_counter_dict, json_file)
                    else:
                        print(f"User {message.author.name} is not in the user_kick_counter_dict")
                    await message.author.kick(reason="You sent a message someone else already sent dumb dumb >:/")
                    break
                    #Add a break here, if you don't want it to spam for every time someone was banned a specific way.
                except:
                    print(f"Banning {message.author.name} failed.")
                    break
            # The scanner did not find anything similar enough to kick the user for, lets add it to the list!
        if not found:
            with open("messages.txt", "a", encoding='utf-8') as file:
                for mes in messages_to_check:
                    if len(mes) < 1:
                        continue
                    add = mes
                    print(f"adding [{add}] to messages list.")
                    file.write(add + '\n')

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Took {elapsed_time:.6f} seconds to search database.")
    """         
    if "shit" in message.content.lower():
        # We need to kick the user for now.
        await message.delete()
        await message.channel.send(f"{message.author.mention} dont use that word!")
    """

@bot.command()
async def reset_messages(ctx):
    await ctx.send(f"Resetting messages from {ctx.message.channel.name}..")

"""
@bot.command()
async def assign_role(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Good')
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} You are assigned to Good!")
    else:
        await ctx.send(f"{ctx.author.mention} Role NA")
"""

"""
@bot.command()
async def remove_role(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Good')
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} You are removed from Good!")
    else:
        await ctx.send(f"{ctx.author.mention} Role NA")
"""

bot.run(token, log_handler=handler, log_level=logging.DEBUG)