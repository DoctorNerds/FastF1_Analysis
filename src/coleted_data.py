import fastf1 as ff1
import os

# Define the years
years = [2021, 2022, 2023]

# Enable the cache
cache_folder = os.path.join(os.path.dirname(__file__), 'cache_data')
ff1.Cache.enable_cache(cache_folder)

def collect_and_cache_data():
    session_names = ['Session1', 'Session2', 'Session3', 'Session4', 'Session5']


    for year in years:
        events = ff1.get_event_schedule(year)
        for event in events['OfficialEventName']:
            sessions = ff1.get_event(year, event)
            for session_name in session_names:
                session = sessions[session_name]
                session_data = ff1.get_session(year, event, session)
                session_data.load()


def collect_and_cache_fault_data():

    session_names = ['Session1', 'Session2', 'Session3', 'Session4', 'Session5']
    event='Singapore'
    year = 2023

    sessions = ff1.get_event(year, event)

    for session_name in session_names:
        session = sessions[session_name]
        session_data = ff1.get_session(year, event, session)
        session_data.load()

if __name__ == "__main__":
    #collect_and_cache_data()
    collect_and_cache_fault_data()

