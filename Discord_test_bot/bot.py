import discord
from discord.ext import commands
from discord import Embed
from discord.ui import Button, View

import os
import dotenv

from gspread import Worksheet

from logs_commands import print_log
from sheets import (SHEETS_LINKS, get_sheets_info,
                    get_all_worksheets, parse_data_by_units)

# Load environment variables
dotenv.load_dotenv()

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


# view for choosing a lesson within a selected unit
class ChooseLessonMsg(View):
    def __init__(self, sheet_name: str, worksheet_name: str, unit_name: str, unit_data: list, previous_embed: Embed = None, previous_view: View = None):
        """
        Embed with buttons for selecting a lesson within a specific unit.
        :param sheet_name:
        :param worksheet_name:
        :param unit_name:
        :param unit_data: List of lessons within the unit.
        :param previous_embed: The previous embed to return to when going back.
        :param previous_view: The previous view to return to when going back.
        """
        super().__init__(timeout=60)
        self.sheet_name = sheet_name
        self.worksheet_name = worksheet_name
        self.unit_name = unit_name
        self.unit_data = unit_data
        self.previous_embed = previous_embed
        self.previous_view = previous_view
        self.create_buttons()

    def __get_all_lessons__(self):
        for id_data in self.unit_data:
            row = id_data[0]



    def create_buttons(self):
        for lesson in self.unit_data:
            button = Button(label=lesson, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(lesson)
            self.add_item(button)

        # Add a "Go Back" button to return to the unit selection view
        back_button = Button(label="Go Back", style=discord.ButtonStyle.secondary)
        back_button.callback = self.go_back_callback
        self.add_item(back_button)

    def create_callback(self, lesson: str):
        async def callback(interaction: discord.Interaction):
            # Create an embed for the selected lesson
            embed = Embed(
                title=f"Lesson: {lesson}",
                description=f"You have selected the lesson: {lesson} from the unit: {self.unit_name}.",
                color=colors['blue']
            )

            # Optionally add more actions for the selected lesson here

            await interaction.message.edit(embed=embed, view=self)
            print_log('INFO', f'{lesson} selected by {interaction.user} (LessonButtonView)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        # Go back to the unit selection view
        await interaction.message.edit(embed=self.previous_embed, view=self.previous_view)
        print_log('INFO', f'User {interaction.user} went back to the unit selection (LessonButtonView -> UnitButtonView)')


# view for choosing a unit within a selected worksheet
class ChooseUnitMsg(View):
    def __init__(self, sheet_name: str, worksheet_name: str, worksheet_data: dict, previous_embed: Embed = None, previous_view: View = None):
        """
        Embed with buttons for selecting a Unit within a specific worksheet.
        :param sheet_name:
        :param worksheet_name:
        :param worksheet_data:
        :param previous_embed:
        :param previous_view:
        """
        super().__init__(timeout=60)
        self.sheet_name = sheet_name
        self.worksheet_name = worksheet_name
        self.units = list(worksheet_data.keys())
        self.previous_embed = previous_embed
        self.previous_view = previous_view
        self.create_buttons()

    def create_buttons(self):
        for unit in self.units:
            button = Button(label=unit, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(unit)
            self.add_item(button)

        # Add a "Go Back" button to return to the worksheet selection view
        back_button = Button(label="Go Back", style=discord.ButtonStyle.secondary)
        back_button.callback = self.go_back_callback
        self.add_item(back_button)

    def create_callback(self, unit_name: str):
        async def callback(interaction: discord.Interaction):
            # Create an embed for the selected unit
            embed = Embed(
                title=f"Unit: {unit_name}",
                description=f"You have selected the unit: {unit_name} from the worksheet: {self.worksheet_name}.",
                color=colors['blue']
            )

            # Optionally add more actions for the selected unit here

            await interaction.message.edit(embed=embed, view=self)
            print_log('INFO', f'{unit_name} selected by {interaction.user} (UnitButtonView)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        # Go back to the worksheet selection view
        await interaction.message.edit(embed=self.previous_embed, view=self.previous_view)
        print_log('INFO', f'User {interaction.user} went back to the worksheet selection (UnitButtonView -> WorksheetButtonView)')


# view for choosing a worksheet within a selected sheet
class ChooseWorksheetMsg(View):
    def __init__(self, sheet_name: str, worksheets_ws: list[Worksheet], previous_embed: Embed = None, previous_view: View = None):
        """
        Embed with buttons for selecting a worksheet within a Google Sheets table.
        :param sheet_name:
        :param worksheets_ws:
        :param previous_embed:
        :param previous_view:
        """
        super().__init__(timeout=60)
        self.sheet_name = sheet_name
        self.worksheets_ws = worksheets_ws
        self.worksheets_names = [ws.title for ws in worksheets_ws]
        self.previous_embed = previous_embed
        self.previous_view = previous_view
        self.create_buttons()

    def create_buttons(self):
        for ws in self.worksheets_ws:
            button = Button(label=ws.title, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(ws)
            self.add_item(button)

        # Add a "Go Back" button to return to the sheet selection view
        back_button = Button(label="Go Back", style=discord.ButtonStyle.secondary)
        back_button.callback = self.go_back_callback
        self.add_item(back_button)

    def create_callback(self, worksheet_ws: Worksheet):
        async def callback(interaction: discord.Interaction):

            data = worksheet_ws.get_all_values()
            parsed_data = parse_data_by_units(data)  # {Unit: [(row, data), ...]}

            # Create an embed for the selected worksheet's units
            embed = Embed(
                title=f"Worksheet: {worksheet_ws.title}",
                description=f"Обери юніт, який хочеш відкрити:",
                color=colors['blue']
            )

            # Switch to the unit selection view
            view = ChooseUnitMsg(self.sheet_name, worksheet_ws.title, parsed_data, previous_embed=interaction.message.embeds[0], previous_view=self)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{worksheet_ws.title} selected by {interaction.user} (WorksheetButtonView -> UnitButtonView)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        # Go back to the sheet selection view
        await interaction.message.edit(embed=self.previous_embed, view=self.previous_view)
        print_log('INFO', f'User {interaction.user} went back to the sheet selection (WorksheetButtonView -> SheetsButtonView)')


# View for choosing a sheet
class ChooseSheetMsg(View):
    def __init__(self, sheets_info: dict[str, str], ctx, embed_title="Google Sheets"):
        """
        Embed with buttons for selecting a Google Sheets document.
        :param sheets_info: {title: 'id'}
        :param ctx:
        :param embed_title:
        """
        super().__init__(timeout=60)
        self.sheets_names = list(sheets_info.keys())
        self.sheets_ids = list(sheets_info.values())
        self.ctx = ctx
        self.embed_title = embed_title
        self.create_buttons()

    def create_buttons(self):
        for sheet_name, sheet_id in zip(self.sheets_names, self.sheets_ids):
            button = Button(label=sheet_name, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(sheet_name, sheet_id)
            self.add_item(button)

    def create_callback(self, sheet_name: str, sheet_id: str):
        async def callback(interaction: discord.Interaction):
            # get worksheets for the selected sheet
            worksheets_ws = get_all_worksheets(sheet_id)

            # prepare the embed for the worksheet selection
            embed = Embed(
                title=sheet_name,
                description="Обери робочий аркуш, який хочеш відкрити:",
                color=colors['blue']
            )

            # go to the worksheet selection view
            view = ChooseWorksheetMsg(sheet_name, worksheets_ws, previous_embed=interaction.message.embeds[0], previous_view=self)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{sheet_name} selected by {interaction.user} (SheetsButtonView -> WorksheetButtonView)')

        return callback


@client.command()
async def show_sheets(ctx):
    sheets_info = get_sheets_info(SHEETS_LINKS)

    # prepare the embed for the sheet selection
    embed = Embed(
        title="Google Sheets",
        description="Обери таблицю, яку хочеш відкрити:",
        color=colors['blue']
    )

    view = ChooseSheetMsg(sheets_info, ctx)

    await ctx.send(embed=embed, view=view)
    print_log('INFO', f'Google Sheets list sent to {ctx.author} (show_sheets)')


if __name__ == "__main__":
    client.run(DS_BOT_TOKEN)
