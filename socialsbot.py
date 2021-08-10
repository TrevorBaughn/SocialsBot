print("Importing libraries...")
while(True):
    try:
        import os

        import discord
        from discord.ext import commands, tasks
        from discord.utils import get
        import configparser
        import scrapetube

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
    print(f'{bot.user} has connected to Discord in:')
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
        self.message = ""

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
    if platform in platforms:
        Social.create(platform, id)

        message = f"Social created with\n ID: `{id}`\n Platform: `{platform}`"
        print(message)
        await ctx.send(message)
    else:
        raise commands.ArgumentParsingError(message=f'{platform} is not a valid platform.')

@bot.command()
@commands.has_permissions(administrator=True)
async def user(ctx, id, user):
    platform = Social.id[id].platform

    if platform == 'youtube':
        try:
            scrapetube.get_channel(user)
        except:
            raise commands.ArgumentParsingError(message=f'{user} channel does not exist.')


    Social.id[id].social_id = user

    message = f"ID: `{id}`\n   Social social ID is now: `{Social.id[id].social_id}`"
    print(message)
    await ctx.send(message)

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

######################################Error Handling

@create.error
async def create_error(ctx, error):
    msg = f'Create Error:\n  {error}'
    print(msg)
    ctx.send(msg)

@user.error
async def user_error(ctx, error):
    msg = f'User Error:\n  {error}'
    print(msg)
    ctx.send(msg)

@channel.error
async def channel_error(ctx, error):
    msg = f'Channel Error:\n  {error}'
    print(msg)
    ctx.send(msg)

@message.error
async def message_error(ctx, error):
    msg = f'Message Error:\n  {error}'
    print(msg)
    ctx.send(msg)

#########################################


bot.run(discord_token)