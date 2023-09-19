import streamlit as st
import fastf1 as ff1
import plotly.express as px

def tyre_performance(data, selected_season, selected_event, selected_session):

    # Enable the cache
    #cache_folder = os.path.join(os.path.dirname(__file__), 'cache_data')
    #ff1.Cache.enable_cache(cache_folder)

    drivers = data.laps.Driver.unique()

    with st.container():
        col1, col2 = st.columns(2)

        with col1:

            # Widget de seleção de Car Numbers
            selected_drivers = st.selectbox('Select Driver:', drivers, key='Tyre Performance Col1')

            driver_laps = data.laps.pick_driver(selected_drivers).pick_quicklaps().reset_index()

            driver_laps['LapTime'] = driver_laps['LapTime'].apply(lambda x: f"{x.total_seconds()//60:02.0f}:{x.total_seconds()%60:06.3f}")

            # Criar o gráfico com Plotly Express
            fig = px.scatter(driver_laps, x="LapNumber", y="LapTime", color="Compound",
                            color_discrete_map=ff1.plotting.COMPOUND_COLORS)

            # Configurações de layout
            fig.update_xaxes(title="Lap Number")
            fig.update_yaxes(title="Lap Time")

            #fig.update_yaxes(autorange="reversed")  # Inverte o eixo y
            laptime_order = driver_laps.sort_values(by="LapTime")["LapTime"].unique()
            fig.update_yaxes(categoryorder="array", categoryarray=laptime_order)
            
            #fig.update_yaxes(autorange="reversed")  # Inverte o eixo y
            fig.update_layout(showlegend=True)
            fig.update_traces(marker=dict(size=10, line=dict(width=0)))

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig, use_container_width=True)

        with col2:

            # Widget de seleção de Car Numbers
            selected_drivers = st.selectbox('Select Driver:', drivers, key='Tyre Performance Col2')

            driver_laps = data.laps.pick_driver(selected_drivers).pick_quicklaps().reset_index()

            # Formate o LapTime diretamente no formato minuto:segundo:decimo,centesimo,milesimo
            driver_laps['LapTime'] = driver_laps['LapTime'].apply(lambda x: f"{x.total_seconds()//60:02.0f}:{x.total_seconds()%60:06.3f}")

            # Criar o gráfico com Plotly Express
            fig = px.scatter(driver_laps, x="LapNumber", y="LapTime", color="Compound",
                            color_discrete_map=ff1.plotting.COMPOUND_COLORS)

            # Configurações de layout
            fig.update_xaxes(title="Lap Number")
            fig.update_yaxes(title="Lap Time")

            #fig.update_yaxes(autorange="reversed")  # Inverte o eixo y
            laptime_order = driver_laps.sort_values(by="LapTime")["LapTime"].unique()
            fig.update_yaxes(categoryorder="array", categoryarray=laptime_order)

            fig.update_layout(showlegend=True)
            fig.update_traces(marker=dict(size=10, line=dict(width=0)))

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig, use_container_width=True)