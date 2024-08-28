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
                 sheet_name: str = None,
                 sheet_id: str = None,
                 worksheet_ws: Worksheet = None,
                 unit_name: str = None,
                 lesson_name: str = None,
                 video_id: int = None):
        self.sheet_name = sheet_name
        self.sheet_id = sheet_id
        self.worksheet_name = worksheet_ws.title
        self.unit_name = unit_name
        self.lesson_name = lesson_name
        self.video_id = video_id


class EditVideoMsg(View):
    def __init__(self, sheet_name: str, worksheet_name: str, unit_name: str, lesson_name: str, video_id: int,
                 video_df: DataFrame, previous_embed: Embed = None, previous_view: View = None):
        """
        Embed with buttons for editing specific attributes of a video.
        :param sheet_name: Name of the Google Sheet.
        :param worksheet_name: Name of the selected worksheet.
        :param unit_name: Name of the selected unit.
        :param lesson_name: Name of the selected lesson.
        :param video_id: ID (row number) of the selected video.
        :param video_df: DataFrame containing the video data.
        :param previous_embed: The previous embed to return to when going back.
        :param previous_view: The previous view to return to when going back.
        """
        super().__init__(timeout=60)
        self.sheet_name = sheet_name
        self.worksheet_name = worksheet_name
        self.unit_name = unit_name
        self.lesson_name = lesson_name
        self.video_id = video_id
        self.video_df = video_df
        self.previous_embed = previous_embed
        self.previous_view = previous_view
        self.create_buttons()

    def create_buttons(self):
        # Add a toggle button for the "Recorded" status
        recorded_status = self.video_df.loc[self.video_id, 'Recorded']  # Assuming 'Recorded' column exists
        recorded_button = Button(label=f"Recorded: {recorded_status}", style=discord.ButtonStyle.primary)
        recorded_button.callback = self.toggle_recorded_status
        self.add_item(recorded_button)

        # Add more buttons for other editable fields as needed

        # 'Go Back' button to return to the video selection view
        back_button = Button(label="Go Back", style=discord.ButtonStyle.secondary)
        back_button.callback = self.go_back_callback
        self.add_item(back_button)

    async def toggle_recorded_status(self, interaction: discord.Interaction):
        # Toggle the 'Recorded' status
        current_status = self.video_df.loc[self.video_id, 'Recorded']
        new_status = not current_status
        self.video_df.at[self.video_id, 'Recorded'] = new_status

        # Update the status in the Google Sheet (assuming you have a function to update the sheet)
        # Example: update_google_sheet(self.video_df, self.video_id, 'Recorded', new_status)

        # Update the button label
        self.children[0].label = f"Recorded: {new_status}"
        await interaction.response.edit_message(view=self)
        print_log('INFO', f"Recorded status toggled to {new_status} for video {self.video_id} by {interaction.user}")

    async def go_back_callback(self, interaction: discord.Interaction):
        # Go back to the video selection view
        await interaction.message.edit(embed=self.previous_embed, view=self.previous_view)
        print_log('INFO', f'User {interaction.user} went back to the video selection (EditVideoMsg -> VideoButtonView)')


# view for choosing a video within a selected lesson
class ChooseVideoMsg(View):
    def __init__(self, sheet_name: str, worksheet_name: str, unit_name: str, lesson_name: str, unit_df: DataFrame,
                 previous_embed: Embed = None, previous_view: View = None):
        """
        Embed with buttons for selecting a video within a specific lesson.
        :param sheet_name: Name of the Google Sheet.
        :param worksheet_name: Name of the selected worksheet.
        :param unit_name: Name of the selected unit.
        :param lesson_name: Name of the selected lesson.
        :param unit_df: DataFrame containing the lesson data.
        :param previous_embed: The previous embed to return to when going back.
        :param previous_view: The previous view to return to when going back.
        """
        super().__init__(timeout=60)
        self.sheet_name = sheet_name
        self.worksheet_name = worksheet_name
        self.unit_name = unit_name
        self.lesson_name = lesson_name
        self.lesson_df = unit_df[unit_df['Lesson'] == lesson_name]  # filters by lesson name
        self.previous_embed = previous_embed
        self.previous_view = previous_view
        self.create_buttons()

    def create_buttons(self):
        for idx, row in self.lesson_df.iterrows():
            video_title = row.get('ID_simulated', f"ID was not found. Pipec blin")
            button = Button(label=video_title, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(video_title, idx)
            self.add_item(button)

        # 'Go Back' button to return to the lesson selection view
        back_button = Button(label="Go Back", style=discord.ButtonStyle.secondary)
        back_button.callback = self.go_back_callback
        self.add_item(back_button)

    def create_callback(self, video_title: str, video_id: int):
        async def callback(interaction: discord.Interaction):
            # Create an embed for the selected video
            video_info = self.lesson_df.loc[video_id]
            video_description = video_info.get('Description', 'No description available.')
            video_url = video_info.get('Video URL', 'No URL available.')

            embed = Embed(
                title=f"Video: {video_title}",
                description=f"Video Info: {video_description}\nVideo URL: {video_url}",
                color=colors['blue']
            )

            # go to the video edit view
            view = EditVideoMsg(self.sheet_name, self.worksheet_name, self.unit_name, self.lesson_name, video_id,
                                self.lesson_df, previous_embed=embed, previous_view=self)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO',
                      f'{video_title} selected for editing by {interaction.user} (VideoButtonView -> EditVideoMsg)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        # Go back to the lesson selection view
        await interaction.message.edit(embed=self.previous_embed, view=self.previous_view)
        print_log('INFO',
                  f'User {interaction.user} went back to the lesson selection (VideoButtonView -> LessonButtonView)')


# view for choosing a lesson within a selected unit
class ChooseLessonMsg(View):
    def __init__(self, sheet_name: str, worksheet_name: str, unit_name: str, worksheet_df: DataFrame,
                 previous_embed: Embed = None, previous_view: View = None):
        """
        Embed with buttons for selecting a lesson within a specific unit.
        :param sheet_name: Name of the Google Sheet.
        :param worksheet_name: Name of the selected worksheet.
        :param unit_name: Name of the selected unit.
        :param worksheet_df: DataFrame containing the worksheet data.
        :param previous_embed: The previous embed to return to when going back.
        :param previous_view: The previous view to return to when going back.
        """
        super().__init__(timeout=60)
        self.sheet_name = sheet_name
        self.worksheet_name = worksheet_name
        self.unit_name = unit_name
        self.unit_df = worksheet_df[worksheet_df['Unit'] == unit_name]  # Filter lessons by unit name
        self.lessons_names = self.unit_df['Lesson'].unique()  # Assuming 'Lesson' column has the lesson names
        self.previous_embed = previous_embed
        self.previous_view = previous_view
        self.create_buttons()

    def create_buttons(self):
        for lesson_name in self.lessons_names:
            button = Button(label=lesson_name, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(lesson_name)
            self.add_item(button)

        # 'Go Back' button to return to the unit selection view
        back_button = Button(label="Go Back", style=discord.ButtonStyle.secondary)
        back_button.callback = self.go_back_callback
        self.add_item(back_button)

    def create_callback(self, lesson: str):
        async def callback(interaction: discord.Interaction):
            metadata = fetch_lesson_videos_info(self.unit_df, lesson)

            actor_role = f"<@&1278343956077215756>"

            # Create an embed for the selected lesson
            embed = Embed(
                title=f"Lesson: {lesson}",
                description="Обери відео, яке хочеш відкрити:",
                color=colors['blue']
            )

            for id in metadata:
                status = metadata[id]['status']
                title = metadata[id]['video_title']
                link = metadata[id]['video_link']
                actor = metadata[id]['actor']

                embed.add_field(name=f"{id}. {title}",
                                value=f"{status}\n"
                                      f"{actor_role}: {actor}\n"  # instead of 'Actor' insert a role in discord
                                      f"{link_in_discord('Відкрити відео в YouTube', link)}",
                                inline=False)

            # go to the video selection view
            view = ChooseVideoMsg(self.sheet_name, self.worksheet_name, self.unit_name, lesson, self.unit_df,
                                  previous_embed=interaction.message.embeds[0], previous_view=self)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{lesson} selected by {interaction.user} (LessonButtonView -> VideoButtonView)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        # Go back to the unit selection view
        await interaction.message.edit(embed=self.previous_embed, view=self.previous_view)
        print_log('INFO',
                  f'User {interaction.user} went back to the unit selection (LessonButtonView -> UnitButtonView)')


# view for choosing a unit within a selected worksheet
class ChooseUnitMsg(View):
    def __init__(self, sheet_name: str, worksheet_name: str, worksheet_df: DataFrame, previous_embed: Embed = None,
                 previous_view: View = None):
        """
        Embed with buttons for selecting a Unit within a specific worksheet.
        :param sheet_name:
        :param worksheet_name:
        :param worksheet_df:
        :param previous_embed:
        :param previous_view:
        """
        super().__init__(timeout=60)
        self.sheet_name = sheet_name
        self.worksheet_name = worksheet_name
        self.units = [unit for unit in worksheet_df['Unit'].unique() if unit]  # remove empty units
        self.worksheet_df = worksheet_df
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

            # Switch to the lesson selection view
            view = ChooseLessonMsg(self.sheet_name, self.worksheet_name, unit_name, self.worksheet_df,
                                   previous_embed=interaction.message.embeds[0], previous_view=self)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{unit_name} selected by {interaction.user} (UnitButtonView -> LessonButtonView)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        # Go back to the worksheet selection view
        await interaction.message.edit(embed=self.previous_embed, view=self.previous_view)
        print_log('INFO',
                  f'User {interaction.user} went back to the worksheet selection (UnitButtonView -> WorksheetButtonView)')


# view for choosing a worksheet within a selected sheet
class ChooseWorksheetMsg(View):
    def __init__(self, sheet_name: str, worksheets_ws: list[Worksheet], previous_embed: Embed = None,
                 previous_view: View = None):
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
            dataframe = worksheet_to_dataframe(worksheet_ws)
            # Create an embed for the selected worksheet's units
            embed = Embed(
                title=f"Worksheet: {worksheet_ws.title}",
                description=f"Обери юніт, який хочеш відкрити:",
                color=colors['blue']
            )

            # Switch to the unit selection view
            view = ChooseUnitMsg(self.sheet_name, worksheet_ws.title, dataframe,
                                 previous_embed=interaction.message.embeds[0], previous_view=self)
            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO',
                      f'{worksheet_ws.title} selected by {interaction.user} (WorksheetButtonView -> UnitButtonView)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        # Go back to the sheet selection view
        await interaction.message.edit(embed=self.previous_embed, view=self.previous_view)
        print_log('INFO',
                  f'User {interaction.user} went back to the sheet selection (WorksheetButtonView -> SheetsButtonView)')


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
            view = ChooseWorksheetMsg(sheet_name, worksheets_ws, previous_embed=interaction.message.embeds[0],
                                      previous_view=self)
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
