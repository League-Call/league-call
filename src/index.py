import asyncio
from config import settings
import app.bot as bot
import discord
import sentry_sdk


print('Loaded settings to:', settings.PROJECT_NAME)
print('In production mode:', not settings.DEBUG)

discord.utils.setup_logging()

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,
)

asyncio.run(bot.setup(settings.PREFIX, settings.TOKEN))
