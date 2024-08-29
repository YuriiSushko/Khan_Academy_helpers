import discord
from discord.ext import commands

import os
import dotenv

from logs_commands import print_log
from sheets import (SHEETS_LINKS, get_sheets_info)
from views.choose_views import SheetMetadata, ChooseSheetMsg, init_embed


# Load environment variables
dotenv.load_dotenv()

DS_BOT_TOKEN = os.getenv('DS_BOT_TOKEN')

client = commands.Bot(command_prefix='-', intents=discord.Intents.all())


@client.event
async def on_ready():
    print_log('SUCCESS', f"Bot is ready! Logged in as {client.user}")


@client.command()
async def ping(ctx):
    await ctx.reply(f"Pong! {round(client.latency * 1000)}ms")
    print_log('INFO', f"Pong! {round(client.latency * 1000)}ms")


@client.command()
async def show_sheets(ctx):
    sheets_info = get_sheets_info(SHEETS_LINKS)
    metadata = SheetMetadata(sheets_info=sheets_info)
    embed = init_embed("chooseSheet", metadata)
    view = ChooseSheetMsg(metadata, ctx)
    await ctx.reply(embed=embed, view=view)
    print_log('INFO', f'Google Sheets list sent to {ctx.author} (show_sheets)')


if __name__ == "__main__":
    client.run(DS_BOT_TOKEN)
