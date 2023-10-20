import streamlit as st
import fastf1 as ff1
import pandas as pd
import numpy as np
import matplotlib as mpl

import plotly.graph_objects as go
import plotly.subplots as sp
import plotly.express as px

from fastf1 import utils  
from fastf1.plotting import team_color
from fastf1 import plotting

from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import cm

from PIL import Image

##################################################################################################
# PARTE 1: CARREGANDO UMA IMAGEM DE CAPA
##################################################################################################


# Configurando o título da página URL
st.set_page_config(
    page_title="F1 TECH",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregando uma imagem
image = Image.open('./images/f1_capa.png')

# Inserindo a imagem na página utilizando os comandos do stremalit
st.image(image, use_column_width=True)
st.write("<div align='center'><h2><i>Explore F1 Data with Artificial Intelligence</i></h2></div>",
         unsafe_allow_html=True)
st.write("")
##################################################################################################

##################################################################################################
# PARTE 2: CRIANDO SELETORES PARA FILTRAR DADOS QUE SERÃO CARREGADOS
##################################################################################################

# Cria um seletor para escolher entre as temporadas 2021, 2022 e 2023
seasons = [2021, 2022, 2023]
st.write(seasons)
selected_season = st.selectbox('Select Season:', seasons, key='season_data', index=seasons.index(2023))
st.write(selected_season)

# Carrega o cronograma da temporada selecionada e extrai todos os eventos do ano
events_data = ff1.get_event_schedule(selected_season)
st.write(events_data)
events = events_data['OfficialEventName']
st.write(events)

# Cria um seletor para escolher entre os eventos da temporada escolhida
selected_event = st.selectbox('Select Event:', events, key='event_data', index=16)
st.write(selected_event)

# Carrega as sessões 'Session1', 'Session2', 'Session3', 'Session4', 'Session5' do evento escolhido 
session_names = ['Session1', 'Session2', 'Session3', 'Session4', 'Session5']
sessions_data = ff1.get_event(selected_season, selected_event)
st.write(sessions_data)
sessions = sessions_data[session_names]
st.write(sessions)

# Criar um seletor para escolher entre as sessões do evento escolhido
selected_session = st.selectbox('Select Session:', sessions, key='session_data')
st.write(selected_session)

# Finalmente, após escolher temporada, evento e sessão, carregamos os dados em 'data' pelo 'get_session'
data = ff1.get_session(selected_season, selected_event, selected_session)
data.load()
st.write(data)

##################################################################################################
# OBS: CRIANDO ABAS DE VISUALIZAÇÃO NO STREAMLIT
##################################################################################################

tabs = st.tabs(["Best Lap Data Analysis", "Sectors", "Speed", "Track Speed and Gear", "Tyre Performance", "Tyre Strategy"])

##################################################################################################
# PARTE 3: CRIANDO UM TEMPLATE PARA ANÁLISE DE DADOS
##################################################################################################

with tabs[0]:

##################################################################################################
# PARTE 3.1: SELETOR DE PILOTOS
# Essa parte vamor criar um seletor de pilotos, disponíveis na sessão escolhida
# Será possível escolher mais de um piloto simultaneamente para fazer a análise
# Os pilotos escolhinhos serão armazenados em um dicionário
##################################################################################################

    # Cria uma lista com os pilotos únicos da sessão escolhida
    drivers = data.laps.Driver.unique()
    st.write(drivers)

    # Cria um seletor para escolher entre os pilotos da sessão
    selected_drivers = st.multiselect('Select Driver:', drivers, key='Best Lap Data Analysis')

    # Cria um dicionário para armazenar os pilotos selecionados
    driver_dict = {}

    # Preencha o dicionário com os pilotos selecionados
    for i, driver in enumerate(selected_drivers, start=1):
        key = f"driver_{i}"  # Gere a chave dinamicamente
        driver_dict[key] = driver

    st.write(driver_dict)

##################################################################################################
# PARTE 3.2: TELA DE VISUALIZAÇÃO DE DADOS
# Vamos ter duas telas, uma para vizualização de apenas 1 piloto e outra para mais pilotos
# A diferença é porque quando selecionamos apenas 1 piloto não plotamos a variavel GAP
##################################################################################################

    # Verifica se há apenas um piloto selecionado
    if len(selected_drivers) == 1:
        # Se apenas 1 piloto selecionado, define os tamanhos das linhas dos gráficos do template
        row_heights = [1, 0.5, 5, 1, 1, 1, 0.5]
    else:
        # Se apenas mais de 1 piloto selecionado, define os tamanhos das linhas dos gráficos do template
        row_heights = [1, 1, 0.5, 5, 1, 1, 0.5]
    
    # Define o nome das variáveis que serão plotadas no gráfico em ordem de exibição
    variable_names_driver = ['RPM', 'Gear', 'Speed', 'Throttle', 'Brake', 'DRS']
    variable_names_drivers = ['Gap to Ref.', 'RPM', 'Gear', 'Speed', 'Throttle', 'Brake', 'DRS']

    # Cria um objeto de subplot de 7 linhas, 1 coluna e com escalas independentes definidas em 'row_heights'
    fig = sp.make_subplots(rows=7, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=row_heights)

    # Verifica se algum piloto foi selecionado, só entra neste bloco após pelo menos 1 piloto ser selecionado
    if selected_drivers:

        # Verifica se há apenas um piloto selecionado, já que a tela de análise será diferente
        if len(selected_drivers) == 1:
            # Seleciona o primeiro piloto armazenado no dicionário 'selected_drivers'
            driver = selected_drivers[0]
            st.write(driver)
            # Através dos métodos .laps e .pick_driver extrai os dados de volta deste piloto
            laps_driver = data.laps.pick_driver(driver)
            st.write(laps_driver)
            # Através do método .pick_fastest extrai os dados da volta mais rápida deste piloto
            fastest_driver = laps_driver.pick_fastest()
            st.write(fastest_driver)

            # Faz uma tentativa de extrair os dados de telemetria da volta mais rápida do piloto
            try:
                # Extrai os dados de telemetria da volta mais rápida e adiciona coluna da distância
                telemetry_driver = fastest_driver.get_telemetry().add_distance()
                st.write(telemetry_driver)
            # Se não for possível extrair os dados de telemetria exibe um aviso na tela
            except Exception as e:
                # Exibe essa mensagem com o aviso se não for possível extrair os dados de telemetria
                st.warning("We do not have telemetry data for this driver in this session.")
                telemetry_driver = None  

            # Se os dados de telemetria para 1 piloto forem carregados, executa o bloco if para gerar os gráficos
            if telemetry_driver is not None:

                # Os gráficos de linha são gerados pela biblioteca plotly, definindo variável, cor e posição.
                fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['RPM'], mode='lines', name=f'{driver} - RPM', line=dict(color='blue')), row=1, col=1)
                fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['nGear'], mode='lines', name=f'{driver} - Gear', line=dict(color='yellow')), row=2, col=1)
                fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['Speed'], mode='lines', name=f'{driver} - Speed', line=dict(color='lightblue')), row=3, col=1)
                fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['Throttle'], mode='lines', name=f'{driver} - Throttle', line=dict(color='green')), row=4, col=1)
                fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['Brake'], mode='lines', name=f'{driver} - Brake', line=dict(color='red')), row=5, col=1)
                fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['DRS'], mode='lines', name=f'{driver} - DRS', line=dict(color='orange')), row=6, col=1)

                # Configura o layout do gráfico
                fig.update_layout(
                    # Adiciona um título
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
                    height=700, 
                )

                # Oculta os eixos y para os 6 gráficos de linha gerados
                fig.update_yaxes(showticklabels=False)

            # Adiciona os nomes das variáveis no eixo Y para os 6 gráficos de linha gerados
            for j, variable_name in enumerate(variable_names_driver, start=1):
                fig.update_yaxes(title_text=variable_name, row=j, col=1)

            # Use o st.plotly_chart para exibir o gráfico no Streamlit
            st.plotly_chart(fig, use_container_width=True)

        # Se mais de um piloto for selecionado, entra neste bloco para gerar os gráficos
        else:
            # Cria uma lista de cores com base na equipe de cada píloto
            colors = []
            # Define como referência (para usar a função que calcula o gap) o primeiro piloto selecionado
            driver_ref = driver_dict['driver_1']
            # Carrega os dados das voltas do piloto referência
            laps_driver_ref = data.laps.pick_driver(driver_ref)
            st.write(laps_driver_ref)
            # Carrega os dados da volta mais rápida
            fastest_driver_ref = laps_driver_ref.pick_fastest()
            st.write(fastest_driver_ref)

            # Bloco para extrair a cor de cada piloto e adicionar na lista colors
            for driver in selected_drivers:
                # Extrai a equipe do piloto selecionado
                team = data.laps.pick_driver(driver).pick_fastest()['Team']
                st.write(team)
                # Extrai a cor da equipe do piloto selecionado (não é usado neste código)
                team_driver_color = team_color(team)
                # Extrai a cor do piloto selecionado
                driver_color = ff1.plotting.driver_color(driver)
                # Adiciona a cor do piloto selecionado na lista colors
                colors.append(driver_color)
            st.write(colors)

            # Bloco para extrair os dados de telemetria de cada piloto selecionado na lista selected_drivers
            for i, driver in enumerate(selected_drivers, start=1):
                # Obtém os dados para o piloto selecionado
                laps_driver = data.laps.pick_driver(driver)
                # Obtém os dados da volta mais rápida do piloto selecionado
                fastest_driver = laps_driver.pick_fastest()
                st.write(driver)
                st.write(fastest_driver)

                # Faz uma tentativa de extrair os dados de telemetria da volta mais rápida do piloto
                try:
                    # Extrai os dados de telemetria da volta mais rápida e adiciona coluna da distância
                    telemetry_driver = fastest_driver.get_telemetry().add_distance()
                    st.write(telemetry_driver)
                # Se não for possível extrair os dados de telemetria exibe um aviso na tela
                except Exception as e:
                    # Exibe essa mensagem com o aviso se não for possível extrair os dados de telemetria
                    st.warning("We do not have telemetry data for these drivers in this session.")
                    telemetry_driver = None  

                # Se os dados de telemetria forem carregados, executa o bloco if para gerar os gráficos
                if telemetry_driver is not None:

                    # Utiliza a função 'delta_time' a partir dos dados da volta mais rápida do piloto selecionado
                    # com a volta mais rápida do piloto referência
                    # É importante saber que a própria biblioteca Fast F1 diz que em breve essa função deixará
                    # de existir, pois podem haver erros no cálculo do gap que deixem a informação imprecisa
                    delta_time, ref_tel, compare_tel = utils.delta_time(fastest_driver_ref, fastest_driver)

                    # Os gráficos de linha são gerados pela biblioteca plotly, definindo variável, cor e posição.
                    # Diferentemente do bloco para apenas 1 piloto, agora são gerados 7 gráficos de linha 
                    # já que vamos plotar também a informação da variável Gap do delta_time
                    fig.add_trace(go.Scatter(x=ref_tel['Distance'], y=delta_time, mode='lines', name=f'{driver} - Gap', line=dict(color=colors[i-1]), legendgroup=driver), row=1, col=1)
                    fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['RPM'], mode='lines', name=f'{driver} - RPM', line=dict(color=colors[i-1]), legendgroup=driver), row=2, col=1)
                    fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['nGear'], mode='lines', name=f'{driver} - Gear', line=dict(color=colors[i-1]), legendgroup=driver), row=3, col=1)
                    fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['Speed'], mode='lines', name=f'{driver} - Speed', line=dict(color=colors[i-1]), legendgroup=driver), row=4, col=1)
                    fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['Throttle'], mode='lines', name=f'{driver} - Throttle', line=dict(color=colors[i-1]), legendgroup=driver), row=5, col=1)
                    fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['Brake'], mode='lines', name=f'{driver} - Brake', line=dict(color=colors[i-1]), legendgroup=driver), row=6, col=1)
                    fig.add_trace(go.Scatter(x=telemetry_driver['Distance'], y=telemetry_driver['DRS'], mode='lines', name=f'{driver} - DRS', line=dict(color=colors[i-1]), legendgroup=driver), row=7, col=1)

                    # Configure o layout do gráfico
                    fig.update_layout(
                        # Adiciona um título
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
                        height=700,  
                    )

                    # Oculta os eixos y para todos os gráficos de todos os pilotos selecionados
                    fig.update_yaxes(showticklabels=False)

            # Adiciona os nomes das variáveis no eixo Y
            for j, variable_name in enumerate(variable_names_drivers, start=1):
                fig.update_yaxes(title_text=variable_name, row=j, col=1)

            # Usa o st.plotly_chart para exibir o gráfico no Streamlit
            st.plotly_chart(fig, use_container_width=True)

##################################################################################################

##################################################################################################
# PARTE 4: CRIANDO AS TABELAS DE SETORES
##################################################################################################

with tabs[1]:

    # Cria a lista para armazenar as informações dos pilotos        
    pilotos_info = []   
    # Cria o dicionário para armazenar as cores de cada piloto  
    driver_colors = {}
    # Extrai todos os nomes de pilotos únicos dos dados selecionados
    drivers = data.laps.Driver.unique()
    st.write(drivers)

    # Bloco de loop que itera sobre cada piloto único da lista drivers
    for driver in drivers:
        st.write(driver)
        # Seleciona o dado das voltas deste piloto
        laps_driver = data.laps.pick_driver(driver)
        # Seleciona o dado da volta mais rápida deste piloto
        fastest_driver = laps_driver.pick_fastest()
        st.write(fastest_driver)
        # Seleciona o time deste piloto
        team = data.laps.pick_driver(driver).pick_fastest()['Team']
        st.write(team)
        
        # Verifique se 'team' é NaN e defina 'team_color' como branco neste caso
        if pd.isna(team):
            team_color = 'white'
        # Senão define team_color como a cor definida pela biblioteca Fast F1 para esta equipe
        else:
            team_color = plotting.team_color(team)
        st.write(team_color)

        # Tenta extrair a cor do piloto através dos métodos .plotting.driver_color
        try:
            # Armazena a cor na variável driver_color
            driver_color = ff1.plotting.driver_color(driver)
        # Se erro, define a variável driver_color com a cor da equipe deste piloto
        except KeyError:
            driver_color = team_color
        st.write(driver_color)

        # Adiciona a cor (valor) para o pilto (chave) correspondente no dicionário driver_colors
        driver_colors[driver] = driver_color
        st.write(driver_colors)
        
        # Extrai as informações desejadas para o piloto atual: Nome, Tempo de volta, setores e composto do pneu
        piloto_info = {
            'Driver': driver,  # Nome do piloto
            'Lap Time (sec)': fastest_driver['LapTime'],
            'Sector 1 (sec)': fastest_driver['Sector1Time'],
            'Sector 2 (sec)': fastest_driver['Sector2Time'],
            'Sector 3 (sec)': fastest_driver['Sector3Time'],
            'Compound': fastest_driver['Compound'],
        }
        st.write(piloto_info)

        # Adiciona as informações do piloto à lista pilotos_info
        pilotos_info.append(piloto_info)

    # Cria um dataframe df com todas as informações de cada piloto deste sessão
    df = pd.DataFrame(pilotos_info)

    # Formata as colunas de tempo para exibição dos tempos em segundos
    # Por exemplo, se x for um objeto timedelta representando 2 minutos e 30 segundos
    # x.total_seconds() retorna 150 segundos 
    # (porque 2 minutos * 60 segundos/minuto + 30 segundos = 150 segundos).
    # A função total_seconds() é um método nativo em objetos do tipo timedelta em Python.
    df['Lap Time (sec)'] = df['Lap Time (sec)'].apply(lambda x: float(x.total_seconds()))
    df['Sector 1 (sec)'] = df['Sector 1 (sec)'].apply(lambda x: float(x.total_seconds()))
    df['Sector 2 (sec)'] = df['Sector 2 (sec)'].apply(lambda x: float(x.total_seconds()))
    df['Sector 3 (sec)'] = df['Sector 3 (sec)'].apply(lambda x: float(x.total_seconds()))
    st.write(df)

    # Seleciona apenas as colunas necessárias, separa em 4 tabelas e ordena os pelos tempos de setor e volta
    table1 = df[['Driver', 'Sector 1 (sec)', 'Compound']].sort_values(by='Sector 1 (sec)').reset_index(drop=True)
    st.write(table1)
    table2 = df[['Driver', 'Sector 2 (sec)', 'Compound']].sort_values(by='Sector 2 (sec)').reset_index(drop=True)
    st.write(table2)
    table3 = df[['Driver', 'Sector 3 (sec)', 'Compound']].sort_values(by='Sector 3 (sec)').reset_index(drop=True)
    st.write(table3)
    table4 = df[['Driver', 'Lap Time (sec)', 'Compound']].sort_values(by='Lap Time (sec)').reset_index(drop=True)
    st.write(table4)

    # Por padrão o index começa com 0, vamos adicionar 1 no início da contagem para servir como informação
    # de posição 
    table1.index += 1 
    table2.index += 1 
    table3.index += 1 
    table4.index += 1 

    # Função que aplica as cores de cada piloto na tabela de setores e tempo de volta
    def apply_color(row, driver_colors):
        driver = row['Driver']
        # Obtém a cor correspondente ao piloto ou vazio se não houver
        color = driver_colors.get(driver, '')  
        # Define a cor do texto como preto se houver uma cor de fundo, caso contrário, vazio
        text_color = 'black' if color else '' 
        # Define o estilo de texto como negrito se houver uma cor de fundo, caso contrário, vazio
        text_style = 'font-weight: bold' if color else ''  
        return [f'background-color: {color}; color: {text_color}; {text_style}' if cell == driver else '' for cell in row]


    # Aplicar a função de estilo para todas as linhas de cada tabela
    styled_table1 = table1.style.apply(apply_color, driver_colors=driver_colors, axis=1)
    styled_table2 = table2.style.apply(apply_color, driver_colors=driver_colors, axis=1)
    styled_table3 = table3.style.apply(apply_color, driver_colors=driver_colors, axis=1)
    styled_table4 = table4.style.apply(apply_color, driver_colors=driver_colors, axis=1)
    
    # Cria tabs para exibir as tabelas uma ao lado da outra na horizontal
    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Exibe a tabela de tempos do setor 1
            st.table(styled_table1.format(precision=3))

        with col2:
            # Exibe a tabela de tempos do setor 2
            st.table(styled_table2.format(precision=3))

        with col3:
            # Exibe a tabela de tempos do setor 3
            st.table(styled_table3.format(precision=3))

        with col4:
            # Exibe a tabela dos tempos de volta
            st.table(styled_table4.format(precision=3))

##################################################################################################

##################################################################################################
# PARTE 5: CRIANDO GRÁFICO DE VELOCIDADES
##################################################################################################

with tabs[2]:

    # Cria a lista para armazenar as informações dos pilotos        
    pilotos_info = []
    # Cria o dicionário para armazenar as cores de cada piloto       
    driver_colors = {}
    # Extrai todos os nomes de pilotos únicos dos dados selecionados
    drivers = data.laps.Driver.unique()

    # Bloco de loop que itera sobre cada piloto único da lista drivers
    for driver in drivers:
        # Seleciona o dado das voltas deste piloto
        laps_driver = data.laps.pick_driver(driver)
        # Seleciona o dado da volta mais rápida deste piloto
        fastest_driver = laps_driver.pick_fastest()
        # Seleciona o time deste piloto
        team = data.laps.pick_driver(driver).pick_fastest()['Team']

        # Verifique se 'team' é NaN e defina 'team_color' como branco neste caso
        if pd.isna(team):
            team_color = 'white'
        # Senão define team_color como a cor definida pela biblioteca Fast F1 para esta equipe
        else:
            team_color = plotting.team_color(team)

        # Tenta extrair a cor do piloto através dos métodos .plotting.driver_color        
        try:
            # Armazena a cor na variável driver_color
            driver_color = ff1.plotting.driver_color(driver)
        # Se erro, define a variável driver_color com a cor da equipe deste piloto
        except KeyError:
            driver_color = team_color

        # Adiciona a cor (valor) para o pilto (chave) correspondente no dicionário driver_colors
        driver_colors[driver] = driver_color

        # Extrai as informações desejadas para o piloto atual: Nome e velocidades
        piloto_info = {
            'Driver': driver,  # Nome do piloto
            'Sector 1 Speed': fastest_driver['SpeedI1'],
            'Sector 2 Speed': fastest_driver['SpeedI2'],
            'Finish Line Speed': fastest_driver['SpeedFL'],
            'Longest Straight Speed': fastest_driver['SpeedST'],
        }

        # Adiciona as informações do piloto à lista pilotos_info
        pilotos_info.append(piloto_info)
        
    # Cria um dataframe df com todas as informações de cada piloto deste sessão
    df_speed = pd.DataFrame(pilotos_info)
    st.write(df_speed)

##################################################################################################
# PARTE 5.1: CRIANDO OS GRÁFICOS 
##################################################################################################

    # Ajuste de escala do eixo y
    max_y_value_speed = df_speed['Sector 1 Speed'].max()*1.01
    min_y_value_speed = df_speed['Sector 1 Speed'].max()*0.80

    # Cria o gráfico de barras com Plotly para o Setor 1 e aplica as cores com o dicionário driver_colors
    fig_sector1 = px.bar(df_speed, x='Driver', y='Sector 1 Speed', color='Driver', color_discrete_map=driver_colors)
    # Define título, eixos e escala
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
        yaxis=dict(range=[min_y_value_speed, max_y_value_speed]) 
    )

    # Exibe o gráfico de barras de velocidade do Setor 1
    st.plotly_chart(fig_sector1, use_container_width=True)

    # Cria o gráfico de barras com Plotly para o Setor 2 e aplica as cores com o dicionário driver_colors
    fig_sector2 = px.bar(df_speed, x='Driver', y='Sector 2 Speed', color='Driver', color_discrete_map=driver_colors)
    # Define título, eixos e escala    
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
        yaxis=dict(range=[min_y_value_speed, max_y_value_speed]) 
    )

    # Exibe o gráfico de barras de velocidade do Setor 2
    st.plotly_chart(fig_sector2, use_container_width=True)

    # Cria o gráfico de barras com Plotly para o Finish Line Speed e aplica as cores com o dicionário driver_colors
    fig_flspeed = px.bar(df_speed, x='Driver', y='Finish Line Speed', color='Driver', color_discrete_map=driver_colors)
    # Define título, eixos e escala        
    fig_flspeed.update_layout(
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
        yaxis=dict(range=[min_y_value_speed, max_y_value_speed]) 
    )

    # Exibe o gráfico de barras de velocidade do Finish Line Speed
    st.plotly_chart(fig_flspeed, use_container_width=True)

    # Cria o gráfico de barras com Plotly para o Longest Straight Speed e aplica as cores com o dicionário driver_colors
    fig_lsspeed = px.bar(df_speed, x='Driver', y='Longest Straight Speed', color='Driver', color_discrete_map=driver_colors)
    # Define título, eixos e escala            
    fig_lsspeed.update_layout(
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
        yaxis=dict(range=[min_y_value_speed, max_y_value_speed]) 
    )

    # Exibe o gráfico de barras de velocidade do Longest Straight Speed
    st.plotly_chart(fig_lsspeed, use_container_width=True)

##################################################################################################

##################################################################################################
# PARTE 6: CRIANDO OS MAPAS COM MARCHAS E VELOCIDADE NA PISTA
##################################################################################################

with tabs[3]:

    # Faz a tentativa de extrair os dados de telemetria desta sessão, caso contrário exibe a mensagem de erro
    # "We do not have telemetry data for this session"
    try:
        # Extrai as informações da volta mais rápida desta sessão 
        lap = data.laps.pick_fastest()
        st.write(lap)
        # Extrai a telemetria da volta mais rápida dessa sessão
        tel = lap.get_telemetry()
        st.write(tel)

        # Extrai as coordenadas em 'X' da volta para criação do mapa da pista e converte numa array Numpy
        x = np.array(tel['X'].values)
        st.write(x)
        # Extrai as coordenadas em 'Y' da volta para criação do mapa da pista e converte numa array Numpy
        y = np.array(tel['Y'].values)
        st.write(y)

        # Cria um título para os gráficos com as informações do nome do piloto, evento e ano
        st.markdown(f"### {lap['Driver']} - {data.event['EventName']} {data.event.year}")

        # Cria as tabs para exibir os mapas de marcha e velocidade um ao lado do outro (horizontal)
        with st.container():

            col1, col2 = st.columns(2)

            # O mapa das marchas na pista é exibido na coluna 1
            with col1:

                # Os arrays x e y são combinados em um array tridimensional, onde cada ponto da pista 
                # é representado por um par de coordenadas (x, y). 
                # A função .T transpõe o array para garantir que as coordenadas estejam no formato correto.
                points = np.array([x, y]).T.reshape(-1, 1, 2)
                st.write(points)
                
                # os segmentos entre os pontos são criados. 
                # O array segments contém pares de pontos consecutivos, formando segmentos de linha.
                segments = np.concatenate([points[:-1], points[1:]], axis=1)
                st.write(segments)

                # A coluna 'nGear' dos dados de telemetria é extraída e convertida em um array NumPy de tipo float. 
                # Esta coluna contém informações sobre a marcha utilizada em cada ponto da pista.
                gear = tel['nGear'].to_numpy().astype(float)
                st.write(gear)

                #  Um mapa de cores (cmap) é definido usando a função get_cmap() do módulo matplotlib.cm.
                cmap = cm.get_cmap('Paired')
                st.write(cmap)

                #  Uma coleção de linhas (LineCollection) é criada usando os segmentos de linha e o mapa de cores. 
                # A normalização é realizada com base na escala de marchas para mapear cores diferentes 
                # para diferentes marchas.
                lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N+1), cmap=cmap)

                # A coleção de linhas é associada com os valores de marcha (gear) para determinar 
                # a cor de cada segmento de linha.
                lc_comp.set_array(gear)

                #  Define a largura das linhas na coleção de linhas.
                lc_comp.set_linewidth(4)

                # Cria uma nova figura (fig) e um conjunto de eixos (ax) para o gráfico. 
                # O tamanho da figura é definido como 6x4 polegadas.
                fig_track_gear, ax = plt.subplots(figsize=(6, 4))

                # Adiciona a coleção de linhas aos eixos.
                ax.add_collection(lc_comp)

                # Garante que a escala dos eixos seja igual, para evitar distorções na visualização.
                ax.axis('equal')

                # Remove os rótulos e os ticks dos eixos para proporcionar uma visualização mais limpa.
                ax.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

                # Adiciona uma barra de cores para representar as marchas. 
                # A função colorbar() cria a barra de cores e mappable=lc_comp especifica 
                # qual objeto de mapa de cores está associado à barra. 
                # boundaries define os limites das cores com base nas marchas de 1 a 9.
                cbar = plt.colorbar(mappable=lc_comp, label="Gear", boundaries=np.arange(1, 10))

                # Remove a borda ao redor do gráfico
                ax.set_frame_on(False)

                # Exibe o gráfico no Streamlit usando a função st.pyplot().
                st.pyplot(fig_track_gear)

            # O mapa das velocidades na pista é exibido na coluna 2
            with col2:

                # Extrai a velocidade (Speed) dos dados de telemetria da volta mais rápida 
                # e armazena na variável color. 
                # Essa será a base para a escala de cores do gráfico.
                color = lap.telemetry['Speed']  
                st.write(color)
                # Cria um array tridimensional de pontos (x, y) que representam a pista. 
                # Esta estrutura é semelhante à utilizada no primeiro gráfico.
                points = np.array([x, y]).T.reshape(-1, 1, 2)
                st.write(points)
                # Define os segmentos de linha conectando pontos consecutivos na pista, 
                # semelhante ao primeiro gráfico.
                segments = np.concatenate([points[:-1], points[1:]], axis=1)
                st.write(segments)

                #  Define o mapa de cores (colormap) como 'plasma' do módulo de cores do Matplotlib.
                colormap = mpl.cm.plasma
                st.write(colormap)
                # Normaliza os valores de velocidade para garantir que estejam na mesma escala de cores.
                norm = plt.Normalize(color.min(), color.max())
                # ria uma coleção de linhas (LineCollection) com base nos segmentos, usando o mapa de cores e a normalização. 
                # As linhas são estilizadas como contínuas (linestyle='-') e têm uma largura de 5 pixels (linewidth=5).
                lc = LineCollection(segments, cmap=colormap, norm=norm, linestyle='-', linewidth=5)
                # Associa os valores de velocidade à coleção de linhas para determinar a cor de cada segmento de linha.
                lc.set_array(color)

                # Cria uma nova figura (fig2) e um conjunto de eixos (ax) para o gráfico. 
                # O tamanho da figura é definido como 6x4.440 polegadas.
                fig_track_speed, ax = plt.subplots(figsize=(6, 4.440))
                # Ajusta a disposição do subplots dentro da figura.
                plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
                # Remove os eixos do gráfico para proporcionar uma visualização mais limpa.
                ax.axis('off')

                # Adiciona uma linha preta representando a pista de corrida ao fundo do gráfico. 
                # A linha tem uma largura de 16 pixels (linewidth=16).
                ax.plot(lap.telemetry['X'], lap.telemetry['Y'], color='black', linestyle='-', linewidth=16, zorder=0)

                # Adiciona a coleção de linhas coloridas (lc) ao gráfico.
                line = ax.add_collection(lc)

                # Adiciona uma barra de cores para representar as velocidades. 
                # A barra de cores é associada à coleção de linhas coloridas (lc) e é rotulada como "Speed".
                cbar = plt.colorbar(mappable=lc, label="Speed")

                #  Exibe o gráfico no Streamlit usando a função st.pyplot().
                st.pyplot(fig_track_speed)

    except Exception:
        st.warning("We do not have telemetry data for this session")

##################################################################################################

##################################################################################################
# PARTE 7: PERFORMANCE DOS PNEUS: TEMPO DE VOLTA X COMPOSTO DE PNEU
##################################################################################################

with tabs[4]:

    # Extrai todos os nomes de pilotos únicos dos dados selecionados
    drivers = data.laps.Driver.unique()
    st.write(drivers)

    # Cria duas colunas para exibir o gráfico de dispersão
    # Os gráficos são iguais, a ideia é justamente poder comparar 2 pilotos diferentes
    with st.container():
        col1, col2 = st.columns(2)

        # Coluna 1 para o primeiro gráfico de dispersão
        with col1:

            # Cria um seletor para escolher um dentre os pilotos da sessão
            selected_drivers = st.selectbox('Select Driver:', drivers, key='Tyre Performance Col1')
            st.write(selected_drivers)

            # Extrai os dados de volta deste piloto com o método .pick_driver e depois filtra
            # apenas as voltas rápidas deste piloto com o método pick_quicklaps
            driver_laps = data.laps.pick_driver(selected_drivers).pick_quicklaps().reset_index()
            st.write(driver_laps)

            # Converte o tempo de volta de um formato de duração (Timedelta) para um formato de string 
            # com minutos e segundos
            #
            # Explicando com detalhes a função a seguir:
            #
            # -> lambda x: ...: Isso é uma expressão lambda em Python, uma forma concisa de definir uma função anônima. Nesse caso, x representa cada valor individual na coluna 'LapTime'.
            # -> x.total_seconds()//60:02.0f: x.total_seconds() converte o valor de tempo em segundos. //60 faz a divisão inteira por 60 para obter o número de minutos, :02.0f formata o número de minutos para ocupar pelo menos 2 caracteres, preenchendo com zeros à esquerda se necessário.
            # -> x.total_seconds()%60:06.3f: x.total_seconds()%60 obtém o resto da divisão por 60 para obter os segundos. :06.3f formata os segundos para ocupar pelo menos 6 caracteres, com 3 casas decimais após o ponto decimal.
            # -> No final, a expressão formata o valor de tempo em minutos e segundos no formato 'MM:SS.SSS'. Por exemplo, se x.total_seconds() fosse 121.345 segundos, a expressão o formataria como '02:01.345'. Isso é útil para apresentar tempos de volta de maneira mais compreensível em gráficos ou tabelas.
           
            driver_laps['LapTime'] = driver_laps['LapTime'].apply(lambda x: f"{x.total_seconds()//60:02.0f}:{x.total_seconds()%60:06.3f}")
            st.write(driver_laps['LapTime'])

            # Cria um gráfico de dispersão usando o Plotly Express, com o número da volta (LapNumber) no eixo x, 
            # o tempo da volta (LapTime) no eixo y e a cor das bolhas baseada no tipo de pneu (Compound). 
            # O mapa de cores para os tipos de pneu é definido pelo atributo color_discrete_map
            fig = px.scatter(driver_laps, x="LapNumber", y="LapTime", color="Compound",
                            color_discrete_map=ff1.plotting.COMPOUND_COLORS)

            # Define o rótulo do eixo x como "Lap Number"
            fig.update_xaxes(title="Lap Number")
            # Define o rótulo do eixo y como "Lap Time"
            fig.update_yaxes(title="Lap Time")

            # Cria uma lista de tempos de volta únicos ordenados para determinar a ordem no eixo y
            laptime_order = driver_laps.sort_values(by="LapTime")["LapTime"].unique()
            # Define a ordem dos valores no eixo y conforme a lista laptime_order.
            fig.update_yaxes(categoryorder="array", categoryarray=laptime_order)
            # Atualiza o layout do gráfico para mostrar a legenda
            fig.update_layout(showlegend=True)
            # Define o tamanho e a largura da linha das bolhas no gráfico
            fig.update_traces(marker=dict(size=10, line=dict(width=0)))

            # Exibe o gráfico de dispersão usando a função plotly_chart do Streamlit,
            #  que permite a visualização interativa do gráfico
            st.plotly_chart(fig, use_container_width=True)

        # Coluna 2 para o segundo gráfico de dispersão
        with col2:

            selected_drivers = st.selectbox('Select Driver:', drivers, key='Tyre Performance Col2')
            st.write(selected_drivers)

            driver_laps = data.laps.pick_driver(selected_drivers).pick_quicklaps().reset_index()
            st.write(driver_laps)

            driver_laps['LapTime'] = driver_laps['LapTime'].apply(lambda x: f"{x.total_seconds()//60:02.0f}:{x.total_seconds()%60:06.3f}")
            st.write(driver_laps['LapTime'])

            fig = px.scatter(driver_laps, x="LapNumber", y="LapTime", color="Compound",
                            color_discrete_map=ff1.plotting.COMPOUND_COLORS)

            fig.update_xaxes(title="Lap Number")
            fig.update_yaxes(title="Lap Time")

            laptime_order = driver_laps.sort_values(by="LapTime")["LapTime"].unique()
            fig.update_yaxes(categoryorder="array", categoryarray=laptime_order)

            fig.update_layout(showlegend=True)
            fig.update_traces(marker=dict(size=10, line=dict(width=0)))

            st.plotly_chart(fig, use_container_width=True)

##################################################################################################

##################################################################################################
# PARTE 8: ESTRATÉGIA DE UTILIZAÇÃO DE PNEUS
##################################################################################################

with tabs[5]:

    # Cria um dicionário com as cores que serão utilizadas para cada tipo de pneu
    compound_colors = {
        'SOFT': '#FF3333',
        'MEDIUM': '#FFF200',
        'HARD': '#EBEBEB',
        'INTERMEDIATE': '#39B54A',
        'WET': '#00AEEF',
    }

    # Cria um DataFrame chamado driver_stints que contém informações sobre os pilotos, os stints
    #  e os compostos de pneus usados por cada piloto durante a corrida. 
    # Ele agrupa os dados pelos pilotos, stints e compostos e conta o número de voltas em cada stint.
    driver_stints = data.laps[['Driver', 'Stint', 'Compound', 'LapNumber']].groupby(
        ['Driver', 'Stint', 'Compound']
    ).count().reset_index()
    st.write(driver_stints)

    # Renomeia a coluna 'LapNumber' para 'StintLength' para representar o comprimento de cada stint
    driver_stints = driver_stints.rename(columns={'LapNumber': 'StintLength'})
  
    # Ordena o DataFrame com base na coluna 'Stint' em ordem crescente
    driver_stints = driver_stints.sort_values(by=['Stint'])
    st.write(driver_stints)

    # Define o tamanho da figura para 15x10 polegadas
    plt.rcParams["figure.figsize"] = [15, 10]
    plt.rcParams["figure.autolayout"] = True

    # Cria uma nova figura e um conjunto de eixos para o gráfico.
    fig, ax = plt.subplots()

    # Bloco de loop que itera sobre a lista dos pilotos na corrida
    for driver in data.results['Abbreviation']:
        # Seleciona os stints do piloto atual no loop
        stints = driver_stints.loc[driver_stints['Driver'] == driver]
        st.write(stints)
        

        previous_stint_end = 0

        # Bloco for que itera sobre os stints do piloto atual no loop
        for _, stint in stints.iterrows():

            # Armazena o nome do composto do pneu na variável compound
            compound = stint['Compound']
            st.write(compound)
            
            # Verifique se o composto de pneu existe no dicionário e 
            # cria barras horizontais para representar os stints de cada piloto.
            # A largura de cada barra é determinada pela coluna 'StintLength'. 
            # O argumento left especifica a posição horizontal de início da barra no gráfico. 
            # A cor da barra é determinada pelo composto de pneu usado, usando o dicionário compound_colors.
            if compound in compound_colors:
                plt.barh(
                    [driver], 
                    stint['StintLength'], 
                    left=previous_stint_end, 
                    color=compound_colors[compound], 
                    edgecolor="black"
                )
            else:
                # Se o composto de pneu não estiver no dicionário usa uma cor padrão 
                plt.barh(
                    [driver], 
                    stint['StintLength'], 
                    left=previous_stint_end, 
                    color='gray',  
                    edgecolor="black"
                )

            # Atualiza a posição horizontal de início da próxima barra para o piloto atual no loop
            # Isso é usado para posicionar as próximas barras ao lado das anteriores
            previous_stint_end = previous_stint_end + stint['StintLength']

    # diciona um rótulo ao eixo x, indicando o número da volta
    plt.xlabel('Lap')

    # Inverte o eixo y para que os stints dos pilotos sejam exibidos na ordem correta de cima para baixo
    plt.gca().invert_yaxis()

    # Removem as bordas do gráfico.
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Cria um dicionário chamado used_colors que contém apenas os compostos de pneu 
    # que estão presentes nos stints dos pilotos
    used_colors = {compound: color for compound, color in compound_colors.items() if compound in driver_stints['Compound'].unique()}
    st.write(used_colors)
    
    # Cria uma lista de identificadores para a legenda
    handles = []

    # Itera sobre used_colors e cria retângulos coloridos para cada composto de pneu conhecido, 
    # adicionando-os à lista handles
    for compound, color in used_colors.items():
        handles.append(plt.Rectangle((0, 0), 1, 1, color=color, label=compound))

    # Adiciona um retângulo cinza para 'TEST_UNKNOWN'
    handles.append(plt.Rectangle((0, 0), 1, 1, color='gray', label='TEST_UNKNOWN'))

    # Adiciona a legenda ao gráfico no canto esquerdo do gráfico
    ax.legend(handles=handles, title='Compounds', loc='center left', bbox_to_anchor=(1, 0.5))

    # Exiba o gráfico no Streamlit
    st.pyplot(fig)