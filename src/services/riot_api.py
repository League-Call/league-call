from riotwatcher import LolWatcher
from config import settings

_api = LolWatcher(settings.RIOT_API_KEY)


def _get_summoner_by_name(name):
    return _api.summoner.by_name(settings.LOL_REGION, name)

def _get_game_by_summoner_id(summoner_id):
    return _api.spectator.by_summoner(settings.LOL_REGION, summoner_id)

def get_game_by_summoner_name(summoner_name):
    summoner = _get_summoner_by_name(summoner_name)

    return _get_game_by_summoner_id(summoner['id'])

def get_match_by_game_id(game_id):
    return _api.match.by_id('AMERICAS', f'{settings.LOL_REGION}_{game_id}')
