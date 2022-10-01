from config import settings
from discord.ext import commands
import discord


class LeagueCallBot(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        registry_games_channel = self.get_channel(settings.REGISTER_GAME_CHANNEL_ID)

        await registry_games_channel.purge()
        print(f'Purging channel {registry_games_channel.name}...')

        button = discord.ui.Button(label="⚔️ Estou em partida!", style=discord.ButtonStyle.danger)
        button.callback = self.registry_game_callback

        view = discord.ui.View(timeout=2000)
        view.add_item(button)

        embed = discord.Embed(title="Registro de partida",
                            description="Clique no botão abaixo para registrar sua partida!",
                            color=discord.Color.red())

        print(f'Sending message button to channel {registry_games_channel.name}...')

        await registry_games_channel.send(embed=embed, view=view)

    async def registry_game_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Você está em partida!", ephemeral=True)

async def setup(prefix, token):
    intents = discord.Intents.all()

    bot = LeagueCallBot(command_prefix=prefix,
                        intents=intents)

    await bot.start(token)
