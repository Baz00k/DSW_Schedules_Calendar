import requests
from urllib.parse import quote
from datetime import datetime, timedelta
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from icalendar import Calendar

from .config import settings


def generate_url(id, start_date, end_date):
    base_url = 'https://harmonogramy.dsw.edu.pl/Plany/WydrukTokuical/'
    query_string = f'dO={start_date}&dD={end_date}'
    encoded_query_string = quote(query_string, safe='=&')
    return f'{base_url}{id}?{encoded_query_string}'

def authenticate_google_calendar():
    service_account_info = json.loads(settings.google_service_account_key)
    creds = Credentials.from_service_account_info(service_account_info, scopes=['https://www.googleapis.com/auth/calendar'])
    return creds

def clear_future_events(calendar_id):
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)

    # Get the current time
    now = datetime.now().isoformat() + 'Z'

    # List all future events in the calendar
    events_result = service.events().list(calendarId=calendar_id, timeMin=now).execute()
    events = events_result.get('items', [])

    # Delete each future event
    for event in events:
        service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
        print(f'Future event deleted: {event["id"]}')

def add_events_to_google_calendar(schedule_ical, calendar_id):
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)

    cal = Calendar.from_ical(schedule_ical)
    for component in cal.walk():
        if component.name == "VEVENT":
            print(component.get('dtstart').dt.isoformat())
            continue

            event = {
                'summary': str(component.get('summary')),
                'location': str(component.get('location')),
                'description': str(component.get('description')),
                'start': {
                    'dateTime': component.get('dtstart').dt.isoformat(),
                    'timeZone': 'Europe/Warsaw',
                },
                'end': {
                    'dateTime': component.get('dtend').dt.isoformat(),
                    'timeZone': 'Europe/Warsaw',
                },
            }
            event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f'Event created: {event.get("htmlLink")}')

def main():
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(weeks=4)).strftime('%Y-%m-%d')

    set_date_range_url = f'https://harmonogramy.dsw.edu.pl/Plany/PlanyTokowGridCustom/{settings.group_id}'
    set_date_range_data = {
        'DXCallbackName': 'gridViewPlanyTokow',
        'parametry': f'{start_date};{end_date};5;{settings.group_id}',
        'id': settings.group_id,
    }

    with requests.Session() as session:
        # Simulate setting the date range
        session.get(f'https://harmonogramy.dsw.edu.pl/Plany/PlanyTokow/{settings.group_id}')

        # Get session cookie
        session_cookie = session.cookies.get_dict()['ASP.NET_SessionId']
        print(f'Aquired session cookie: {session_cookie}')

        response = session.post(set_date_range_url, data=set_date_range_data)
        if response.status_code != 200:
            print('Failed to set date range')
            return

        # Generate the URL to fetch the schedule
        url = generate_url(settings.group_id, start_date, end_date)

        # Fetch the schedule
        response = session.get(url)
        schedule_ical = response.text

    clear_future_events(settings.google_calendar_id)
    add_events_to_google_calendar(schedule_ical, settings.google_calendar_id)

if __name__ == '__main__':
    main()
