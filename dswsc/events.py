from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
from icalendar import Calendar

from .config import settings


class EventDetails(BaseModel):
    summary: str
    start: datetime
    end: datetime
    timeZone: str = settings.timezone
    group_name: str = Field(alias='Plan dla toku')
    date: str = Field(alias='Data zajęć')
    start_time: str = Field(alias='Czas od')
    end_time: str = Field(alias='Czas do')
    school_hours: str = Field(alias='Liczba godzin')
    subject: str = Field(alias='Przedmiot')
    form: str | None = Field(alias='Forma zajęć', default=None)
    type_of_class: str | None = Field(alias='Grupy', default=None)
    location: str = Field(alias='Sala', default='Zdalnie') # If location is not provided, assume it's online
    instructor: str | None = Field(alias='Prowadzący', default=None)
    assessment: str | None = Field(alias='Forma zaliczenia', default=None)
    remarks: str | None = Field(alias='Uwagi', default=None)

    @property
    def description(self) -> str:
        """
        Generate a description for the event.
        """
        description_fields = [
            ('Forma zajęć', self.type_of_class),
            ('Prowadzący', self.instructor),
            ('Liczba godzin lekcyjnych', self.school_hours),
            ('Uwagi', self.remarks),
        ]

        description = f'{self.subject}\n\n'

        for key, value in description_fields:
            if value:
                description += f'{key}: {value}\n'

        return description

    @property
    def color_id(self) -> str | None:
        """
        Determine the colorId based on the type of class and location.
        """
        if self.type_of_class is None:
            return None # TODO: Check the exact case when type_of_class is None

        if self.type_of_class.lower().startswith('cw'):
            if self.location == 'Zdalnie':
                return '5'  # Ćwiczenia online, "banana" color
            else:
                return '2'  # Ćwiczenia stacjonarne, "sage" color
        elif self.type_of_class.lower().startswith('wyk'):
            if self.location == 'Zdalnie':
                return '8'  # Wykład online, "graphite" color
            else:
                return '1'  # Wykład stacjonarny, "lavender" color

        return None # Default calendar color

    @classmethod
    def from_ical_event(cls, component) -> 'EventDetails':
        """
        Parse the iCal event component to extract and format event details.
        """
        summary = str(component.get('summary'))
        start = component.get('dtstart').dt
        end = component.get('dtend').dt

        lines = str(component.get('description')).strip().split('\n')
        event_details = {}

        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)

                if not value or value.isspace():
                    continue

                event_details[key.strip()] = value.strip()

        return cls(
            summary=summary,
            start=start,
            end=end,
            **event_details
        )


def parse_ical_to_events(schedule_ical: str) -> List[EventDetails]:
    """
    Parse iCal data to extract events.
    """
    cal = Calendar.from_ical(schedule_ical)
    events = []

    for component in cal.walk():
        if component.name == "VEVENT":
            event_details = EventDetails.from_ical_event(component)
            events.append(event_details)

    return events
