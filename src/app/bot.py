from config import settings
from discord.ext import commands
import discord
import services.riot_api as api
from riotwatcher import ApiError


class LeagueCallBot(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        registry_games_channel = self.get_channel(settings.REGISTER_GAME_CHANNEL_ID)

        await registry_games_channel.purge()
        print(f'Purging channel {registry_games_channel.name}...')

        button = discord.ui.Button(label="Estou em partida!", style=discord.ButtonStyle.danger)
        button.emoji = "⚔️"
        button.callback = self.registry_game_callback

        view = discord.ui.View(timeout=2000)
        view.add_item(button)

        embed = discord.Embed(title="Registro de partida",
                            description="Clique no botão abaixo para registrar sua partida!",
                            color=discord.Color.red())

        print(f'Sending message button to channel {registry_games_channel.name}...')

        await registry_games_channel.send(embed=embed, view=view)

    async def registry_game_callback(self, interaction: discord.Interaction):
        if (not interaction.user.get_role(settings.ROLE_CONFIGURED_ID)):
            return

        try:
            game = api.get_game_by_summoner_name(interaction.user.nick)
        except ApiError as error:
            if (error.response.status_code == 404):
                await interaction.response.send_message("Infelizmente não encontramos a sua partida", ephemeral=True)
                return
            else:
                print(error)
                await interaction.response.send_message("Ocorreu um erro ao registrar sua partida!", ephemeral=True)
                return
        except Exception as error:
            print(error)
            await interaction.response.send_message("Ocorreu um erro ao registrar sua partida!", ephemeral=True)
            return

        await self._create_channels(game, interaction)

        await interaction.response.send_message("Partida registrada com sucesso!", ephemeral=True)

    async def _create_channels(self, game, interaction: discord.Interaction):
        category = discord.utils.get(interaction.guild.categories, name=f"# {game.get('gameId')}")

        if (category):return

        category = await interaction.guild.create_category(f"# {game.get('gameId')}")

        await interaction.guild.create_voice_channel(f'🔊 Blue Side', category=category)
        await interaction.guild.create_voice_channel(f'🔊 Red Side', category=category)


async def setup(prefix, token):
    intents = discord.Intents.all()

    bot = LeagueCallBot(command_prefix=prefix,
                        intents=intents)

    await bot.start(token)
