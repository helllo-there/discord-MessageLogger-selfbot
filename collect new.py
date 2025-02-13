import discord
from discord.ext import commands
import asyncio
import os

bot = commands.Bot(command_prefix="!", self_bot=True, chunk_guilds_at_startup=False)

# whitelist: the bot will only log messages from channels in this list
category_whitelist = [ # essentially, you only want to be using this when you're adding new categories - or not? idk
    [GUILD_ID, CATEGORY_ID_1, CATEGORY_ID_2], # guild_id, category_id1, category_id2, ...
    [GUILD_ID, CATEGORY_ID_1]
    ]
channel_whitelist = [CHANNEL_ID_1, CHANNEL_ID_2] #etc
logs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FILE_NAME")
whitelist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whitelist.txt")
bot_prefixes = ("!", "g.", ">", "a!") # bot prefixes, add your own here

def write(file, data): #yes tiny function but the category_channel_append is already a mess so shush
    try:
        with open(file, 'a', encoding="utf-8") as f:
            f.write(data)
    except: #incase message_cleanup returns an empty message
        pass

async def category_channel_append(bot, category_data):
    "Appends all channels in the specified categories to the whitelist, and writes them in a txt so the user can replace the channel_whitelist list, avoiding future discord API calls"
    NEWFILE(whitelist)
    write(whitelist, str(channel_whitelist)[:-1]) #add already existing channels duh
    for data in category_data:
        guild_id, category_ids = data[0], data[1:]
        
        guild = bot.get_guild(guild_id)  # Check cache first, faster
        if guild is None:
            try:
                guild = await bot.fetch_guild(guild_id)  # Fetch if not cached, slower
            except discord.NotFound:
                print(f"Guild ID {guild_id} not found!")
                continue
            except discord.Forbidden:
                print(f"Missing permissions to access Guild ID {guild_id}.")
                continue

        # if nesting is real (if it works, it works)
        for category_id in category_ids:
            category = guild.get_channel(category_id)
            if category and isinstance(category, discord.CategoryChannel):
                for channel in category.channels:
                    if channel.id not in channel_whitelist: # check for duplicates
                        channel_whitelist.append(channel.id)
                        write(whitelist, f", {channel.id}")
                        print(f"Added: {channel.id} from {category.name} in {guild.name}")
                    else:
                        print(f"Channel ID {channel.id} already in whitelist.")
            else:
                print(f"Category ID {category_id} not found in {guild.name}.")
    write(whitelist, "]")

def NEWFILE(file):
    if os.path.exists(file):
        os.remove(file)
    with open(file, 'w') as f:
        pass
    print(f"New file created: {file}")
#NEWFILE(logs) # comment this when we dont want to overwrite old data, just for testing purposes

def message_cleanup(message):
    "removes newlines, user mentions, custom emojis, role mentions, steamcommunity virus link, and sends back empty if the message has a file attached"
    if message.attachments or message.embeds or message.stickers: # if message has a file / gif / sticker attached
        return
    if any(x in message.content.lower() for x in ["steamcommunity", "tenor.com", "cdn.discordapp.com", "media.discordapp.net", "a!afk"] or message.startswith(bot_prefixes)):
        return
    while any(x in message.content for x in ["<a:", "<:", "<#", "<@", "<!"]): #custom emojis, channel mentions, user mentions, role mentions
        start, end = message.content.index("<"), message.content.index(">")
        message.content = message.content[:start] + message.content[end+1:]
    split = message.content.split()
    if split == []:
        return
    print(' '.join(split))
    return ' '.join(split) + "\n"

       
        

@bot.event
async def on_ready():
    await category_channel_append(bot, category_whitelist)
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('Selfbot is ready!')
    print("---------------------------------------------------------------------------------------------------")

@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot or message.channel.id not in channel_whitelist:
        return
    write(logs, message_cleanup(message))
    
bot.run('TOKEN')