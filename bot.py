from dotenv import load_dotenv
from mp3 import grab_mp3
from textwrap import dedent
from youtube import get_mp3_by_title
import aiohttp
import asyncio
import os
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import nacl


"""
pyBot
Author: Carter Reynolds
Date Created: 2/15/2023
Last Updated: 2/15/2023
"""

# Get path to current file
path = os.path.dirname(os.path.abspath(__file__)) + "/"

# Get tokens from .env file stored in the same directory as this file
load_dotenv(dotenv_path=path + ".env")
TOKEN = os.getenv("DISCORD_TOKEN")
OVERLORD = int(os.getenv("OVERLORD_DADDY_ID")) # type: ignore
JARVIS = int(os.getenv("JARVIS")) # type: ignore
MASOOD = int(os.getenv("MASOOD")) # type: ignore

powerusers = [OVERLORD, JARVIS, MASOOD]



# Create the discord client
client = discord.Client(intents=discord.Intents.all())

# Dictionary of commands
commands = {
    "!mp3": "Converts a youtube video to mp3 and uploads to channel. Type *!mp3 help* for more info.",
    "!daddy": "Checks if you're daddy.",
    "!dog": "Sends a random dog picture.",
    "!cat": "Sends a random cat picture.",
    "!help": "Displays all commands.",
}

# When the bot is ready
@client.event
async def on_ready():
    print(f"{client.user} is connected to the following guilds:")
    for guild in client.guilds:
        print(f"{guild.name} (id: {guild.id})")

    # set bot status
    await client.change_presence(
        activity=discord.Game(name="!help for commands - otherwise, sadness.")
    )


# When a message is sent
@client.event
async def on_message(message):
    
    # Set up variables we need a lot
    author = message.author
    author_id = message.author.id
    author_msg = message.content
    bot = client.user
    argument = author_msg.split(" ")[1:] # get the argument(s) after the command
    msg_source = message.channel
    
    # if the message starts with a !, it's a command
    if not author_msg.startswith("!"):
        return # do nothing if it's not a command
    
    else: 
        
        if author == bot:
            return 

        ########################################
        #           COMMANDS                   #
        ########################################
        
        ## !MP3 COMMAND ##
        elif author_msg.startswith("!mp3"):
            
            if author_id not in powerusers:
                await msg_source.send("You do not have permission to use this command.")
                return

            if argument == "help":
                await msg_source.send(
                    dedent(
                        """
                        To convert a video, simply enter a valid youtube link after !mp3. 
                        Keep in mind discord has a 8MB file size limit, so anything larger than that will not work.
                        
                        Example: ```!mp3 https://www.youtube.com/watch?v=dQw4w9WgXcQ```
                        Example: ```!mp3 Lil Nas X - Old Town Road```
                        """
                    )
                )
            # if no argument is given, send help message ^^^
            # otherwise, convert the video  
            else:
                
                if "youtube.com" in argument:
                    await msg_source.send("Converting Youtube video to mp3...")
                else:
                    await msg_source.send("Searching for video on youtube...")

                video_url, video_title = get_mp3_by_title(argument)
                data = grab_mp3(video_url)                              # DLs the mp3 and returns the file name
                file_name = data.split(".\\")[1]                        # get the file name and remove path
                
                # check if message author is in a voice channel
                # or if the command is being run with the "~~" argument
                if author.voice is None or "~~" in argument:
                    
                    try:
                        await msg_source.send(file=discord.File(file_name))  # send the mp3 file

                    except discord.errors.HTTPException:
                        await msg_source.send("Error: File too large or other issue.")
                        
                    finally:
                        os.remove(file_name)                # delete the mp3 file
                        
                        if author_id in powerusers:
                            pass                            # don't delete the command message if daddy
                        else:
                            await message.delete()          # delete the command message
                    
                else:
                    
                    # join the voice channel
                    voice_channel = author.voice.channel
                    voice = await voice_channel.connect()
                    
                    voice.play(discord.PCMVolumeTransformer(
                        discord.FFmpegPCMAudio(
                            executable='codec/ffmpeg.exe', 
                            source=file_name
                        ),  volume=0.05
                    ))
                
                    # wait for the mp3 to finish playing or user leaves voice channel
                    while voice.is_playing():
                        
                        # if user leaves voice channel, stop playing and disconnect
                        if len(voice_channel.members) == 1:
                            voice.stop()
                            break
                    
                        await asyncio.sleep(1)
                    
                    await voice.disconnect()
                    
                    os.remove(file_name)
    

        ## !HELP COMMAND ##        
        elif author_msg == "!help":

            help_msg = ""

            for key, value in commands.items():
                help_msg += f"**{key}** - {value}\n"

            await msg_source.send("Help Menu:\n" + help_msg)

        
        ## !DADDY COMMAND ##
        elif author_msg == "!daddy":

            # get the user's id
            user_id: int = author_id

            # get user name from id
            user = await client.fetch_user(OVERLORD)

            if user_id == OVERLORD:
                await msg_source.send("You are daddy!")
            else:
                await msg_source.send(f"You are not daddy! {user} is daddy!")

        
        ## !DOG COMMAND ##
        elif author_msg == "!dog":

            url = await get_dog()
            await msg_source.send(url)
            await message.delete()

        
        ## !CAT COMMAND ##
        elif author_msg == "!cat":

            url = await get_cat()
            await msg_source.send(url)
            await message.delete()
    
    

########################################
#           Helper Functions           #
########################################


async def get_dog():
    async with aiohttp.ClientSession() as session:
        dog_url = "https://random.dog/woof.json"
        async with session.get(dog_url) as resp:
            dog = await resp.json()
            return dog["url"]


async def get_cat():
    async with aiohttp.ClientSession() as session:
        cat_url = "http://aws.random.cat/meow"
        async with session.get(cat_url) as resp:
            cat = await resp.json()
            return cat["file"]


# todo - finish this
async def get_dank_meme():
    async with aiohttp.ClientSession() as session:
        meme_url = "https://meme-api.herokuapp.com/gimme"
        async with session.get(meme_url) as resp:
            meme = await resp.json()
            return meme["url"]
        

@client.event
async def on_error(event, *args, **kwargs):
    with open("err.log", "a") as f:
        if event == "on_message":
            f.write(f"Unhandled message: {args[0]}\n")
        else:
            raise


client.run(TOKEN) # type: ignore
