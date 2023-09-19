import streamlit as st
from matplotlib import pyplot as plt

def tyre_strategy(data, selected_season, selected_event, selected_session):

    compound_colors = {
        'SOFT': '#FF3333',
        'MEDIUM': '#FFF200',
        'HARD': '#EBEBEB',
        'INTERMEDIATE': '#39B54A',
        'WET': '#00AEEF',
    }
        
    # Enable the cache
    #cache_folder = os.path.join(os.path.dirname(__file__), 'cache_data')
    #ff1.Cache.enable_cache(cache_folder)

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
            #plt.title(f'{selected_session} strategy - {selected_event} {selected_season}')

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