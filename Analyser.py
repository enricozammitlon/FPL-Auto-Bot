import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.animation as ani

class Analyser:
    def __init__(self,year):
        self.year = year
        self.palette = sns.color_palette("RdBu_r", 7)
        sns.set(style="white")

    def plot_correlations(self,df : pd.DataFrame,prependix :str ="") -> pd.DataFrame:
        corr = df.corr()
        mask = np.triu(np.ones_like(corr, dtype=np.bool))
        fig, _ax = plt.subplots(figsize=(20, 20))
        sns.heatmap(corr, mask=mask, center=0,cmap=self.palette,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
        fig.savefig(f"Plots/{prependix}_correlations_{self.year.replace('-','_')}_.png")
        return corr
    
    def plot_season_progression(self, managers:pd.DataFrame,season_data : pd.DataFrame) -> pd.DataFrame:
        fig, _original_ax = plt.subplots(figsize=(20, 20))
        season_data=pd.merge(left=season_data, right=managers)
        def build_timestep_bar(time_step : int):
            fig.clear()
            #colours = colours.sort_values('overall_rank')
            #print(colours)
            timestep_data = season_data['gw']==time_step+1

            order = season_data[timestep_data].sort_values('overall_rank')
            
            ax=sns.barplot(x="points",  y="player_name",hue="rank",order=order['player_name'], data=season_data[timestep_data],dodge=False)
            for index,p in enumerate(order['points']):
                padding=0
                if not str(order.iloc[index]['chip']).upper() == "NAN":
                    ax.text(p+1, index, str(order.iloc[index]['chip']).upper(), horizontalalignment='left', size='medium', color='black', weight='semibold')
                    padding=len(str(order.iloc[index]['chip']).upper())
                if not order.iloc[index]['transfers']== 0:
                    ax.text(p+padding+2, index, f"TRANS x{order.iloc[index]['transfers']}", horizontalalignment='left', size='medium', color='green' if order.iloc[index]['transfers'] == 1 else 'red' , weight='semibold')
            ax.set_title(f"Gameweek {time_step+1}")
            ax.set_ylabel("Player Name")
            ax.set_xlabel("GW Points")
            ax.get_legend().remove()
            sns.despine(left=True, bottom=True)
        Writer = ani.writers['ffmpeg']
        writer = Writer(fps=1, metadata=dict(artist='Enrico Zammit Lonardelli'), bitrate=1800)
        animator = ani.FuncAnimation(fig,build_timestep_bar,frames=season_data['gw'].max(),repeat=False)
        animator.save(f"Plots/bar_progression_top_managers_{self.year.replace('-','_')}_.mp4", writer=writer)
