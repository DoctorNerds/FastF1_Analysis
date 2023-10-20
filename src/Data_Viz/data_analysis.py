import streamlit as st
import fastf1 as ff1
import plotly.graph_objects as go
import plotly.subplots as sp
from fastf1 import utils  

def data_analysis(data, selected_season, selected_event, selected_session):

    drivers = data.laps.Driver.unique()

    # Widget de seleção de Car Numbers
    selected_drivers = st.multiselect('Select Driver:', drivers, key='Best Lap Data Analysis')

    # Crie um dicionário para armazenar os pilotos selecionados
    driver_dict = {}

    # Preencha o dicionário com os pilotos selecionados
    for i, driver in enumerate(selected_drivers, start=1):
        key = f"driver_{i}"  # Gere a chave dinamicamente
        driver_dict[key] = driver

    # Verifique se há apenas um driver selecionado
    if len(selected_drivers) == 1:
        row_heights = [1, 0.5, 5, 1, 1, 1, 0.5]
    else:
        row_heights = [1, 1, 0.5, 5, 1, 1, 0.5]
    
    variable_names_driver = ['RPM', 'Gear', 'Speed', 'Throttle', 'Brake', 'DRS']
    variable_names_drivers = ['Gap to Ref.', 'RPM', 'Gear', 'Speed', 'Throttle', 'Brake', 'DRS']

    # Crie um novo objeto de subplot com escalas independentes
    fig = sp.make_subplots(rows=7, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=row_heights)

    if selected_drivers:

        # Verifique se há apenas um driver selecionado
        if len(selected_drivers) == 1:
            driver = selected_drivers[0]
            # Obtenha a telemetria para o driver atual
            laps_driver = data.laps.pick_driver(driver)
            fastest_driver = laps_driver.pick_fastest()

            try:
                telemetry_driver = fastest_driver.get_telemetry().add_distance()
            except Exception as e:
                st.warning("We do not have telemetry data for this driver in this session.")
                telemetry_driver = None  

            if telemetry_driver is not None:

                # Adicione as linhas para as diferentes variáveis em subplots separados com cores padrão
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


                try:
                    telemetry_driver = fastest_driver.get_telemetry().add_distance()
                except Exception as e:
                    st.warning("We do not have telemetry data for these drivers in this session.")
                    telemetry_driver = None  

                if telemetry_driver is not None:

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
                    fig.update_yaxes(showticklabels=False, row=j, col=i)

            # Adicione nomes das variáveis no eixo Y
            for j, variable_name in enumerate(variable_names_drivers, start=1):
                fig.update_yaxes(title_text=variable_name, row=j, col=1)

            # Use o st.plotly_chart para exibir o gráfico no Streamlit
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Select at least one driver.")

