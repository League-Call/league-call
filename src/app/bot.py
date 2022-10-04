from config import settings

from discord.ext import commands, tasks
import discord

import services.riot_api as api
from riotwatcher import ApiError
import logging


class LeagueCallBot(commands.Bot):
    async def on_ready(self):
        logging.info(f'Logged on as {self.user}!')
        registry_games_channel = self.get_channel(settings.REGISTER_GAME_CHANNEL_ID)

        await registry_games_channel.purge()
        logging.info(f'Purging channel {registry_games_channel.name}...')

        button = discord.ui.Button(label="Estou em partida!", style=discord.ButtonStyle.danger)
        button.emoji = "⚔️"
        button.callback = self.registry_game_callback

        view = discord.ui.View(timeout=2000)
        view.add_item(button)

        embed = discord.Embed(title="Registro de partida",
                            description="Clique no botão abaixo para registrar sua partida!",
                            color=discord.Color.red())

        logging.info(f'Sending message button to channel {registry_games_channel.name}...\n')

        await registry_games_channel.send(embed=embed, view=view)
        self.league_server = self.get_guild(settings.GUILD_ID)
        self.handle_games.start()

    async def registry_game_callback(self, interaction: discord.Interaction):
        if (not interaction.user.get_role(settings.ROLE_CONFIGURED_ID)):
            return

        try:
            game = api.get_game_by_summoner_name(interaction.user.display_name)
        except ApiError as error:
            if (error.response.status_code == 404):
                await interaction.response.send_message("Infelizmente não encontramos a sua partida", ephemeral=True)
                return
            else:
                logging.error(error)
                await interaction.response.send_message("Ocorreu um erro ao registrar sua partida!", ephemeral=True)
                return
        except Exception as error:
            logging.error(error)
            await interaction.response.send_message("Ocorreu um erro ao registrar sua partida!", ephemeral=True)
            return

        if (game.get('gameType') != 'MATCHED_GAME'):
            await interaction.response.send_message("Infelizmente não encontramos a sua partida!", ephemeral=True)
            return

        channels = await self._create_channels(game, interaction)
        embed = discord.Embed(title="Registro de partida",
                            description="Partida registrada com sucesso!",
                            color=discord.Color.green())

        embed.add_field(name="Blue Side", value=channels[0].mention)
        embed.add_field(name="Red Side", value=channels[1].mention)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _create_channels(self, game, interaction: discord.Interaction) -> list[discord.VoiceChannel]:
        category_name = f"JOGO: {game.get('gameId')}"
        category = discord.utils.get(interaction.guild.categories, name=category_name)

        if (category): return category.channels

        category_overwrite = {
            interaction.guild.default_role: discord.PermissionOverwrite(
                view_channel=False),
        }

        participants = game.get('participants')

        members = [(discord.utils.get(interaction.guild.members, display_name=participant.get('summonerName')),
                    participant.get('teamId'))
                    for participant in participants]

        blueside_overwrite = {
            member: discord.PermissionOverwrite(
                read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True)
                for member, teamId in members if teamId == 100 and member
        }

        redside_overwrite = {
            member: discord.PermissionOverwrite(
                read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True)
                for member, teamId in members if teamId == 200 and member
        }

        category = await interaction.guild.create_category(category_name, overwrites=category_overwrite)

        blueside_channel = await category.create_voice_channel(f'🔊 Blue Side', overwrites=blueside_overwrite)
        redside_channel = await category.create_voice_channel(f'🔊 Red Side', overwrites=redside_overwrite)

        return blueside_channel, redside_channel

    @tasks.loop(minutes=5)
    async def handle_games(self):
        for category in self.league_server.categories:
            if(category.name.startswith('JOGO:')):
                game_id = category.name.split(': ')[1]

                # Verify if game is ended
                try:
                    api.get_match_by_game_id(game_id)
                except ApiError as error:
                    if (error.response.status_code == 404):
                        continue
                    logging.error(error)
                    continue
                except Exception as error:
                    logging.error(error)
                    continue

                for channel in category.channels:
                    await channel.delete()

                await category.delete()


async def setup(prefix, token):
    intents = discord.Intents.all()

    bot = LeagueCallBot(command_prefix=prefix,
                        intents=intents)

    await bot.start(token)
