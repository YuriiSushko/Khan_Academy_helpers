from discord import Embed
from gspread import Worksheet
from pandas import DataFrame
from sheets import worksheet_to_dataframe, fetch_lesson_videos_info


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


def link_in_discord(text: str, link: str):
    return f"[{text}]({link})"


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

