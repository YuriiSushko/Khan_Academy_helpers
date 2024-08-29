import discord
from discord.ui import Button, View
from gspread import Worksheet

from logs_commands import print_log
from sheets import get_all_worksheets
from common import SheetMetadata, init_embed, worksheet_to_dataframe
from views.edit_video import ChooseVideoMsg


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
            view = ChooseVideoMsg(self.metadata, self)
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