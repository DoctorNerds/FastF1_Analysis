import streamlit as st
import numpy as np

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import cm

def track_speed_gear(data, selected_season, selected_event, selected_session):

    # Enable the cache
    #cache_folder = os.path.join(os.path.dirname(__file__), 'cache_data')
    #ff1.Cache.enable_cache(cache_folder)
        
    try:
        lap = data.laps.pick_fastest()
        tel = lap.get_telemetry()

        x = np.array(tel['X'].values)
        y = np.array(tel['Y'].values)

        # Crie um título comum
        st.markdown(f"### {lap['Driver']} - {data.event['EventName']} {data.event.year}")
        #st.title(f"{lap['Driver']} - {data.event['EventName']} {data.event.year}")

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

    except Exception:
        st.warning("We do not have telemetry data for this session")

