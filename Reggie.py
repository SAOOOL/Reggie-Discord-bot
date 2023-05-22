#See Readme for operational instructions
#'members' and 'members content' privledges needed

import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.ext.commands import has_permissions, MissingPermissions
from discord import Member
import random
import asyncio

description = '''Hello there, I am at your command. 
You may find all of my capabilites and functionality below!'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

queues = {}
#login acknowledgement 
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    while True:
        await asyncio.sleep(30)
        with open("no_spam.txt", "r+") as file:
            file.truncate(0)
#Spam deterrent and handling
#if spam goes on for more that 10 messages, ALL roles will be removed from user
#Warning is issued at 5 spam messages
@bot.listen('on_message')
async def on_message(message):
    counter = 0
    if message.author.id == bot.user.id:
        return
    with open("no_spam.txt", "r+") as file:
        for lines in file:
            if lines.strip("\n") == str(message.author.id):
                    counter += 1

        file.writelines(f"{str(message.author.id)}\n")
        if counter == 5:
            await message.channel.send("Continue and you will be silenced.")
        if counter == 10:
            await message.channel.send("Shhhh")
            await message.author.edit(roles = [])


#points out the error of commonly misspelled words in the chat
@bot.listen('on_message')
async def listen(message):
    words = [ 'u', 'thier', 'hie','pastim','vacuum', 'alot', 'beleive'  ]
    
    msg = message.content

    deterrant = (":Your spelling is incorrect. ","You spelled {msg} like that?", ":facepalm:")

    for x in words:
        if x.lower() in msg.lower():
            await message.channel.send(random.choice(deterrant))

    ryan = 'ryan'
    if ryan.lower() in msg.lower():
        await message.channel.send("We don't speak that name here.")

#incativity timpout while in a channel
@bot.event
async def on_voice_state_update(member, before, after):
    
    if not member.id == bot.user.id:
        return

    elif before.channel is None:
        voice = after.channel.guild.voice_client
        time = 0
        while True:
            await asyncio.sleep(1)
            time = time + 1
            if voice.is_playing() and not voice.is_paused():
                time = 0
            if time == 300:
                await voice.disconnect()
            if not voice.is_connected():
                break
#Gives the date of when a apecific user has joined the server
@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}')       
#Calls the bot into the channel the requester is in
@bot.command(pass_context = True)
async def join(ctx):
    """Summons me"""
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
    else:
        await ctx.send("Sit in a channel to call upon me")
#Removes the bot from its current channel
@bot.command(pass_context = True)
async def leave(ctx):
    """Removed me from a channel"""
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send('Farewell')
    else:
        await ctx.send('I am not currently in a channel')

#Clears all items in soundboard queue
@bot.command(pass_context = True)
async def clear(ctx):
    """Clears the Queue"""
    queues.clear()

def check_queue(ctx, id):
    if queues[id] != []:
        voice =ctx.guild.voice_client
        source =queues[id].pop(0)
        player = voice.play(source, after=lambda x=None: check_queue(ctx, ctx.message.guild.id))
#Command to play audio from audio files in current directory
@bot.command(pass_context = True)
async def play(ctx, arg):
    """The soundboard"""
    if (ctx.guild.voice_client in  bot.voice_clients) and ctx.voice_client.is_playing(): 
        voice = ctx.guild.voice_client
        song = arg + '.mp3'
        source = FFmpegPCMAudio(song)

        guild_id = ctx.message.guild.id

        if guild_id in queues:
            queues[guild_id].append(source)
            
        else:
            queues[guild_id] = [source]
            
        await ctx.send("Added " + arg +" to queue")

    elif (ctx.guild.voice_client in  bot.voice_clients):
        voice = ctx.guild.voice_client
        song = arg + '.mp3'
        source = FFmpegPCMAudio(song)
        player = voice.play(source, after=lambda x=None: check_queue(ctx, ctx.message.guild.id))

    elif not ctx.guild.voice_client in bot.voice_clients:
        if (ctx.author.voice):
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()

            voice = ctx.guild.voice_client
            song = arg + '.mp3'
            source = FFmpegPCMAudio(song)
            player = voice.play(source, after=lambda x=None: check_queue(ctx, ctx.message.guild.id))

        else:
            await ctx.send("Populate a channel and try again")

def is_connected(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected



#Command will list the available audio files for playback
@bot.command(pass_context = True)
async def voicelines(ctx):
    """List audio"""
    await ctx.send("warselection")

#pause command 
@bot.command(pass_context = True)
async def pause(ctx):
    """pauses music"""
    server = ctx.message.guild
    voice_channel = server.voice_client                
    voice_channel.pause()
   
#resume command
@bot.command(pass_context = True)
async def resume(ctx):
    """Continues paused music"""
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.resume()
    
#skip current audio
@bot.command(pass_context = True)
async def skip(ctx):
    """Skips music in the queue"""
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.stop()
    
#The following are the administrative commands
#appropriate server permission are required
@bot.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *,reason=None):
    """Kicks people"""
    await member.kick(reason=reason)
    await ctx.send(f'{member} has been removed')

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't seem to have that permission...")

@bot.command(name="mute", pass_context=True)
@has_permissions(manage_roles=True)
async def mute(ctx, member: Member):
    """Mutes people"""
    await member.edit(mute=True)

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You don't seem to have that permission...")

@bot.command(name="unmute", pass_context=True)
@has_permissions(manage_roles=True)
async def unmute(ctx, member: Member):
    """Unmutes people"""
    await member.edit(mute=False)

@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("No")

@bot.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *,reason=None):
    """Bans people"""
    await member.kick(reason=reason)
    await ctx.send(f"You have banned {member}. May the universe have mercy on them.")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the authority")

#mutes entire channel in one command 
@bot.command(name="vcmute", pass_context=True)
@has_permissions(manage_roles=True)
async def vcmute(ctx):
    """Mutes ENTIRE channel"""
    vc = ctx.author.voice.channel
    for member in vc.members:
        await member.edit(mute=True)

@vcmute.error
async def vcmute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You don't seem to have that permission...")

#unmutes entire channel
@bot.command(name="vcunmute", pass_context=True)
@has_permissions(manage_roles=True)
async def vcunmute(ctx):
    """Unmutes Entire channel"""
    vc = ctx.author.voice.channel
    for member in vc.members:
        await member.edit(mute=False)

@vcunmute.error
async def vcunmute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("Be patient, you do not have this ability")
    


#token for bot goes here
bot.run('########')
