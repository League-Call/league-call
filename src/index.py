import asyncio
from config import settings
import app.bot as bot
import discord


print('Loaded settings to:', settings.PROJECT_NAME)
print('In production mode:', not settings.DEBUG)

discord.utils.setup_logging()

asyncio.run(bot.setup(settings.PREFIX, settings.TOKEN))
