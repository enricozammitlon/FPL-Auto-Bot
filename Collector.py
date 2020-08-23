import pandas as pd
import numpy as np
from fpl import FPL
import csv


class Collector:

    def __init__(self,fpl_client: FPL, user_id : int, year: str) -> None:
        self.user_id = user_id
        self.fpl_client = fpl_client
        self.year = year
        self.current_year = True if year == '2020-21' else False

    # Always get the current personal team from 2020-21 here
    async def get_personal_team(self) -> pd.DataFrame:
        user = await self.fpl_client.get_user(self.user_id)
        team = await user.get_team()
        return pd.DataFrame(team)
    
    async def load_map(self) -> None:
        reader = pd.read_csv(f'Fantasy-Premier-League/data/{self.year}/player_idlist.csv')
        reader.rename(columns = {'id':'old_id'}, inplace = True)
        all_players =  await self.fpl_client.get_players(return_json=True)
        all_players = pd.DataFrame(all_players)[['first_name','second_name','id']]
        all_players=pd.merge(left=all_players, right=reader)
        self.id_map = all_players
    
    # Used to get the player with today's id, from a previous season
    def get_past_player(self,df :pd.DataFrame ,id : int):
        mapping_match = self.id_map['id'] == id
        try:
            player_id = self.id_map['old_id'][mapping_match].values[0]
        except IndexError:
            print(f"Data for player with id {id} is missing.")
            return pd.DataFrame(data=[np.zeros(len(df.columns))],columns=df.columns)
        matching_player = df['id'] == player_id
        return df[matching_player]
    
    async def get_player_info(self, player_id : int) -> dict:
        player = {}
        if self.current_year :
            try:
                player = await self.fpl_client.get_player(player_id,return_json=True)
            except ValueError:
                print(f"Player {player_id} not found")
        else:
            reader = pd.read_csv(f'Fantasy-Premier-League/data/{self.year}/players_raw.csv')
            player = self.get_past_player(reader,player_id)
            
        return player
    
    def filter_important(self, df : pd.DataFrame) -> pd.DataFrame :
        return df[['assists','bonus','bps','clean_sheets','cost_change_start',
       'cost_change_start_fall','creativity','event_points','goals_conceded','goals_scored','ict_index',
       'influence','minutes','now_cost','own_goals', 'penalties_missed', 'penalties_saved','points_per_game',
       'red_cards', 'saves','selected_by_percent','team','threat','total_points','value_form', 'value_season',
       'yellow_cards']]


    async def add_players_info(self,team_info: pd.DataFrame) -> pd.DataFrame:
        players_info = [await self.get_player_info(player_id) for player_id in team_info['element']]
        players_info = pd.concat(players_info)
        players_info.rename(columns = {'id':'element'}, inplace = True)
        players_info=players_info.reset_index()
        players_and_info= pd.concat([players_info, team_info], axis=1, join='inner')
        return self.filter_important(players_and_info)

    async def get_all_players(self) -> pd.DataFrame:
        if self.current_year :
            players = await self.fpl_client.get_players(return_json=True)
        else:
            players = pd.read_csv(f'Fantasy-Premier-League/data/{self.year}/players_raw.csv')
        return self.filter_important(players)
    
    # In the 2019-20 dataset due to COVID19 there is a gap in GW column
    # it jumps from 29 -> 39
    def get_top_managers_info(self) -> pd.DataFrame:
        if not self.year == '2019-20' :
            print("This data does not exist!")
            return None
        reader = pd.read_csv(f'Fantasy-Premier-League/data/{self.year}/managers/top_managers_gwInfo.csv')
        reader['gw']=reader['gw'].apply(lambda x : x if x <=29 else x-9)
        return reader

    def get_top_managers(self) -> pd.DataFrame:
        if not self.year == '2019-20' :
            print("This data does not exist!")
            return None
        reader = pd.read_csv(f'Fantasy-Premier-League/data/{self.year}/managers/top_managers.csv')
        reader.rename(columns = {'entry':'team_id'}, inplace = True)
        return reader