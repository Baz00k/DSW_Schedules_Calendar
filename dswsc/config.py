from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True, env_file=".env", env_file_encoding="utf-8")

    group_id: str = Field(alias='GROUP_ID', description='ID of the group to fetch the schedule for', examples=['995'])
    google_calendar_id: str = Field(alias='GOOGLE_CALENDAR_ID', description='ID of the Google Calendar to add events to')
    google_service_account_key: str = Field(alias='GOOGLE_SERVICE_ACCOUNT_KEY', description='Service account key for Google Calendar API')


try:
    settings = Settings()
except ValidationError as e:
    exit(f"Invalid configuration: {e}")
