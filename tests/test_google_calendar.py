from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from orchestrator.google_calendar import GoogleCalendarService


def test_calendar_disabled_allows_booking():
    service = GoogleCalendarService()

    service.settings.google_calendar_enabled = False

    result = service.is_available(
        interviewer_id="interviewer@example.com",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=timezone.utc),
    )

    assert result is True


def test_free_calendar_allows_booking():
    service = GoogleCalendarService()

    service.settings.google_calendar_enabled = True

    mock_google_service = MagicMock()

    mock_google_service.freebusy.return_value.query.return_value.execute.return_value = {
        "calendars": {"interviewer@example.com": {"busy": []}}
    }

    with patch.object(
        service,
        "_get_calendar_service",
        return_value=mock_google_service,
    ):
        result = service.is_available(
            interviewer_id="interviewer@example.com",
            start_time=datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 9, 1, 11, 0, tzinfo=timezone.utc),
        )

    assert result is True


def test_busy_calendar_rejects_booking():
    service = GoogleCalendarService()

    service.settings.google_calendar_enabled = True

    mock_google_service = MagicMock()

    mock_google_service.freebusy.return_value.query.return_value.execute.return_value = {
        "calendars": {
            "interviewer@example.com": {
                "busy": [
                    {
                        "start": "2026-09-01T10:30:00Z",
                        "end": "2026-09-01T11:30:00Z",
                    }
                ]
            }
        }
    }

    with patch.object(
        service,
        "_get_calendar_service",
        return_value=mock_google_service,
    ):
        result = service.is_available(
            interviewer_id="interviewer@example.com",
            start_time=datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 9, 1, 11, 0, tzinfo=timezone.utc),
        )

    assert result is False


def test_calendar_failure_allows_booking():
    service = GoogleCalendarService()

    service.settings.google_calendar_enabled = True

    with patch.object(
        service,
        "_get_calendar_service",
        side_effect=Exception("Google API unavailable"),
    ):
        result = service.is_available(
            interviewer_id="interviewer@example.com",
            start_time=datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 9, 1, 11, 0, tzinfo=timezone.utc),
        )

    assert result is True
