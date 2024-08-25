import csv
import typing
from typing import Final, Optional
import os
import discord
from Discord_bot.responses import get_response
from google_sheets import get_all_entries
from dotenv import load_dotenv
from discord import Intents, app_commands, Message
from discord.ext import commands
from io import StringIO

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
GUILD_ID: Final[int] = int(os.getenv('GUILD_ID'))


class BotClient(commands.Bot):
    def __init__(self, intents: Intents):
        super().__init__(command_prefix="/", intents=intents)
        self.courses = [
            'Arithmetic',
            'Precalculus',
            'Algebra 2',
            'Basic geometry and measurements'
        ]
        self.roles = [
            "Actor",
            "Translator",
            "Auditor",
            "Post production"
        ]
        self.add_commands()

    def add_commands(self):
        @app_commands.command(name="info", description="Get user information about his work")
        @app_commands.autocomplete(course=self.course_autocomplete)
        @app_commands.autocomplete(role=self.role_autocomplete)
        async def info(interaction: discord.Interaction, name: str, surname: str, course: str, role: str):
            if not await self.validate_inputs(interaction, course, role):
                return
            if role == "Actor":
                await self.send_actor_info(interaction, name, surname, course)

        self.tree.add_command(info)

        @app_commands.command(name="ping", description="Check if the bot is responsive")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message("Pong!")

        self.tree.add_command(ping)

    async def course_autocomplete(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice]:
        return [app_commands.Choice(name=course_name, value=course_name)
                for course_name in self.courses if current.lower() in course_name.lower()]

    async def role_autocomplete(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice]:
        return [app_commands.Choice(name=role, value=role)
                for role in self.roles if current.lower() in role.lower()]

    async def send_actor_info(self, interaction: discord.Interaction, name: str, surname: str, course: str):
        data = get_all_entries(name, surname, course)

        csv_output = StringIO()
        csv_writer = csv.writer(csv_output)

        csv_writer.writerow(['Status', 'Video Title', 'Link'])

        for entry in data:
            status = entry['Status']
            video_title = entry['Video title(En)']
            link = entry['Unnamed: 26']
            csv_writer.writerow([status, video_title, link])

        csv_output.seek(0)
        discord_file = discord.File(fp=csv_output, filename="actor_info.csv")
        await interaction.response.send_message(content="Статус відео/конспекту/тесту: дані додано у вкладений файл",
                                                file=discord_file)

    async def validate_inputs(self, interaction: discord.Interaction, course: str, role: str) -> bool:
        if course not in self.courses:
            await interaction.response.send_message(
                f"Error: Введіть будь ласка курс зі списку:\n{', '.join(self.courses)}", ephemeral=True)
            return False
        if role not in self.roles:
            await interaction.response.send_message(
                f"Error: Введіть будь ласка роль зі списку:\n{', '.join(self.roles)}", ephemeral=True)
            return False
        return True

    async def on_ready(self):
        await self.tree.sync()
        commands = await self.tree.fetch_commands()

        print(f"Commands registered in guild {GUILD_ID}:")
        for command in commands:
            print(f"Command: {command.name}, Description: {command.description}")

        print(f"{self.user} is now online!")

    async def on_message(self, message: Message):
        if message.author == self.user:
            return

        username = str(message.author)
        user_message = message.content
        channel = str(message.channel)

        print(f"[{channel}] {username}: '{user_message}'")
        await self.handle_message(message, user_message)

    async def handle_message(self, message: Message, user_message: str):
        if not user_message:
            print('(Message was empty because intents were disabled or the message was empty)')
            return

        if user_message.startswith('?'):
            await self.send_response(message, user_message[1:], is_private=True)
        elif not user_message.startswith('?'):
            pass
        else:
            await self.send_response(message, user_message, is_private=False)

    async def send_response(self, message: Message, user_message: str, is_private: bool):
        try:
            response = get_response(user_message)
            if is_private:
                await message.author.send(response)
            else:
                await message.channel.send(response)
        except Exception as e:
            print(f"Failed to send message: {e}")


def main() -> None:
    intents: Intents = discord.Intents.default()
    intents.message_content = True
    bot = BotClient(intents=intents)
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
