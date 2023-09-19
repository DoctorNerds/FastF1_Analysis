import os
import pandas as pd
import fastf1
from fastf1.core import Laps
import matplotlib as plt
from fastf1 import utils
import plotly.express as px
import plotly.graph_objects as go
# Enable caching to avoid unnecessary strain on the API
# Replace "fastf1cache" with your cache location
fastf1.Cache.enable_cache('cache_data')
# Use variables year, wknd, ses, and driver to specify the race, session and driver
year = 2022
wknd = 14
ses = 'R'
# Obtain and load session data
session = fastf1.get_session(year, wknd, ses)
session.load()
drivers = session.drivers

driver_1, driver_2 = 'PER', 'LEC'

# Laps can now be accessed through the .laps object coming from the session
laps_driver_1 = session.laps.pick_driver(driver_1)
laps_driver_2 = session.laps.pick_driver(driver_2)

# Select the fastest lap
fastest_driver_1 = laps_driver_1.pick_fastest()
fastest_driver_2 = laps_driver_2.pick_fastest()

# Retrieve the telemetry and add the distance column
telemetry_driver_1 = fastest_driver_1.get_telemetry().add_distance()
telemetry_driver_2 = fastest_driver_2.get_telemetry().add_distance()

# Make sure whe know the team name for coloring
team_driver_1 = fastest_driver_1['Team']
team_driver_2 = fastest_driver_2['Team']

# Extract the delta time
delta_time, ref_tel, compare_tel = utils.delta_time(fastest_driver_1, fastest_driver_2)


# Crie um novo objeto de figura
fig = go.Figure()

# Adicione as linhas para as diferentes variáveis
fig.add_trace(go.Scatter(x=telemetry_driver_1['Distance'], y=telemetry_driver_1['Speed'], mode='lines', name='RPM', line=dict(color='blue')))

# Configure o layout do gráfico
fig.update_layout(
    title=f'Telemetry Data for {driver_1}',
    xaxis_title='Distance (meters)',
    yaxis_title='Value',
    hovermode='x'  # Mostra dicas de ferramentas ao passar o mouse ao longo do eixo x
)

# Mostre o gráfico
fig.show()






