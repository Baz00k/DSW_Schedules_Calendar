import os
import json
from typing import List
from hashlib import md5

from .config import settings
from .events import EventDetails

def _get_cache_file_path(group_id: str) -> str:
    return os.path.join(settings.cache_dir, settings.cache_file_template.format(group_id=group_id))


def events_to_json(events: List[EventDetails]) -> str:
    return json.dumps([event.model_dump(mode="json", warnings="warn") for event in events], sort_keys=True)


def string_to_hash(string: str) -> str:
    return md5(string.encode()).hexdigest()


def events_to_hash(events: List[EventDetails]) -> str:
    return string_to_hash(events_to_json(events))


def load_events_cache(group_id: str) -> str | None:
    cache_file = _get_cache_file_path(group_id)
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return f.read()
        
    return None


def save_events_cache(group_id: str, events: List[EventDetails]) -> None:
    if not os.path.exists(settings.cache_dir):
        os.makedirs(settings.cache_dir)

    cache_file = _get_cache_file_path(group_id)

    with open(cache_file, 'w') as f:
        f.write(events_to_hash(events))

