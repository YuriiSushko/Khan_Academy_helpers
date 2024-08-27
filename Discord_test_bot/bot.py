import discord
from discord.ext import commands
from discord import Embed
from discord.ui import Button, View

import os
import dotenv
import asyncio

from logs_commands import print_log
from sheets import get_all_worksheets

# Load environment variables
dotenv.load_dotenv()

SHEETS_LINK = os.getenv('SHEETS_LINK')
SHEET_ID = SHEETS_LINK.split('/')[-2]

DS_BOT_TOKEN = os.getenv('DS_BOT_TOKEN')

client = commands.Bot(command_prefix='-', intents=discord.Intents.all())


colors = {
    'red': 0xe74c3c,
    'green': 0x2ecc71,
    'blue': 0x3498db,
    'yellow': 0xf1c40f,
    'orange': 0xe67e22,
    'purple': 0x9b59b6,
    'pink': 0xe91e63,
    'cyan': 0x00ffff,
    'white': 0xffffff,
}


@client.event
async def on_ready():
    print_log('SUCCESS', f"Bot is ready! Logged in as {client.user}")


@client.command()
async def ping(ctx):
    await ctx.reply(f"Pong! {round(client.latency * 1000)}ms")
    print_log('INFO', f"Pong! {round(client.latency * 1000)}ms")


# send an embed message
@client.command()
async def create_embed(ctx):
    embed = Embed(
        title="Embed Title",
        description="This is a sample embed message.",
        color=0x3498db  # Blue color
    )

    # Adding fields to the embed
    embed.add_field(name="Field 1", value="This is the value for field 1", inline=False)
    embed.add_field(name="Field 2", value="This is the value for field 2", inline=True)
    embed.add_field(name="Field 3", value="This is the value for field 3", inline=True)

    # Adding additional details
    embed.set_author(name="Bot Author", icon_url="https://example.com/author_icon.png")
    embed.set_footer(text="This is a footer text")
    embed.set_thumbnail(url="https://example.com/thumbnail.png")
    embed.set_image(url="https://example.com/image.png")

    await ctx.send(embed=embed)
    print_log('INFO', 'Embed message created and sent')


# multiple embed messages with navigation
@client.command()
async def paginate_embeds(ctx):
    # Define the embeds
    embeds = [
        Embed(title="Page 1", description="This is the first page", color=0x3498db),
        Embed(title="Page 2", description="This is the second page", color=0xe74c3c),
        Embed(title="Page 3", description="This is the third page", color=0x2ecc71),
    ]

    message = await ctx.send(embed=embeds[0])  # Send the first embed
    print_log('INFO', 'First embed message sent for pagination')

    # Add reactions for navigation
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

    i = 0
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout=60.0, check=check)
            if str(reaction.emoji) == "➡️" and i < len(embeds) - 1:
                i += 1
                await message.edit(embed=embeds[i])
                await message.remove_reaction(reaction, user)
            elif str(reaction.emoji) == "⬅️" and i > 0:
                i -= 1
                await message.edit(embed=embeds[i])
                await message.remove_reaction(reaction, user)
            else:
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            break
    await message.clear_reactions()
    print_log('INFO', 'Pagination ended and reactions cleared')


# see all worksheets in embed message
@client.command()
async def show_worksheets(ctx):
    worksheets = get_all_worksheets(SHEET_ID)

    embed = Embed(
        title="Worksheets",
        description="Список усіх робочих аркушів у Google Таблиці",
        color=colors['green']
    )

    for worksheet in worksheets:
        worksheet_link = f"[Відкрити в браузері](https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={worksheet.id})"
        embed.add_field(name=worksheet.title, value=worksheet_link, inline=False)

    await ctx.send(embed=embed)
    print_log('INFO', 'Worksheets list sent')


if __name__ == "__main__":
    client.run(DS_BOT_TOKEN)

