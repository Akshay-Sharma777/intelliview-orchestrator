"""Google Calendar availability integration."""

import logging
from datetime import datetime
from pathlib import Path

from config import get_settings

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Read-only Google Calendar availability service."""

    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

    def __init__(self):
        self.settings = get_settings()

    def is_available(
        self,
        interviewer_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> bool:
        """
        Check whether an interviewer is available during the requested period.

        Returns True when no conflicting Google Calendar event is found.

        Calendar/API failures are handled gracefully and do not block booking.
        """

        if not self.settings.google_calendar_enabled:
            return True

        try:
            service = self._get_calendar_service()

            if service is None:
                return True

            body = {
                "timeMin": start_time.isoformat(),
                "timeMax": end_time.isoformat(),
                "items": [{"id": interviewer_id}],
            }

            result = service.freebusy().query(body=body).execute()

            busy_slots = (
                result.get("calendars", {}).get(interviewer_id, {}).get("busy", [])
            )

            return not busy_slots

        except Exception:
            logger.exception(
                "Google Calendar availability check failed for interviewer %s",
                interviewer_id,
            )

            # Calendar failures must not crash the booking system.
            return True

    def _get_calendar_service(self):
        """Build an authenticated read-only Google Calendar API client."""

        credentials_file = self.settings.google_calendar_credentials_file

        if not credentials_file:
            logger.warning("Google Calendar credentials are not configured")
            return None

        credentials_path = Path(credentials_file)

        if not credentials_path.exists():
            logger.warning(
                "Google Calendar credentials file does not exist: %s",
                credentials_path,
            )
            return None

        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            token_path = Path(self.settings.google_calendar_token_file)

            credentials = None

            if token_path.exists():
                credentials = Credentials.from_authorized_user_file(
                    str(token_path),
                    self.SCOPES,
                )

            if credentials is None or not credentials.valid:
                if (
                    credentials is not None
                    and credentials.expired
                    and credentials.refresh_token
                ):
                    credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path),
                        self.SCOPES,
                    )
                    credentials = flow.run_local_server(port=0)

                token_path.write_text(
                    credentials.to_json(),
                    encoding="utf-8",
                )

            return build(
                "calendar",
                "v3",
                credentials=credentials,
                cache_discovery=False,
            )

        except Exception:
            logger.exception("Failed to initialize Google Calendar service")
            return None
