import pytest

from workers.tts_engine import synthesize_speech


def test_synthesize_speech_returns_audio_bytes():
    audio = synthesize_speech("Tell me about your experience with Python.")

    assert isinstance(audio, bytes)
    assert len(audio) > 0


def test_synthesize_speech_rejects_empty_text():
    with pytest.raises(ValueError, match=r"Text must not be empty\."):
        synthesize_speech("")
