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
                 unit_name: str = None,
                 lesson_name: str = None,
                 video_id: int = None,
                 current_df: DataFrame = None):
        self.sheets_info = sheets_info
        self.sheet_name = sheet_name
        self.sheet_id = sheet_id
        self.worksheets_ws = worksheets_ws
        self.current_ws = current_worksheet_ws  # Worksheet object for direct cell modifications
        self.worksheet_name = current_worksheet_ws.title if current_worksheet_ws else None
        self.unit_name = unit_name
        self.lesson_name = lesson_name
        self.video_id = video_id
        self.current_df = current_df  # DataFrame to store the current data


def init_embed(name: str, metadata: SheetMetadata) -> Embed:
    """
    Initializes or updates an embed based on the current metadata.
    :param name: The name representing the current view (e.g., 'sheet', 'worksheet', 'unit', 'lesson', 'video').
    :param metadata: The metadata holding the current state of the navigation.
    :return: A Discord Embed object.
    """
    if name == "sheet":
        return Embed(
            title="Google Sheets",
            description="Обери таблицю, яку хочеш відкрити:",
            color=colors['blue']
        )
    elif name == "worksheet":
        return Embed(
            title=f"Worksheet: {metadata.worksheet_name}",
            description="Обери юніт, який хочеш відкрити:",
            color=colors['blue']
        )
    elif name == "unit":
        return Embed(
            title=f"Unit: {metadata.unit_name}",
            description=f"Обери урок, який хочеш відкрити:",
            color=colors['blue']
        )
    elif name == "lesson":
        lesson_meta = fetch_lesson_videos_info(metadata.current_df, metadata.lesson_name)

        actor_role = f"<@&1278343956077215756>"

        # Create an embed for the selected lesson
        embed = Embed(
            title=f"Lesson: {metadata.lesson_name}",
            description="Обери відео, яке хочеш відкрити:",
            color=colors['blue']
        )
        for id in lesson_meta:
            status = lesson_meta[id]['status']
            title = lesson_meta[id]['video_title']
            link = lesson_meta[id]['video_link']
            actor = lesson_meta[id]['actor']

            embed.add_field(name=f"{id}. {title}",
                            value=f"{status}\n"
                                  f"{actor_role}: {actor}\n"  # instead of 'Actor' insert a role in discord
                                  f"{link_in_discord('Відкрити відео в YouTube', link)}",
                            inline=False)

        return embed
    elif name == "video":
        # Ensure video_id is set and valid
        video_info = metadata.current_df.loc[metadata.video_id]
        video_title = video_info.get('ID_simulated', "ID was not found.")
        video_description = video_info.get('Description', 'No description available.')
        video_url = video_info.get('Video URL', 'No URL available.')

        return Embed(
            title=f"Video: {video_title}",
            description=f"Video Info: {video_description}\nVideo URL: {video_url}",
            color=colors['blue']
        )
    return Embed()  # Return an empty embed if the name is not recognized


class EditVideoMsg(View):
    def __init__(self, metadata: SheetMetadata):
        super().__init__(timeout=60)
        self.metadata = metadata
        self.create_buttons()

    def create_buttons(self):
        recorded_status = self.metadata.current_df.loc[self.metadata.video_id, 'Recorded']  # Assuming 'Recorded' exists
        recorded_button = Button(label=f"Recorded: {recorded_status}", style=discord.ButtonStyle.primary)
        recorded_button.callback = self.toggle_recorded_status
        self.add_item(recorded_button)

        # Add more buttons for other editable fields as needed

        back_button = Button(label="Go Back", style=discord.ButtonStyle.secondary)
        back_button.callback = self.go_back_callback
        self.add_item(back_button)

    async def toggle_recorded_status(self, interaction: discord.Interaction):
        current_status = self.metadata.current_df.loc[self.metadata.video_id, 'Recorded']
        new_status = not current_status
        self.metadata.current_df.at[self.metadata.video_id, 'Recorded'] = new_status

        cell_row = self.metadata.video_id + 2  # Assuming the data starts at row 2 in the sheet
        cell_col = self.metadata.current_df.columns.get_loc('Recorded') + 1  # Find the column index for 'Recorded'
        self.metadata.current_ws.update_cell(cell_row, cell_col, new_status)

        self.children[0].label = f"Recorded: {new_status}"
        await interaction.response.edit_message(view=self)  # fix it later
        print_log('INFO', f"Recorded status toggled to {new_status} for video {self.metadata.video_id} by {interaction.user}")

    async def go_back_callback(self, interaction: discord.Interaction):
        embed = init_embed("lesson", self.metadata)
        view = ChooseVideoMsg(self.metadata)
        await interaction.message.edit(embed=embed, view=view)
        print_log('INFO', f'User {interaction.user} went back to the video selection (EditVideoMsg -> VideoButtonView)')


class ChooseVideoMsg(View):
    def __init__(self, metadata: SheetMetadata):
        super().__init__(timeout=60)
        self.metadata = metadata
        self.lesson_df = metadata.current_df[metadata.current_df['Lesson'] == metadata.lesson_name]
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
            self.metadata.video_id = video_id
            video_info = self.lesson_df.loc[video_id]

            # Update embed and metadata before editing
            self.metadata.current_df = self.lesson_df
            embed = init_embed("video", self.metadata)
            view = EditVideoMsg(self.metadata)

            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{video_title} selected for editing by {interaction.user} (VideoButtonView -> EditVideoMsg)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        embed = init_embed("unit", self.metadata)
        view = ChooseLessonMsg(self.metadata)
        await interaction.message.edit(embed=embed, view=view)
        print_log('INFO', f'User {interaction.user} went back to the lesson selection (VideoButtonView -> LessonButtonView)')


class ChooseLessonMsg(View):
    def __init__(self, metadata: SheetMetadata):
        super().__init__(timeout=60)
        self.metadata = metadata
        self.unit_df = metadata.current_df[metadata.current_df['Unit'] == metadata.unit_name]
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
            self.metadata.current_df = self.unit_df
            embed = init_embed("lesson", self.metadata)
            view = ChooseVideoMsg(self.metadata)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{lesson} selected by {interaction.user} (LessonButtonView -> VideoButtonView)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        embed = init_embed("worksheet", self.metadata)
        view = ChooseUnitMsg(self.metadata)
        await interaction.message.edit(embed=embed, view=view)
        print_log('INFO', f'User {interaction.user} went back to the unit selection (LessonButtonView -> UnitButtonView)')


class ChooseUnitMsg(View):
    def __init__(self, metadata: SheetMetadata):
        super().__init__(timeout=60)
        self.metadata = metadata
        self.units = [unit for unit in metadata.current_df['Unit'].unique() if unit]
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
            embed = init_embed("unit", self.metadata)
            view = ChooseLessonMsg(self.metadata)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{unit_name} selected by {interaction.user} (UnitButtonView -> LessonButtonView)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        embed = init_embed("worksheet", self.metadata)
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
            self.metadata.current_df = dataframe
            embed = init_embed("worksheet", self.metadata)
            view = ChooseUnitMsg(self.metadata)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{worksheet_ws.title} selected by {interaction.user} (WorksheetButtonView -> UnitButtonView)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        embed = init_embed("sheet", self.metadata)
        view = ChooseSheetMsg(self.metadata.sheets_info, interaction)
        await interaction.message.edit(embed=embed, view=view)
        print_log('INFO', f'User {interaction.user} went back to the sheet selection (WorksheetButtonView -> SheetsButtonView)')


class ChooseSheetMsg(View):
    def __init__(self, sheets_info: dict[str, str], ctx):
        super().__init__(timeout=60)
        self.sheets_info = sheets_info
        self.ctx = ctx
        self.create_buttons()

    def create_buttons(self):
        for sheet_name, sheet_id in zip(self.sheets_info.keys(), self.sheets_info.values()):
            button = Button(label=sheet_name, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(sheet_name, sheet_id)
            self.add_item(button)

    def create_callback(self, sheet_name: str, sheet_id: str):
        async def callback(interaction: discord.Interaction):
            worksheets_ws = get_all_worksheets(sheet_id)
            metadata = SheetMetadata(
                sheets_info=self.sheets_info,
                sheet_name=sheet_name,
                sheet_id=sheet_id,
                worksheets_ws=worksheets_ws
            )
            embed = init_embed("sheet", metadata)
            view = ChooseWorksheetMsg(metadata, worksheets_ws)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{sheet_name} selected by {interaction.user} (SheetsButtonView -> WorksheetButtonView)')

        return callback


@client.command()
async def show_sheets(ctx):
    sheets_info = get_sheets_info(SHEETS_LINKS)
    embed = init_embed("sheet", SheetMetadata())
    view = ChooseSheetMsg(sheets_info, ctx)
    await ctx.send(embed=embed, view=view)
    print_log('INFO', f'Google Sheets list sent to {ctx.author} (show_sheets)')


if __name__ == "__main__":
    client.run(DS_BOT_TOKEN)
