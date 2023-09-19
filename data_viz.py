import pandas as pd
import streamlit as st
from PIL import Image
import fastf1 as ff1
import os
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import matplotlib as mpl
import plotly.graph_objects as go
import plotly.subplots as sp

import plotly.express as px
import numpy as np
import itertools
import pickle
from fastf1 import utils  
from fastf1 import plotting  

from matplotlib.collections import LineCollection
from matplotlib import cm

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

# Criar o menu lateral para navegar entre as páginas
page = st.sidebar.radio("Select the report", ["📊 Data Analysis",  "⏱️ Strategy",
                                              "🏎️ Tyre Performance", "🔧 Track Information"])

# Definir o conteúdo de cada página
if page == "📊 Data Analysis":

    st.write("<div align='center'><h1><b>Data Analysis</b></h1></div>", unsafe_allow_html=True)
    st.markdown("""<div style='text-align: center;'><hr style='border-top: 5px solid black'></div>""",
                unsafe_allow_html=True)
    
    # Enable the cache
   # cache_folder = os.path.join(os.path.dirname(__file__), 'cache_data')
   # ff1.Cache.enable_cache(cache_folder)
        
    seasons = [2021, 2022, 2023]
    session_names = ['Session1', 'Session2', 'Session3', 'Session4', 'Session5']

    # Criar a interface de seleção de 'season' e 'stage'
    selected_season = st.selectbox('Select Season:', seasons, key='season_data')

    events_data = ff1.get_event_schedule(selected_season)
    events = events_data['OfficialEventName']

    # Criar a interface de seleção de 'season' e 'stage'
    selected_event = st.selectbox('Select Event:', events, key='event_data')

    sessions_data = ff1.get_event(selected_season, selected_event)
    sessions = sessions_data[session_names]

    # Criar a interface de seleção de 'season' e 'stage'
    selected_session = st.selectbox('Select Session:', sessions, key='session_data')

    data = ff1.get_session(selected_season, selected_event, selected_session)
    data.load()

    tabs = st.tabs(["Best Lap Data Analysis", "Sectors", "Speed"])

    with tabs[0]:

        drivers = data.laps.Driver.unique()

        # Widget de seleção de Car Numbers
        selected_drivers = st.multiselect('Select Driver:', drivers, key='Best Lap Data Analysis')

        # Crie um dicionário para armazenar os pilotos selecionados
        driver_dict = {}

        # Preencha o dicionário com os pilotos selecionados
        for i, driver in enumerate(selected_drivers, start=1):
            key = f"driver_{i}"  # Gere a chave dinamicamente
            driver_dict[key] = driver

        # Lista de alturas relativas para cada linha
        row_heights = [1, 1, 0.5, 5, 1, 1, 0.5]
        variable_names = ['Gap to Ref.', 'RPM', 'Gear', 'Speed', 'Throttle', 'Brake', 'DRS']

        # Crie um novo objeto de subplot com escalas independentes
        fig = sp.make_subplots(rows=7, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=row_heights)

        if selected_drivers:

            # Verifique se há apenas um driver selecionado
            if len(selected_drivers) == 1:
                driver = selected_drivers[0]
                # Obtenha a telemetria para o driver atual
                laps_driver = data.laps.pick_driver(driver)
                fastest_driver = laps_driver.pick_fastest()
                telemetry_driver = fastest_driver.get_telemetry().add_distance()

                # Adicione as linhas para as diferentes variáveis em subplots separados com cores padrão
                fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['RPM'], mode='lines', name=f'{driver} - RPM', line=dict(color='blue')), row=1, col=1)
                fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['nGear'], mode='lines', name=f'{driver} - Gear', line=dict(color='yellow')), row=2, col=1)
                fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['Speed'], mode='lines', name=f'{driver} - Speed', line=dict(color='lightblue')), row=3, col=1)
                fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['Throttle'], mode='lines', name=f'{driver} - Throttle', line=dict(color='green')), row=4, col=1)
                fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['Brake'], mode='lines', name=f'{driver} - Brake', line=dict(color='red')), row=5, col=1)
                fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['DRS'], mode='lines', name=f'{driver} - DRS', line=dict(color='orange')), row=6, col=1)
            else:
                # Crie uma lista de cores com base na equipe de cada driver
                colors = []
                driver_ref = driver_dict['driver_1']
                laps_driver_ref = data.laps.pick_driver(driver)
                fastest_driver_ref = laps_driver_ref.pick_fastest()

                # Lista de nomes das variáveis
                for driver in selected_drivers:
                    team = data.laps.pick_driver(driver).pick_fastest()['Team']
                    team_color = ff1.plotting.team_color(team)
                    driver_color = ff1.plotting.driver_color(driver)
                    colors.append(driver_color)

                # Itere sobre os drivers selecionados
                for i, driver in enumerate(selected_drivers, start=1):
                    # Obtenha a telemetria para o driver atual
                    laps_driver = data.laps.pick_driver(driver)
                    fastest_driver = laps_driver.pick_fastest()
                    telemetry_driver = fastest_driver.get_telemetry().add_distance()
                    delta_time, ref_tel, compare_tel = utils.delta_time(fastest_driver_ref, fastest_driver)

                    # Adicione as linhas para as diferentes variáveis em subplots separados
                    fig.add_trace(go.Scatter(x=ref_tel['Distance'], y=delta_time, mode='lines', name=f'{driver} - Gap', line=dict(color=colors[i-1]), legendgroup=driver), row=1, col=1)
                    fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['RPM'], mode='lines', name=f'{driver} - RPM', line=dict(color=colors[i-1]), legendgroup=driver), row=2, col=1)
                    fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['nGear'], mode='lines', name=f'{driver} - Gear', line=dict(color=colors[i-1]), legendgroup=driver), row=3, col=1)
                    fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['Speed'], mode='lines', name=f'{driver} - Speed', line=dict(color=colors[i-1]), legendgroup=driver), row=4, col=1)
                    fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['Throttle'], mode='lines', name=f'{driver} - Throttle', line=dict(color=colors[i-1]), legendgroup=driver), row=5, col=1)
                    fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['Brake'], mode='lines', name=f'{driver} - Brake', line=dict(color=colors[i-1]), legendgroup=driver), row=6, col=1)
                    fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['DRS'], mode='lines', name=f'{driver} - DRS', line=dict(color=colors[i-1]), legendgroup=driver), row=7, col=1)

            # Configure o layout do gráfico
            fig.update_layout(
                title={
                            'text': f'Telemetry Data for {selected_session}',
                            'x': 0.5,
                            'xanchor': 'center',
                            'y': 0.95,
                            'yanchor': 'top',
                            'font': {'size': 36}
                        },
                showlegend=False,
                hovermode="x unified",
                height=700,  # Ajuste a altura do gráfico com base no número de variáveis (6) multiplicado pelo número de drivers selecionados
            )

            # Oculte os eixos y
            for i in range(1, len(selected_drivers) + 1):
                for j in range(1, 7):
                    fig.update_yaxes(showticklabels=False, row=j, col=i)

            # Adicione nomes das variáveis no eixo Y
            for j, variable_name in enumerate(variable_names, start=1):
                fig.update_yaxes(title_text=variable_name, row=j, col=1)

            # Use o st.plotly_chart para exibir o gráfico no Streamlit
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Selecione pelo menos um piloto.")

    with tabs[1]:  

        pilotos_info = []     
        driver_colors = {}
        drivers = data.laps.Driver.unique()

        for driver in drivers:
            laps_driver = data.laps.pick_driver(driver)
            fastest_driver = laps_driver.pick_fastest()
            team = data.laps.pick_driver(driver).pick_fastest()['Team']
            team_color = ff1.plotting.team_color(team)
            try:
                driver_color = ff1.plotting.driver_color(driver)
            except KeyError:
                driver_color = team_color
    
            driver_colors[driver] = driver_color
           
        
            # Extraia as informações desejadas para o piloto atual
            piloto_info = {
                'Driver': driver,  # Nome do piloto
                'Lap Time (sec)': fastest_driver['LapTime'],
                'Sector 1 (sec)': fastest_driver['Sector1Time'],
                'Sector 2 (sec)': fastest_driver['Sector2Time'],
                'Sector 3 (sec)': fastest_driver['Sector3Time'],
                'Compound': fastest_driver['Compound'],
            }

            # Adicione as informações do piloto à lista
            pilotos_info.append(piloto_info)

        df = pd.DataFrame(pilotos_info)

        # Formatar as colunas de tempo para exibição
        df['Lap Time (sec)'] = df['Lap Time (sec)'].apply(lambda x: float(x.total_seconds()))
        df['Sector 1 (sec)'] = df['Sector 1 (sec)'].apply(lambda x: float(x.total_seconds()))
        df['Sector 2 (sec)'] = df['Sector 2 (sec)'].apply(lambda x: float(x.total_seconds()))
        df['Sector 3 (sec)'] = df['Sector 3 (sec)'].apply(lambda x: float(x.total_seconds()))

        # Selecione apenas as colunas necessárias e ordene os DataFrames
        table1 = df[['Driver', 'Sector 1 (sec)', 'Compound']].sort_values(by='Sector 1 (sec)').reset_index(drop=True)
        table2 = df[['Driver', 'Sector 2 (sec)', 'Compound']].sort_values(by='Sector 2 (sec)').reset_index(drop=True)
        table3 = df[['Driver', 'Sector 3 (sec)', 'Compound']].sort_values(by='Sector 3 (sec)').reset_index(drop=True)
        table4 = df[['Driver', 'Lap Time (sec)', 'Compound']].sort_values(by='Lap Time (sec)').reset_index(drop=True)

        table1.index += 1 
        table2.index += 1 
        table3.index += 1 
        table4.index += 1 
        
        def apply_color(row, driver_colors):
            driver = row['Driver']
            color = driver_colors.get(driver, '')  # Obtém a cor correspondente ao piloto ou vazio se não houver
            text_color = 'black' if color else ''  # Define a cor do texto como preto se houver uma cor de fundo, caso contrário, vazio
            text_style = 'font-weight: bold' if color else ''  # Define o estilo de texto como negrito se houver uma cor de fundo, caso contrário, vazio
            return [f'background-color: {color}; color: {text_color}; {text_style}' if cell == driver else '' for cell in row]


        # Aplicar a função de estilo para todas as linhas do DataFrame
        styled_table1 = table1.style.apply(apply_color, driver_colors=driver_colors, axis=1)
        styled_table2 = table2.style.apply(apply_color, driver_colors=driver_colors, axis=1)
        styled_table3 = table3.style.apply(apply_color, driver_colors=driver_colors, axis=1)
        styled_table4 = table4.style.apply(apply_color, driver_colors=driver_colors, axis=1)
        
        # Crie tabs para exibir as tabelas
        with st.container():
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.table(styled_table1.format(precision=3))

            with col2:
                st.table(styled_table2.format(precision=3))

            with col3:
                st.table(styled_table3.format(precision=3))

            with col4:
                st.table(styled_table4.format(precision=3))

    with tabs[2]: 

        pilotos_info = []     
        driver_colors = {}
        drivers = data.laps.Driver.unique()

        for driver in drivers:
            laps_driver = data.laps.pick_driver(driver)
            fastest_driver = laps_driver.pick_fastest()
            team = data.laps.pick_driver(driver).pick_fastest()['Team']
            team_color = ff1.plotting.team_color(team)
            try:
                driver_color = ff1.plotting.driver_color(driver)
            except KeyError:
                driver_color = team_color
    
            driver_colors[driver] = driver_color

            # Extraia as informações desejadas para o piloto atual
            piloto_info = {
                'Driver': driver,  # Nome do piloto
                'Sector 1 Speed': fastest_driver['SpeedI1'],
                'Sector 2 Speed': fastest_driver['SpeedI2'],
                'Finish Line Speed': fastest_driver['SpeedFL'],
                'Longest Straight Speed': fastest_driver['SpeedST'],
            }

            # Adicione as informações do piloto à lista
            pilotos_info.append(piloto_info)

        df_speed = pd.DataFrame(pilotos_info)

        # Ajuste de escala do eixo y
        max_y_value_sector1_speed = df_speed['Sector 1 Speed'].max()*1.01
        min_y_value_sector1_speed = df_speed['Sector 1 Speed'].max()*0.80

        # Para Sector 1 Speed
        fig_sector1 = px.bar(df_speed, x='Driver', y='Sector 1 Speed', color='Driver', color_discrete_map=driver_colors)
        fig_sector1.update_layout(
            title={
                    'text': 'Sector 1 Speed',
                    'x': 0.5,
                    'xanchor': 'center',
                    'y': 0.95,
                    'yanchor': 'top',
                    'font': {'size': 36}
                },
            xaxis_title='Driver',
            yaxis_title='Speed',
            yaxis=dict(range=[min_y_value_sector1_speed, max_y_value_sector1_speed]) 
        )
    
        # Exibindo os gráficos
        st.plotly_chart(fig_sector1, use_container_width=True)

        # Ajuste de escala do eixo y
        max_y_value_sector2_speed = df_speed['Sector 2 Speed'].max()*1.01
        min_y_value_sector2_speed = df_speed['Sector 2 Speed'].max()*0.80

        # Para Sector 1 Speed
        fig_sector2 = px.bar(df_speed, x='Driver', y='Sector 2 Speed', color='Driver', color_discrete_map=driver_colors)
        fig_sector2.update_layout(
            title={
                    'text': 'Sector 2 Speed',
                    'x': 0.5,
                    'xanchor': 'center',
                    'y': 0.95,
                    'yanchor': 'top',
                    'font': {'size': 36}
                },
            xaxis_title='Driver',
            yaxis_title='Speed',
            yaxis=dict(range=[min_y_value_sector2_speed, max_y_value_sector2_speed]) 
        )
    
        # Exibindo os gráficos
        st.plotly_chart(fig_sector2, use_container_width=True)

        # Ajuste de escala do eixo y
        max_y_value_fl_speed = df_speed['Finish Line Speed'].max()*1.01
        min_y_value_fl_speed = df_speed['Finish Line Speed'].max()*0.80

        # Para Sector 1 Speed
        fig_sector3 = px.bar(df_speed, x='Driver', y='Finish Line Speed', color='Driver', color_discrete_map=driver_colors)
        fig_sector3.update_layout(
            title={
                    'text': 'Finish Line Speed',
                    'x': 0.5,
                    'xanchor': 'center',
                    'y': 0.95,
                    'yanchor': 'top',
                    'font': {'size': 36}
                },
            xaxis_title='Driver',
            yaxis_title='Speed',
            yaxis=dict(range=[min_y_value_fl_speed, max_y_value_fl_speed]) 
        )
    
        # Exibindo os gráficos
        st.plotly_chart(fig_sector3, use_container_width=True)

        # Ajuste de escala do eixo y
        max_y_value_ls_speed = df_speed['Longest Straight Speed'].max()*1.01
        min_y_value_ls_speed = df_speed['Longest Straight Speed'].max()*0.80

        # Para Sector 1 Speed
        fig_sector4 = px.bar(df_speed, x='Driver', y='Longest Straight Speed', color='Driver', color_discrete_map=driver_colors)
        fig_sector4.update_layout(
            title={
                    'text': 'Longest Straight Speed',
                    'x': 0.5,
                    'xanchor': 'center',
                    'y': 0.95,
                    'yanchor': 'top',
                    'font': {'size': 36}
                },
            xaxis_title='Driver',
            yaxis_title='Speed',
            yaxis=dict(range=[min_y_value_ls_speed, max_y_value_ls_speed]) 
        )
    
        # Exibindo os gráficos
        st.plotly_chart(fig_sector4, use_container_width=True)

# Definir o conteúdo de cada página
if page == "⏱️ Strategy":

    st.write("<div align='center'><h1><b>Strategy Analysis</b></h1></div>", unsafe_allow_html=True)
    st.markdown("""<div style='text-align: center;'><hr style='border-top: 5px solid black'></div>""",
                unsafe_allow_html=True)
    
    compound_colors = {
        'SOFT': '#FF3333',
        'MEDIUM': '#FFF200',
        'HARD': '#EBEBEB',
        'INTERMEDIATE': '#39B54A',
        'WET': '#00AEEF',
    }
        
    # Enable the cache
    cache_folder = os.path.join(os.path.dirname(__file__), 'cache_data')
    ff1.Cache.enable_cache(cache_folder)
        
    seasons = [2021, 2022, 2023]
    session_names = ['Session1', 'Session2', 'Session3', 'Session4', 'Session5']

    # Criar a interface de seleção de 'season' e 'stage'
    selected_season = st.selectbox('Select Season:', seasons, key='season_strategy')

    events_data = ff1.get_event_schedule(selected_season)
    events = events_data['OfficialEventName']

    # Criar a interface de seleção de 'season' e 'stage'
    selected_event = st.selectbox('Select Event:', events, key='event_strategy')

    data = ff1.get_session(selected_season, selected_event, 'R')
    #laps = data.load_laps(with_telemetry=True)
    data.load()

    driver_stints = data.laps[['Driver', 'Stint', 'Compound', 'LapNumber']].groupby(
        ['Driver', 'Stint', 'Compound']
    ).count().reset_index()

    driver_stints = driver_stints.rename(columns={'LapNumber': 'StintLength'})

    driver_stints = driver_stints.sort_values(by=['Stint'])

    # Defina o tamanho da figura
    plt.rcParams["figure.figsize"] = [15, 10]
    plt.rcParams["figure.autolayout"] = True

    # Crie a figura e o eixo
    fig, ax = plt.subplots()

    for driver in data.results['Abbreviation']:
        stints = driver_stints.loc[driver_stints['Driver'] == driver]
        
        previous_stint_end = 0
        for _, stint in stints.iterrows():
            plt.barh(
                [driver], 
                stint['StintLength'], 
                left=previous_stint_end, 
                color=compound_colors[stint['Compound']], 
                edgecolor="black"
            )
            
            previous_stint_end = previous_stint_end + stint['StintLength']
            
    # Defina o título
    plt.title(f'Race strategy - {selected_event} {selected_season}')

    # Defina o rótulo do eixo x
    plt.xlabel('Lap')

    # Inverta o eixo y
    plt.gca().invert_yaxis()

    # Remova a moldura do gráfico
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    used_colors = {compound: color for compound, color in compound_colors.items() if compound in driver_stints['Compound'].unique()}
    handles = [plt.Rectangle((0, 0), 1, 1, color=color, label=compound) for compound, color in used_colors.items()]

    ax.legend(handles=handles, title='Compounds', loc='center left', bbox_to_anchor=(1, 0.5))


    # Exiba o gráfico no Streamlit
    st.pyplot(fig)


# Definir o conteúdo de cada página
if page == "🏎️ Tyre Performance":

    st.write("<div align='center'><h1><b>Tyre Performance Analysis</b></h1></div>", unsafe_allow_html=True)
    st.markdown("""<div style='text-align: center;'><hr style='border-top: 5px solid black'></div>""",
                unsafe_allow_html=True)
    
    # Enable the cache
    cache_folder = os.path.join(os.path.dirname(__file__), 'cache_data')
    ff1.Cache.enable_cache(cache_folder)
        
    seasons = [2021, 2022, 2023]
    session_names = ['Session1', 'Session2', 'Session3', 'Session4', 'Session5']

    # Criar a interface de seleção de 'season' e 'stage'
    selected_season = st.selectbox('Select Season:', seasons, key='season_tyre')

    events_data = ff1.get_event_schedule(selected_season)
    events = events_data['OfficialEventName']

    # Criar a interface de seleção de 'season' e 'stage'
    selected_event = st.selectbox('Select Event:', events, key='event_tyre')

    sessions_data = ff1.get_event(selected_season, selected_event)
    sessions = sessions_data[session_names]

    # Criar a interface de seleção de 'season' e 'stage'
    selected_session = st.selectbox('Select Session:', sessions, key='session_tyre')

    data = ff1.get_session(selected_season, selected_event, selected_session)
    data.load()

    drivers = data.laps.Driver.unique()

    with st.container():
        col1, col2 = st.columns(2)

        with col1:

            # Widget de seleção de Car Numbers
            selected_drivers = st.selectbox('Select Driver:', drivers, key='Tyre Performance Col1')

            driver_laps = data.laps.pick_driver(selected_drivers).pick_quicklaps().reset_index()

            # Criar o gráfico com Plotly Express
            fig = px.scatter(driver_laps, x="LapNumber", y="LapTime", color="Compound",
                            color_discrete_map=ff1.plotting.COMPOUND_COLORS,
                            title=f"{selected_drivers} Laptimes in the {selected_season} {selected_event} - {selected_session}")

            # Configurações de layout
            fig.update_xaxes(title="Lap Number")
            fig.update_yaxes(title="Lap Time")
            fig.update_yaxes(autorange="reversed")  # Inverte o eixo y
            fig.update_layout(showlegend=True)
            fig.update_traces(marker=dict(size=10, line=dict(width=0)))

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig, use_container_width=True)

        with col2:

            # Widget de seleção de Car Numbers
            selected_drivers = st.selectbox('Select Driver:', drivers, key='Tyre Performance Col2')

            driver_laps = data.laps.pick_driver(selected_drivers).pick_quicklaps().reset_index()

            # Criar o gráfico com Plotly Express
            fig = px.scatter(driver_laps, x="LapNumber", y="LapTime", color="Compound",
                            color_discrete_map=ff1.plotting.COMPOUND_COLORS,
                            title=f"{selected_drivers} Laptimes in the {selected_season} {selected_event} - {selected_session}")

            # Configurações de layout
            fig.update_xaxes(title="Lap Number")
            fig.update_yaxes(title="Lap Time")
            fig.update_yaxes(autorange="reversed")  # Inverte o eixo y
            fig.update_layout(showlegend=True)
            fig.update_traces(marker=dict(size=10, line=dict(width=0)))

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig, use_container_width=True)

if page == "🔧 Track Information":

    st.write("<div align='center'><h1><b>Track Information</b></h1></div>", unsafe_allow_html=True)
    st.markdown("""<div style='text-align: center;'><hr style='border-top: 5px solid black'></div>""",
                unsafe_allow_html=True)
    
    # Enable the cache
    cache_folder = os.path.join(os.path.dirname(__file__), 'cache_data')
    ff1.Cache.enable_cache(cache_folder)
        
    seasons = [2021, 2022, 2023]
    session_names = ['Session1', 'Session2', 'Session3', 'Session4', 'Session5']

    # Criar a interface de seleção de 'season' e 'stage'
    selected_season = st.selectbox('Select Season:', seasons, key='season_track')

    events_data = ff1.get_event_schedule(selected_season)
    events = events_data['OfficialEventName']

    # Criar a interface de seleção de 'season' e 'stage'
    selected_event = st.selectbox('Select Event:', events, key='event_track')

    sessions_data = ff1.get_event(selected_season, selected_event)
    sessions = sessions_data[session_names]

    # Criar a interface de seleção de 'season' e 'stage'
    selected_session = st.selectbox('Select Session:', sessions, key='session_track')

    data = ff1.get_session(selected_season, selected_event, selected_session)
    data.load()

    # Obtenha a volta mais rápida
    lap = data.laps.pick_fastest()
    tel = lap.get_telemetry()

    x = np.array(tel['X'].values)
    y = np.array(tel['Y'].values)

    # Crie um título comum
    st.title(f"Fastest Lap Visualization\n{lap['Driver']} - {data.event['EventName']} {data.event.year}")

    # Crie tabs para exibir as tabelas
    with st.container():
        col1, col2 = st.columns(2)

        with col1:

            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)
            gear = tel['nGear'].to_numpy().astype(float)

            cmap = cm.get_cmap('Paired')
            lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N+1), cmap=cmap)
            lc_comp.set_array(gear)
            lc_comp.set_linewidth(4)

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.add_collection(lc_comp)
            ax.axis('equal')
            ax.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

            cbar = plt.colorbar(mappable=lc_comp, label="Gear", boundaries=np.arange(1, 10))

            # Remova a borda preta do gráfico
            ax.set_frame_on(False)

            # Exiba o gráfico no Streamlit
            st.pyplot(fig)

        with col2:

            colormap = mpl.cm.plasma
            color = lap.telemetry['Speed']      # value to base color gradient on
            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            # Configurar o mapa de cores
            colormap = mpl.cm.plasma
            norm = plt.Normalize(color.min(), color.max())
            lc = LineCollection(segments, cmap=colormap, norm=norm, linestyle='-', linewidth=5)
            lc.set_array(color)

            # Configurar a figura
            fig2, ax = plt.subplots(figsize=(6, 4.143))
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
            ax.axis('off')

            # Adicionar a linha de fundo da pista
            ax.plot(lap.telemetry['X'], lap.telemetry['Y'], color='black', linestyle='-', linewidth=16, zorder=0)

            # Adicionar a linha colorida
            line = ax.add_collection(lc)

            # Adicionar a barra de cores com rótulo "Speed"
            cbar = plt.colorbar(mappable=lc, label="Speed")

            # Exibir o gráfico no Streamlit
            st.pyplot(fig2)
