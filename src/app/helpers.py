def find_participant_in_game_info(game, summoner_name):
    for participant in game.get('participants'):
        if participant.get('summonerName') == summoner_name:
            return participant
    return None
