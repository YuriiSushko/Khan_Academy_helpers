import typing
from typing import Final, Optional, Tuple
import os
import discord
import requests
from google_sheets import get_latest_entry
from dotenv import load_dotenv
from discord import Intents, Client, Message, app_commands
from discord.ext import commands
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')


class BotClient(commands.Bot):
    def __init__(self, intents: Intents):
        super().__init__(command_prefix="/", intents=intents)
        self.courses = [
            'Arithmetic',
            'Precalculus'
        ]
        self.add_commands()

    def add_commands(self):
        @app_commands.command(name="info", description="Get user course information")
        @app_commands.autocomplete(course=self.course_autocomplete)
        async def info(interaction: discord.Interaction, name: str, surname: str, course: str):
            try:
                # Simulate fetching an entry
                entry = True if course in self.courses else False
                course_name = course if entry else "Жодної інформації"
                await interaction.response.send_message(f"Course: {course_name}")
            except Exception as e:
                await interaction.response.send_message(f"Не вийшло отримати інформацію за запитом, причина: {e}")

        self.tree.add_command(info)

    async def course_autocomplete(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice]:
        choices = [
            app_commands.Choice(name=course_name, value=course_name)
            for course_name in self.courses
        ]
        return [choice for choice in choices if current.lower() in choice.name.lower()]

    async def on_ready(self):
        await self.tree.sync()
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
        elif user_message.startswith('!'):
            await self.process_command(message)
        else:
            await self.send_response(message, user_message, is_private=False)

    async def process_command(self, message: Message):
        parts = message.content.strip().split(' ', 3)

        command, *args = parts

        valid_commands = ['info']
        if command[1:] not in valid_commands:
            await message.channel.send(f"Error: Невідома команда '{command[1:]}'")
            return

        if command[1:] == 'info':
            if len(args) == 3:
                name, surname, course = args
                try:
                    course in self.courses
                except ValueError:
                    await message.channel.send(f"Error: Введіть будь ласка курс зі списку:\n {self.courses}")
                    return
                await self.user_info(message.channel, name, surname, course)
            else:
                await message.channel.send(
                    "Error: Будь ласка, напишіть команду в такому форматі '!command_name surname course'.")
                return

    async def send_response(self, message: Message, user_message: str, is_private: bool):
        try:
            response = get_response(user_message)
            if is_private:
                await message.author.send(response)
            else:
                await message.channel.send(response)
        except Exception as e:
            print(f"Failed to send message: {e}")

    async def download_video(self, attachment: discord.Attachment, part_number: int = 0):
        try:
            url = attachment.url
            file_extension = attachment.filename.split('.')[-1]
            filename = f'part_{part_number}.{file_extension}' if part_number else attachment.filename

            response = requests.get(url)
            with open(filename, 'wb') as f:
                f.write(response.content)

            print(f'Downloaded {filename}')
        except Exception as e:
            print(f"Failed to download video: {e}")


def main() -> None:
    intents: Intents = discord.Intents.default()
    intents.message_content = True

    bot = BotClient(intents=intents)
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
