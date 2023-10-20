import streamlit as st
import fastf1 as ff1
import os

from PIL import Image

from Data_Viz.data_analysis import data_analysis
from Data_Viz.sectors import sectors
from Data_Viz.speed import speed
from Data_Viz.tyre_strategy import tyre_strategy
from Data_Viz.tyre_performance import tyre_performance
from Data_Viz.track_speed_gear import track_speed_gear

# Enable the cache
ff1.Cache.enable_cache('cache_data2')

# Título página inicial
st.set_page_config(
    page_title="F1 TECH",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded"
)

image = Image.open('./images/f1_capa.png')

st.image(image, use_column_width=True)
st.write("<div align='center'><h2><i>Explore F1 Data with Artificial Intelligence</i></h2></div>",
         unsafe_allow_html=True)
st.write("")
       
seasons = [2021, 2022, 2023]
session_names = ['Session1', 'Session2', 'Session3', 'Session4', 'Session5']

# Criar a interface de seleção de 'season' e 'stage'
selected_season = st.selectbox('Select Season:', seasons, key='season_data', index=seasons.index(2023))

events_data = ff1.get_event_schedule(selected_season)
events = events_data['OfficialEventName']

# Criar a interface de seleção de 'season' e 'stage'
selected_event = st.selectbox('Select Event:', events, key='event_data', index=18)

sessions_data = ff1.get_event(selected_season, selected_event)
sessions = sessions_data[session_names]

# Criar a interface de seleção de 'season' e 'stage'
selected_session = st.selectbox('Select Session:', sessions, key='session_data')

data = ff1.get_session(selected_season, selected_event, selected_session)
data.load()

tabs = st.tabs(["Best Lap Data Analysis", "Sectors", "Speed", "Tyre Strategy", "Tyre Performance", "Track Speed and Gear"])

with tabs[0]:

    data_analysis(data, selected_season, selected_event, selected_session)

with tabs[1]:  

    sectors(data, selected_season, selected_event, selected_session)

with tabs[2]: 

    speed(data, selected_season, selected_event, selected_session)

with tabs[3]:

    tyre_strategy(data, selected_season, selected_event, selected_session)
    
with tabs[4]:
        
    tyre_performance(data, selected_season, selected_event, selected_session)

with tabs[5]:
    
    track_speed_gear(data, selected_season, selected_event, selected_session)
