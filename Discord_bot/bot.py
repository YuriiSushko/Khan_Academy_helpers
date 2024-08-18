from typing import Final
import os
import requests
from google_sheets import get_latest_entry
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Setting up the bot
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)

courses = {1: 'Arithmetic',
           2: 'Precalculus'}

# Adding message functionality
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were disabled (probably))')
        return

    if is_private_respond := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private_respond else await message.channel.send(response)
    except Exception as e:
        print(e)


# Startup for bot
@client.event
async def on_ready() -> None:
    print(f"{client.user} зараз працює!")


# Receive messages
@client.event
async def on_message(message: Message) -> None:
    name: str
    surname: str
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f"[{channel}] {username}: '{user_message}'")
    await send_message(message, user_message)

    video_attachments = [att for att in message.attachments if
                         att.content_type and att.content_type.startswith('video')]

    start: int
    if len(video_attachments) != 0:
        start = 1
    else:
        start = 0

    if video_attachments:
        for i, attachment in enumerate(video_attachments, start=start):
            await download_video(attachment, i)
        await request_user_info(message.author)

    if message.content.startswith('!'):
        try:
            _, name, surname, number = message.content.split(' ', 3)
            entry = get_latest_entry(name, surname, int(number))
            if entry:
                course = courses[number]

            else:
                await message.channel.send('No matching entry found.')
        except ValueError:
            await message.channel.send(f'Usage: ! {name} {surname}')


@client.event
async def download_video(attachment, part_number=0):
    url = attachment.url
    if part_number != 0:
        file_extension = attachment.filename.split('.')[-1]
        filename = f'part_{part_number}.{file_extension}'
    else:
        filename = attachment.filename

    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

    print(f'Downloaded {filename}')


@client.event
async def request_user_info(user):
    try:
        dm_channel = await user.create_dm()
        courses_list = ["1: Arithmetic",
                        "2: Precalculus"]
        await dm_channel.send(f"Будь ласка, напиши ім'я, призвіще та номер свого курсу зі списку:\n {courses_list}")

        def check(m):
            return m.author == user and m.channel == dm_channel

        message = await client.wait_for('message', check=check)
        user_info = message.content.split()
        if len(user_info) >= 3:
            name, surname, number = user_info[0], user_info[1], user_info[2]
            print(f"User info received: Name: {name}, Surname: {surname}, Number: {number}")
            return name, surname, number
        else:
            await dm_channel.send("Please provide your full name and number.")
    except Exception as e:
        print(f"Failed to request user info: {e}")


# Main entry point

def main() -> None:
    client.run(token=TOKEN)


if __name__ == "__main__":
    main()
