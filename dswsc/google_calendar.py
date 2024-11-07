import json
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import List

from .config import settings
from .utils import get_offset_from_timezone
from .events import EventDetails


SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    """
    Authenticate with Google Calendar using service account credentials.
    """
    service_account_info = json.loads(settings.google_service_account_key)
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    return creds

def clear_event_from_date(calendar_id: str, date: datetime):
    """
    Clear all future events from the specified date in the Google Calendar.
    """
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)

    offset = get_offset_from_timezone(settings.timezone)
    date_formatted = '{date}{sign}{offset:02d}:00'.format(
        date=date.strftime('%Y-%m-%dT%H:%M:%S'),
        sign='+' if offset >= 0 else '-',
        offset=offset
    )

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=date_formatted,
        timeZone=settings.timezone,
        singleEvents=True,
    ).execute()
    events = events_result.get('items', [])

    print(f'Clearing {len(events)} events...')
    
    for event in events:
        service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
    
    print('Events cleared!')

def add_events_to_google_calendar(events: List[EventDetails], calendar_id: str):
    """
    Add events to the specified Google Calendar.
    """
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)
    
    print(f'Adding {len(events)} events to Google Calendar...')
    
    for event_details in events:
        event = {
            'summary': event_details.summary,
            'description': event_details.description,
            'start': {
                'dateTime': event_details.start.isoformat(),
                'timeZone': event_details.timeZone,
            },
            'end': {
                'dateTime': event_details.end.isoformat(),
                'timeZone': event_details.timeZone,
            },
            'location': event_details.location,
        }

        service.events().insert(calendarId=calendar_id, body=event).execute()
            
    print('Events added!')
