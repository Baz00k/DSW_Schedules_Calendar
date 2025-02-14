import json
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import List

from .config import settings
from .utils import get_offset_from_timezone
from .events import EventDetails


SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarService:
    _instance = None

    @classmethod
    def get_instance(cls):
        """Get or create a Google Calendar service instance."""

        if cls._instance is None:
            service_account_info = json.loads(settings.google_service_account_key)
            creds = Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES
            )
            cls._instance = build("calendar", "v3", credentials=creds)
        return cls._instance


def clear_event_from_date(calendar_id: str, date: datetime):
    """
    Clear all future events from the specified date in the Google Calendar.
    """
    service = CalendarService.get_instance()

    offset = get_offset_from_timezone(settings.timezone)
    date_formatted = f"{date.strftime('%Y-%m-%dT%H:%M:%S')}{'+' if offset >= 0 else '-'}{abs(offset):02d}:00"

    page_token = None
    total_deleted = 0

    while True:
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=date_formatted,
                timeZone=settings.timezone,
                singleEvents=True,
                maxResults=250,
                pageToken=page_token,
            )
            .execute()
        )

        events = events_result.get("items", [])
        if not events:
            break

        batch = service.new_batch_http_request()
        for event in events:
            batch.add(
                service.events().delete(calendarId=calendar_id, eventId=event["id"])
            )
        batch.execute()

        total_deleted += len(events)

        page_token = events_result.get("nextPageToken")
        if not page_token:
            break

    if total_deleted > 0:
        print(f"Successfully cleared {total_deleted} events!")
    else:
        print("No events to clear")


def add_events_to_google_calendar(events: List[EventDetails], calendar_id: str):
    """
    Add events to the specified Google Calendar using batch requests.
    """
    service = CalendarService.get_instance()

    if not events:
        print("No events to add")
        return

    print(f"Adding {len(events)} events to Google Calendar...")

    batch_size = 50

    for i in range(0, len(events), batch_size):
        batch = service.new_batch_http_request()
        batch_events = events[i : i + batch_size]

        for event_details in batch_events:
            event = {
                "summary": event_details.summary,
                "description": event_details.description,
                "start": {
                    "dateTime": event_details.start.isoformat(),
                    "timeZone": event_details.timeZone,
                },
                "end": {
                    "dateTime": event_details.end.isoformat(),
                    "timeZone": event_details.timeZone,
                },
                "location": event_details.location,
                "colorId": event_details.color_id,
            }
            batch.add(service.events().insert(calendarId=calendar_id, body=event))

        batch.execute()

    print("Events added!")
