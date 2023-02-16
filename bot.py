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

    # don't respond to ourselves
    if message.author == client.user:
        return

    # if the message starts with !mp3
    elif message.content.startswith("!mp3"):
        
        if message.author.id not in powerusers:
            # inform the user they don't have permission to use the command
            await message.channel.send("You do not have permission to use this command.")
            return

        full_discord_msg = message.content
        argument = full_discord_msg.split(" ")[1:]

        # if the user wants help, send them the help message
        if argument == "help":

            await message.channel.send(
                dedent(
                    """
            To convert a video, simply enter a valid youtube link after !mp3. 
            Keep in mind discord has a 8MB file size limit, so anything larger than that will not work.
            
            Example: ```!mp3 https://www.youtube.com/watch?v=dQw4w9WgXcQ```
            Example: ```!mp3 Lil Nas X - Old Town Road```
            """
                )
            )

        # if the user entered anything else try to convert the video
        else:
            
            if "youtube.com" in argument:
                await message.channel.send("Converting Youtube video to mp3...")
            else:
                await message.channel.send("Searching for video on youtube...")

            video_url, video_title = get_mp3_by_title(argument)
            data = grab_mp3(video_url)                              # DLs the mp3 and returns the file name
            file_name = data.split(".\\")[1]                        # get the file name and remove path
            
             # check if message author is in a voice channel
            if message.author.voice is None:
                print("User not in a voice channel - sending mp3 file instead.")
                
                try:
                    await message.channel.send(file=discord.File(file_name))  # send the mp3 file
                    
                    if message.author.id not in powerusers:
                        pass                            # don't delete the command message if daddy
                    else:
                        await message.delete()          # delete the command message
                        
                    os.remove(file_name)                # delete the mp3 file

                except discord.errors.HTTPException:
                    await message.channel.send("Error: File too large or other issue.")
                
            else:
                print("User in a voice channel - playing mp3 in voice channel.")
                
                # join the voice channel
                voice_channel = message.author.voice.channel
                voice = await voice_channel.connect()
                voice.play(discord.FFmpegPCMAudio(executable='codec/ffmpeg.exe', source=file_name))
               
                # wait for the mp3 to finish playing or user leaves voice channel
                while voice.is_playing():
                    if message.author.voice is None:
                        voice.stop()
                        break
                    
                    await asyncio.sleep(1)
                
                # disconnect from the voice channel
                await voice.disconnect()
                
                if message.author.id not in powerusers:
                    pass
                else:
                    await message.delete()
            
    elif message.content == "!help":

        help_msg = ""

        for key, value in commands.items():
            help_msg += f"**{key}** - {value}\n"

        await message.channel.send("Help Menu:\n" + help_msg)

    elif message.content == "!daddy":

        # get the user's id
        user_id: int = message.author.id

        # get user name from id
        user = await client.fetch_user(OVERLORD)

        if user_id == OVERLORD:
            await message.channel.send("You are daddy!")
        else:
            await message.channel.send(f"You are not daddy! {user} is daddy!")

    elif message.content == "!dog":

        url = await get_dog()
        await message.channel.send(url)
        await message.delete()

    elif message.content == "!cat":

        url = await get_cat()
        await message.channel.send(url)
        await message.delete()
    
    
        


@client.event
async def on_error(event, *args, **kwargs):
    with open("err.log", "a") as f:
        if event == "on_message":
            f.write(f"Unhandled message: {args[0]}\n")
        else:
            raise


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


client.run(TOKEN) # type: ignore
