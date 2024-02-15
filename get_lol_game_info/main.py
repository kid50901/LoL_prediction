import get_game_info
import pandas as pd

Tournaments_allLink_list=get_game_info.get_Tournaments_allLink(['link-S7'])
GameID_df = get_game_info.get_gameDfAllTournament(Tournaments_allLink_list)
GameID_list=GameID_df['game_ID'].to_list()
all_game_info=get_game_info.get_computation_all_data(GameID_list)

GameID_list=GameID_df['game_ID'].to_list()
all_game_info=get_game_info.get_computation_all_data(GameID_list)