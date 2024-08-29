import discord
from discord.ext import commands
from discord import Embed
from discord.ui import Button, View

import os
import dotenv

from gspread import Worksheet
from pandas import DataFrame

from logs_commands import print_log
from sheets import (SHEETS_LINKS, get_sheets_info,
                    get_all_worksheets, worksheet_to_dataframe, fetch_lesson_videos_info)

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


def link_in_discord(text: str, link: str):
    return f"[{text}]({link})"


@client.event
async def on_ready():
    print_log('SUCCESS', f"Bot is ready! Logged in as {client.user}")


@client.command()
async def ping(ctx):
    await ctx.reply(f"Pong! {round(client.latency * 1000)}ms")
    print_log('INFO', f"Pong! {round(client.latency * 1000)}ms")


class SheetMetadata:
    def __init__(self,
                 sheets_info: dict[str, str] = None,
                 sheet_name: str = None,
                 sheet_id: str = None,
                 worksheets_ws: list[Worksheet] = None,
                 current_worksheet_ws: Worksheet = None,
                 current_worksheet_df: DataFrame = None,
                 unit_name: str = None,
                 lesson_name: str = None,
                 video_id: int = None):
        self.sheets_info = sheets_info
        self.sheet_name = sheet_name
        self.sheet_id = sheet_id
        self.worksheets_ws = worksheets_ws
        self.current_ws = current_worksheet_ws  # Worksheet object for direct cell modifications
        self.worksheet_df = current_worksheet_df
        self.worksheet_name = current_worksheet_ws.title if current_worksheet_ws else None
        self.unit_name = unit_name
        self.lesson_name = lesson_name
        self.video_id = video_id


def init_embed(name: str, metadata: SheetMetadata) -> Embed:
    """
    Initializes or updates an embed based on the current metadata.
    :param name: The name representing the current view (e.g., 'sheet', 'worksheet', 'unit', 'lesson', 'video').
    :param metadata: The metadata holding the current state of the navigation.
    :return: A Discord Embed object.
    """
    if name == "chooseSheet":
        return Embed(
            title="Google Sheets",
            description="Обери таблицю, яку хочеш відкрити:",
            color=colors['blue']
        )
    elif name == "chooseWorksheet":
        return Embed(
            title="Sheet",
            description="Обери робочий лист, який хочеш відкрити:",
            color=colors['blue']
        )
    elif name == "chooseUnit":
        return Embed(
            title=f"Worksheet: {metadata.worksheet_name}",
            description="Обери юніт, який хочеш відкрити:",
            color=colors['blue']
        )
    elif name == "chooseLesson":
        return Embed(
            title=f"Unit: {metadata.unit_name}",
            description=f"Обери урок, який хочеш відкрити:",
            color=colors['blue']
        )
    elif name == "chooseVideo":
        dataframe = metadata.worksheet_df
        unit_df = dataframe[dataframe['Unit'] == metadata.unit_name]
        lesson_df = unit_df[unit_df['Lesson'] == metadata.lesson_name]
        videos_meta = fetch_lesson_videos_info(lesson_df)

        actor_role = f"<@&1278343956077215756>"

        # Create an embed for the selected lesson
        embed = Embed(
            title=f"Lesson: {metadata.lesson_name}",
            description="Обери відео, яке хочеш відкрити:",
            color=colors['blue']
        )
        for id in videos_meta:
            status = videos_meta[id]['status']
            title = videos_meta[id]['video_title']
            link = videos_meta[id]['video_link']
            actor = videos_meta[id]['actor']

            embed.add_field(name=f"{id}. {title}",
                            value=f"{status}\n"
                                  f"{actor_role}: {actor}\n"  # instead of 'Actor' insert a role in discord
                                  f"{link_in_discord('Відкрити відео в YouTube', link)}",
                            inline=False)

        return embed
    elif name == "editVideo":
        # Ensure video_id is set and valid
        video_info = metadata.worksheet_df.loc[metadata.video_id]
        video_title = video_info.get('ID_simulated', "ID was not found.")
        video_description = video_info.get('Description', 'No description available.')
        video_url = video_info.get('Video URL', 'No URL available.')

        return Embed(
            title=f"Video: {video_title}",
            description=f"Video Info: {video_description}\nVideo URL: {video_url}",
            color=colors['blue']
        )
    return Embed()  # Return an empty embed if the name is not recognized


def update_worksheet_and_df(worksheet_ws: Worksheet, row: int, col: int, new_value) -> DataFrame:
    """
    Updates the Google Sheet table and returns the updated DataFrame.
    :param worksheet_ws:
    :param row:
    :param col:
    :param new_value:
    :return: updated DataFrame
    """

    # Update the Google Sheet (row and col are 0-based in DataFrame, but 1-based in Sheets)
    worksheet_ws.update_cell(row + 2, col + 1, new_value)  # +2 and +1 to adjust for headers

    new_df = worksheet_to_dataframe(worksheet_ws)

    return new_df


class EditVideoMsg(View):
    def __init__(self, metadata: SheetMetadata):
        super().__init__(timeout=60)
        self.metadata = metadata
        self.create_buttons()

    def create_buttons(self):
        recorded_status = self.metadata.worksheet_df.loc[self.metadata.video_id, 'Recorded']
        recorded_button = Button(label=f"Recorded: {recorded_status}", style=discord.ButtonStyle.primary)
        recorded_button.callback = self.toggle_recorded_status
        self.add_item(recorded_button)

        back_button = Button(label="Go Back", style=discord.ButtonStyle.secondary)
        back_button.callback = self.go_back_callback
        self.add_item(back_button)

    async def toggle_recorded_status(self, interaction: discord.Interaction):
        current_status = self.metadata.worksheet_df.loc[self.metadata.video_id, 'Recorded']
        print(f"Current status: {current_status} {type(current_status)}")
        new_status = "FALSE" if current_status == "TRUE" else "TRUE"

        # Find the row and column index in the DataFrame
        row_index = self.metadata.video_id
        col_index = self.metadata.worksheet_df.columns.get_loc('Recorded')

        # Debug: Print current values before update
        print(f"Updating row {row_index}, column {col_index} to {new_status}")
        print(f"Updating cell {self.metadata.worksheet_df.loc[row_index, 'Recorded']} to {new_status}")

        # Update the DataFrame and Google Sheet using the helper function
        updated_df = update_worksheet_and_df(
            self.metadata.current_ws,
            row_index,
            col_index,
            new_status
        )

        # Debug: Print updated DataFrame row
        print(f"Updated DataFrame row: {updated_df.loc[row_index]}")

        # Assign the updated DataFrame back to the metadata
        self.metadata.worksheet_df = updated_df

        # Update the button label
        button = self.children[0]
        button.label = f"Recorded: {new_status}"

        await interaction.message.edit(view=self)
        print_log('INFO', f"Recorded status toggled to {new_status} for video {self.metadata.video_id} by {interaction.user}")

    async def go_back_callback(self, interaction: discord.Interaction):
        embed = init_embed("chooseVideo", self.metadata)
        view = ChooseVideoMsg(self.metadata)
        await interaction.message.edit(embed=embed, view=view)
        print_log('INFO', f'User {interaction.user} went back to the video selection (EditVideoMsg -> VideoButtonView)')


class ChooseVideoMsg(View):
    def __init__(self, metadata: SheetMetadata):
        super().__init__(timeout=60)
        self.metadata = metadata
        self.unit_df = metadata.worksheet_df[metadata.worksheet_df['Unit'] == metadata.unit_name]
        self.lesson_df = self.unit_df[self.unit_df['Lesson'] == metadata.lesson_name]
        self.create_buttons()

    def create_buttons(self):
        for idx, row in self.lesson_df.iterrows():
            video_title = row.get('ID_simulated', "ID was not found.")
            button = Button(label=video_title, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(video_title, idx)
            self.add_item(button)

        back_button = Button(label="Go Back", style=discord.ButtonStyle.secondary)
        back_button.callback = self.go_back_callback
        self.add_item(back_button)

    def create_callback(self, video_title: str, video_id: int):
        async def callback(interaction: discord.Interaction):
            # Ensure video_id is set before accessing the DataFrame
            self.metadata.video_id = self.lesson_df.index[video_id]  # Use DataFrame index

            embed = init_embed("editVideo", self.metadata)
            view = EditVideoMsg(self.metadata)

            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{video_title} selected for editing by {interaction.user} (VideoButtonView -> EditVideoMsg)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        embed = init_embed("chooseLesson", self.metadata)
        view = ChooseLessonMsg(self.metadata)
        await interaction.message.edit(embed=embed, view=view)
        print_log('INFO', f'User {interaction.user} went back to the lesson selection (VideoButtonView -> LessonButtonView)')


class ChooseLessonMsg(View):
    def __init__(self, metadata: SheetMetadata):
        super().__init__(timeout=60)
        self.metadata = metadata
        self.unit_df = metadata.worksheet_df[metadata.worksheet_df['Unit'] == metadata.unit_name]
        self.lessons_names = self.unit_df['Lesson'].unique()
        self.create_buttons()

    def create_buttons(self):
        for lesson_name in self.lessons_names:
            button = Button(label=lesson_name, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(lesson_name)
            self.add_item(button)

        back_button = Button(label="Go Back", style=discord.ButtonStyle.secondary)
        back_button.callback = self.go_back_callback
        self.add_item(back_button)

    def create_callback(self, lesson: str):
        async def callback(interaction: discord.Interaction):
            self.metadata.lesson_name = lesson
            embed = init_embed("chooseVideo", self.metadata)  # Make sure the correct metadata is passed
            view = ChooseVideoMsg(self.metadata)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{lesson} selected by {interaction.user} (LessonButtonView -> VideoButtonView)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        embed = init_embed("chooseUnit", self.metadata)
        view = ChooseUnitMsg(self.metadata)
        await interaction.message.edit(embed=embed, view=view)
        print_log('INFO', f'User {interaction.user} went back to the unit selection (LessonButtonView -> UnitButtonView)')


class ChooseUnitMsg(View):
    def __init__(self, metadata: SheetMetadata):
        super().__init__(timeout=60)
        self.metadata = metadata
        self.units = [unit for unit in metadata.worksheet_df['Unit'].unique() if unit]
        self.create_buttons()

    def create_buttons(self):
        for unit in self.units:
            button = Button(label=unit, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(unit)
            self.add_item(button)

        back_button = Button(label="Go Back", style=discord.ButtonStyle.secondary)
        back_button.callback = self.go_back_callback
        self.add_item(back_button)

    def create_callback(self, unit_name: str):
        async def callback(interaction: discord.Interaction):
            self.metadata.unit_name = unit_name
            embed = init_embed("chooseLesson", self.metadata)
            view = ChooseLessonMsg(self.metadata)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{unit_name} selected by {interaction.user} (UnitButtonView -> LessonButtonView)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        embed = init_embed("chooseWorksheet", self.metadata)
        view = ChooseWorksheetMsg(self.metadata, self.metadata.worksheets_ws)
        await interaction.message.edit(embed=embed, view=view)
        print_log('INFO', f'User {interaction.user} went back to the worksheet selection (UnitButtonView -> WorksheetButtonView)')


class ChooseWorksheetMsg(View):
    def __init__(self, metadata: SheetMetadata, worksheets_ws: list[Worksheet]):
        super().__init__(timeout=60)
        self.metadata = metadata
        self.worksheets_ws = worksheets_ws
        self.create_buttons()

    def create_buttons(self):
        for ws in self.worksheets_ws:
            button = Button(label=ws.title, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(ws)
            self.add_item(button)

        back_button = Button(label="Go Back", style=discord.ButtonStyle.secondary)
        back_button.callback = self.go_back_callback
        self.add_item(back_button)

    def create_callback(self, worksheet_ws: Worksheet):
        async def callback(interaction: discord.Interaction):
            dataframe = worksheet_to_dataframe(worksheet_ws)
            self.metadata.current_ws = worksheet_ws
            self.metadata.worksheet_name = worksheet_ws.title
            self.metadata.worksheet_df = dataframe
            embed = init_embed("chooseUnit", self.metadata)
            view = ChooseUnitMsg(self.metadata)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{worksheet_ws.title} selected by {interaction.user} (WorksheetButtonView -> UnitButtonView)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        embed = init_embed("chooseSheet", self.metadata)
        view = ChooseSheetMsg(self.metadata, interaction)
        await interaction.message.edit(embed=embed, view=view)
        print_log('INFO', f'User {interaction.user} went back to the sheet selection (WorksheetButtonView -> SheetsButtonView)')


class ChooseSheetMsg(View):
    def __init__(self, metadata: SheetMetadata, ctx):
        super().__init__(timeout=60)
        self.metadata = metadata
        self.ctx = ctx
        self.create_buttons()

    def create_buttons(self):
        for sheet_name, sheet_id in zip(self.metadata.sheets_info.keys(), self.metadata.sheets_info.values()):
            button = Button(label=sheet_name, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(sheet_name, sheet_id)
            self.add_item(button)

    def create_callback(self, sheet_name: str, sheet_id: str):
        async def callback(interaction: discord.Interaction):
            worksheets_ws = get_all_worksheets(sheet_id)
            self.metadata.sheet_name = sheet_name
            self.metadata.sheet_id = sheet_id
            self.metadata.worksheets_ws = worksheets_ws
            embed = init_embed("chooseWorksheet", self.metadata)
            view = ChooseWorksheetMsg(self.metadata, worksheets_ws)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{sheet_name} selected by {interaction.user} (SheetsButtonView -> WorksheetButtonView)')

        return callback


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
