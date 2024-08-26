import discord
from discord.ext import commands
import os
import dotenv

from logs_commands import print_log

# Load environment variables
dotenv.load_dotenv()
DS_BOT_TOKEN = os.getenv('DS_BOT_TOKEN')

client = commands.Bot(command_prefix='-', intents=discord.Intents.all())


@client.event
async def on_ready():
    print_log('SUCCESS', f"Bot is ready! Logged in as {client.user}")


@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms")
    print_log('INFO', f"Pong! {round(client.latency * 1000)}ms")

if __name__ == "__main__":
    client.run(DS_BOT_TOKEN)

