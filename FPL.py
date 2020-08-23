import asyncio
import aiohttp
from Connection import Connect
from Collector import Collector
from Analyser import Analyser
from dotenv import load_dotenv
import os


async def FPL(year='2019-20'):
    load_dotenv()
    async with aiohttp.ClientSession() as session:
        fpl = await Connect(session)
        user_id=os.environ.get("USER_ID")
        collector = Collector(fpl,user_id,year)
        await collector.load_map()
        analyser = Analyser(year)
        '''
        my_team = await collector.get_personal_team()
        my_team = await collector.add_players_info(my_team)
        _team_correlations = analyser.plot_correlations(my_team,prependix='team')
        all_teams = await collector.get_all_players()
        _season_correlations = analyser.plot_correlations(all_teams,prependix='season')
        '''
        top_managers_info = collector.get_top_managers_info()
        top_managers = collector.get_top_managers()
        analyser.plot_season_progression(top_managers,top_managers_info)
if __name__ == "__main__":
    asyncio.run(FPL())