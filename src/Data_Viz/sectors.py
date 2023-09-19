import streamlit as st
import fastf1 as ff1
import pandas as pd

from fastf1 import plotting

def sectors(data, selected_season, selected_event, selected_session):

    pilotos_info = []     
    driver_colors = {}
    drivers = data.laps.Driver.unique()

    for driver in drivers:
        laps_driver = data.laps.pick_driver(driver)
        fastest_driver = laps_driver.pick_fastest()
        team = data.laps.pick_driver(driver).pick_fastest()['Team']
        
        # Verifique se 'team' é NaN e defina 'team_color' em conformidade
        if pd.isna(team):
            team_color = 'white'
        else:
            team_color = plotting.team_color(team)

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