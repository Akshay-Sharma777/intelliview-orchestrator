"""
Unit tests for TTS functions in workers/ai_client.py
"""

import sys
from unittest.mock import MagicMock, patch
import pytest

from workers.ai_client import speak_text, speak_text_to_file


@pytest.fixture
def mock_pyttsx3():
    """Fixture to mock pyttsx3 engine initialization without requiring package installation."""
    mock_engine = MagicMock()
    mock_module = MagicMock()
    mock_module.init.return_value = mock_engine

    # Inject pyttsx3 into sys.modules so imports/references don't fail
    with patch.dict(sys.modules, {"pyttsx3": mock_module}):
        with patch("workers.ai_client.pyttsx3", mock_module, create=True):
            yield mock_module, mock_engine


class TestSpeakText:
    """Tests for speak_text() function."""

    def test_speak_text_success(self, mock_pyttsx3):
        _, mock_engine = mock_pyttsx3
        with patch("workers.ai_client.HAS_TTS", True):
            result = speak_text("Hello world")

        assert result is True
        mock_engine.say.assert_called_once_with("Hello world")
        mock_engine.runAndWait.assert_called_once()

    def test_speak_text_empty_string(self):
        with patch("workers.ai_client.HAS_TTS", True):
            assert speak_text("") is False
            assert speak_text("   ") is False

    def test_speak_text_none_input(self):
        with patch("workers.ai_client.HAS_TTS", True):
            assert speak_text(None) is False

    def test_speak_text_no_tts_available(self):
        with patch("workers.ai_client.HAS_TTS", False):
            result = speak_text("Hello world")
            assert result is False

    def test_speak_text_exception_handling(self, mock_pyttsx3):
        _, mock_engine = mock_pyttsx3
        mock_engine.runAndWait.side_effect = Exception("TTS Engine Error")

        with patch("workers.ai_client.HAS_TTS", True):
            result = speak_text("Hello world")
            assert result is False


class TestSpeakTextToFile:
    """Tests for speak_text_to_file() function."""

    def test_speak_text_to_file_success(self, mock_pyttsx3):
        _, mock_engine = mock_pyttsx3
        with patch("workers.ai_client.HAS_TTS", True):
            result = speak_text_to_file("Hello world", "output.mp3")

        assert result is True
        mock_engine.save_to_file.assert_called_once_with("Hello world", "output.mp3")
        mock_engine.runAndWait.assert_called_once()

    def test_speak_text_to_file_empty_string(self):
        with patch("workers.ai_client.HAS_TTS", True):
            assert speak_text_to_file("", "output.mp3") is False

    def test_speak_text_to_file_no_tts_available(self):
        with patch("workers.ai_client.HAS_TTS", False):
            result = speak_text_to_file("Hello world", "output.mp3")
            assert result is False

    def test_speak_text_to_file_exception_handling(self, mock_pyttsx3):
        _, mock_engine = mock_pyttsx3
        mock_engine.runAndWait.side_effect = Exception("File Save Error")

        with patch("workers.ai_client.HAS_TTS", True):
            result = speak_text_to_file("Hello world", "output.mp3")
            assert result is False