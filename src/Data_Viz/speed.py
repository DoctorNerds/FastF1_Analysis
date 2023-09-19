import streamlit as st
import fastf1 as ff1
import pandas as pd
import plotly.express as px

from fastf1 import plotting

def speed(data, selected_season, selected_event, selected_session):

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