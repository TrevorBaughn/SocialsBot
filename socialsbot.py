print("Importing libraries...")
while(True):
    try:
        import os

        import discord
        from discord.ext import commands, tasks
        from discord.utils import get
        import configparser

        print("Imported libraries successfully")
        break
    except:
        print("Failed to import libraries, trying to install them and retrying...")
        os.system('pip3 install discord.py')
        os.system('pip3 install configparser')
        os.system('pip3 install jsons')

        
#setup to grab from config
config = configparser.ConfigParser()
config.read('config.ini')
config.sections()

#set up Social APIs



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

#########################################################################

#makes Social client object
class Socials:
    def __init__(self, platform, id):
        self.social_id = None
        self.discord_channels = []
        self.platform = platform
        self.id = id

#social maker
class CreateSocial:
    def __init__(self):
        self.id = {}

    def create(self, platform, id):
        instance = Socials(platform, id)
        self.id[str(id)] = instance

Social = CreateSocial()

############################################################################



platforms = ['twitter','youtube']
@bot.command()
@commands.has_permissions(administrator=True)
async def create(ctx, platform, id):
    if platform in platforms:
        Social.create(platform, id)

        message = f"Social created with\n ID: {id}\n Platform: {platform}"
        print(message)
        await ctx.send(message)
    else:
        raise commands.ArgumentParsingError(message=f'{platform} is not a valid platform.')

@bot.command()
@commands.has_permissions(administrator=True)
async def user(ctx, id, user):
    platform = Social.id[id].platform

    Social.id[id].social_id = user

    message = f"ID: {id}\n Social social ID is now: {Social.id[id].social_id}"
    print(message)
    await ctx.send(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def channel(ctx, id):
    def check(msg):
        return ctx.author == msg.author
    
    await ctx.send(f"Mention a channel you want {id} to forward to.")
    msg = await bot.wait_for('message', timeout=30.0, check=check)
    msg = msg.content.split("#")[1].split('>')[0]
    channel = get(ctx.guild.channels, id=int(msg))

    Social.id[id].discord_channels.append(channel)

    message = f"ID: {id}\n Social has had #{channel} added to list of channels to send to."
    print(message)
    await ctx.send(message)




bot.run(discord_token)