import discord
from discord.ui import Button, View
from logs_commands import print_log
from common import SheetMetadata, init_embed, update_worksheet_and_df


class ChooseVideoMsg(View):
    def __init__(self, metadata: SheetMetadata, lesson_view: View):
        super().__init__(timeout=60)
        self.lesson_view = lesson_view
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
            view = EditVideoMsg(self.metadata, self.lesson_view)

            await interaction.message.edit(embed=embed, view=view)
            print_log('INFO', f'{video_title} selected for editing by {interaction.user} (VideoButtonView -> EditVideoMsg)')

        return callback

    async def go_back_callback(self, interaction: discord.Interaction):
        embed = init_embed("chooseLesson", self.metadata)
        view = self.lesson_view
        await interaction.message.edit(embed=embed, view=view)
        print_log('INFO', f'User {interaction.user} went back to the lesson selection (VideoButtonView -> LessonButtonView)')


class EditVideoMsg(View):
    def __init__(self, metadata: SheetMetadata, lesson_view: View):
        super().__init__(timeout=60)
        self.metadata = metadata
        self.lesson_view = lesson_view
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
        view = ChooseVideoMsg(self.metadata, lesson_view=self.lesson_view)
        await interaction.message.edit(embed=embed, view=view)
        print_log('INFO', f'User {interaction.user} went back to the video selection (EditVideoMsg -> VideoButtonView)')

