print("Importing libraries...")
while(True):
    try:
        import os

        import discord
        from discord.ext import commands, tasks
        from discord.utils import get
        import configparser
        import scrapetube
        import pickle

        print("Imported libraries successfully")
        break
    except:
        print("Failed to import libraries, trying to install them and retrying...")
        os.system('pip3 install discord.py')
        os.system('pip3 install configparser')
        os.system('pip3 install scrapetube')



#setup to grab from config
config = configparser.ConfigParser()
config.read('config.ini')
config.sections()

#set up Discord bot
print('\nDISCORDBOT--------')
bot = discord.Client()
print("Client set up")
discord_token = config.get('Discord', 'DiscordToken')
print(f'Discord Token  : {discord_token}')
bot_prefix = config.get('Discord', 'BotPrefix')
bot = commands.Bot(command_prefix = bot_prefix)
print(f'Command Prefix : {bot.command_prefix}')
print('Connecting to Discord...\n')


@bot.event
async def on_ready():
    #wait for the bot to be ready
    await bot.wait_until_ready()

    #print the names of guilds connected to
    print(f'\n{bot.user} has connected to Discord in:')
    for guild in bot.guilds:
        print(f'  {guild.name}(id:{guild.id})')

    print("\nBot initialization complete...\n\n")

    print("Checking for posts...\n")
    check_for_posts.start()

#########################################################################

#makes Social client object
class Socials:
    def __init__(self, platform, id):
        self.social_id = None
        self.discord_channels = []
        self.platform = platform
        self.id = id
        self.message = None

        self.last_url = None

    def check_for_post(self):
        if self.platform == 'youtube' and self.social_id != None:
            return self.check_youtube()

    def check_youtube(self):
        print(f"{self.id} checking for new youtube videos...")

        videos = scrapetube.get_channel(self.social_id)
        for video in videos: #I know this looks inefficient as all hell, but scrapetube doesn't have the docs to help me figure out another way to get 1 video...
            url = f"https://www.youtube.com/watch?v={video['videoId']}"
            break
            
        #checks the last video seen to see if it's the same as the one now
        if self.last_url != url:
            result = url
            self.last_url = url

            return result
        else: 
            result = None



#social maker
class CreateSocial:
    def __init__(self):
        self.id = {}

    def create(self, platform, id):
        instance = Socials(platform, id)
        self.id[str(id)] = instance

Social = CreateSocial()

#load shit
try: #makes directory if it doesn't already exist
    os.mkdir('saves') 
except:
    print("")
print('Loading socials...')
with os.scandir('saves/') as dir_contents:
    for entry in dir_contents:
        file = entry.name
        filename = file.replace('.pkl','')

        instance = Socials(None, filename)

        Social.id[filename] = instance

        with open(f'saves/{file}', 'rb') as inp:
            Social.id[filename] = pickle.load(inp)
print("Socials loaded")
            



        

############################################################################

@tasks.loop(seconds=5)
async def check_for_posts():
    for i in Social.id:
        url = Social.id[i].check_for_post()
        message = Social.id[i].message
        post = f"{message}\n{url}"
        if url is not None:
            print(post)
            for j in Social.id[i].discord_channels:
                channel = bot.get_channel(j)
                await channel.send(post)



platforms = ['youtube']
@bot.command()
@commands.has_permissions(administrator=True)
async def create(ctx, platform, id):
    try:
        int(id)
        raise commands.ArgumentParsingError(message=f"ID can't be a number")
    except:

        if platform in platforms:
            Social.create(platform, id)

            message = f"Social created with\n ID: `{id}`\n Platform: `{platform}`"
            print(message)
            await ctx.send(message)
            save_one(id)
        else:
            raise commands.ArgumentParsingError(message=f'{platform} is not a valid platform.')

@bot.command()
@commands.has_permissions(administrator=True)
async def user(ctx, id, user):
    platform = Social.id[id].platform

    if platform == 'youtube':
        try:
            videos = scrapetube.get_channel(user)
            for video in videos: #I know this looks inefficient as all hell, but scrapetube doesn't have the docs to help me figure out another way to get 1 video...
                break
        except:
            raise commands.ArgumentParsingError(message=f'{user} channel does not exist.')


    Social.id[id].social_id = user

    message = f"ID: `{id}`\n   Social social ID is now: `{Social.id[id].social_id}`"
    print(message)
    await ctx.send(message)
    save_one(id)

@bot.command()
@commands.has_permissions(administrator=True)
async def channel(ctx, id):
    def check(msg):
        return ctx.author == msg.author
    
    await ctx.send(f"Mention a channel you want `{id}` to forward to.")
    msg = await bot.wait_for('message', timeout=30.0, check=check)
    msg = msg.content.split("#")[1].split('>')[0]
    channel = get(ctx.guild.channels, id=int(msg))

    Social.id[id].discord_channels.append(int(msg))

    message = f"ID: `{id}`\n   Social has had #{channel}:{msg} added to list of channels to send to."
    print(message)
    await ctx.send(message)
    save_one(id)

@bot.command()
@commands.has_permissions(administrator=True)
async def message(ctx, id):
    def check(msg):
        return ctx.author == msg.author
    
    await ctx.send(f"What message do you want to go along with the posts `{id}` forwards from.")
    msg = await bot.wait_for('message', timeout=30.0, check=check)
    msg = msg.content

    Social.id[id].message = msg

    message = f'ID: `{id}`\n   Social has had: \n"{msg}"\n, added to be a message to send with the link'
    print(message)
    await ctx.send(message)
    save_one(id)

##
def save_one(id):
    try:
        Social.id[id]
    except NameError:
        var_exists = False
    else:
        var_exists = True
    
    if var_exists:
        with open(f'saves/{id}.pkl', 'wb') as outp:
            pickle.dump(Social.id[id], outp, pickle.HIGHEST_PROTOCOL)

@bot.command()
@commands.has_permissions(administrator=True)
async def delete(ctx, id):
    del Social.id[id]
    path = os.path.realpath(__file__)
    path = path.replace('\socialsbot.py', '')
    path = path + f'\saves\{id}.pkl'
    os.remove(path)

    message = f'ID: `{id}`\n   Deleted'
    print(message)
    await ctx.send(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def check(ctx, id):
    message = f'Checking ID: {id}...'
    print(message)
    await ctx.send(message)

    try:
        check = Social.id[id].id

        message = f"""
ID: `{Social.id[id].id}`
Platform: `{Social.id[id].platform}`
Social ID: `{Social.id[id].social_id}`
Discord Channels: `{Social.id[id].discord_channels}`
Last URL: `{Social.id[id].last_url}`
Message: `{Social.id[id].message}`"""
    except:
        message = f"ID: {id}\n  ID does not exist"

    print(message)
    await ctx.send(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def socials(ctx):
    message = 'List of IDs:'
    for i in Social.id:
        message.append(f"\n- `{i.id}`")
        print(message)
        await ctx.send(message)

##

######################################Error Handling

@create.error
async def create_error(ctx, error):
    error = f'`{error}`'
    msg = f'Create Error:\n  {error}'
    print(msg)
    await ctx.send(msg)

@user.error
async def user_error(ctx, error):
    error = f'`{error}`'
    msg = f'User Error:\n  {error}'
    print(msg)
    await ctx.send(msg)

@channel.error
async def channel_error(ctx, error):
    error = f'`{error}`'
    msg = f'Channel Error:\n  {error}'
    print(msg)
    await ctx.send(msg)

@message.error
async def message_error(ctx, error):
    error = f'`{error}`'
    msg = f'Message Error:\n  {error}'
    print(msg)
    await ctx.send(msg)

@check.error
async def check_error(ctx, error):
    error = f'`{error}`'
    msg = f'Check Error:\n  {error}'
    print(msg)
    await ctx.send(msg)

@delete.error
async def delete_error(ctx, error):
    error = f'`{error}`'
    msg = f'Delete Error:\n  {error}'
    print(msg)
    await ctx.send(msg)

#########################################


bot.run(discord_token)