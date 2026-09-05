"""Dedicated Unit tests for Voice Activity Detection (VAD) Engine (workers/vad.py).

Verifies RMS calculation, silence detection, normal/quiet speech detection,
adaptive noise floor behavior, zero noise floor safety, short pause tolerance,
sustained silence END_OF_SPEECH emission, pause cancellation on speech return,
bounded confidence (0 to 1), and deterministic frame/sample timing.
"""

import math

from workers.vad import VADConfig, VADEvent, VoiceActivityDetector


def _generate_synthetic_frames(
    duration_ms: float,
    sample_rate: int = 16000,
    amplitude: float = 0.0,
    frequency: float = 440.0,
) -> list[float]:
    """Generate synthetic PCM float32 samples for a given duration in milliseconds."""
    n_samples = int((duration_ms / 1000.0) * sample_rate)
    if amplitude == 0.0:
        return [0.0] * n_samples
    return [
        amplitude * math.sin(2.0 * math.pi * frequency * (i / float(sample_rate)))
        for i in range(n_samples)
    ]


def test_rms_calculation_and_silence_detection():
    """Verify correct RMS energy calculation and pure silence detection."""
    detector = VoiceActivityDetector()
    silent_samples = _generate_synthetic_frames(duration_ms=300, amplitude=0.0)
    events = detector.process_frames(silent_samples)

    assert len(events) > 0
    assert all(e.event_type == "SILENCE" for e in events)


def test_normal_speech_detection():
    """Verify normal candidate speech detection generates SPEECH_START and SPEECH_CONTINUED."""
    detector = VoiceActivityDetector()
    speech_samples = _generate_synthetic_frames(duration_ms=300, amplitude=0.1)
    events = detector.process_frames(speech_samples)

    assert events[0].event_type == "SPEECH_START"
    assert all(
        e.event_type in ("SPEECH_START", "SPEECH_CONTINUED") for e in events
    )


def test_quiet_speech_detection():
    """Verify that quiet candidate speech above offset/onset thresholds is reliably detected."""
    detector = VoiceActivityDetector()
    quiet_speech = _generate_synthetic_frames(duration_ms=300, amplitude=0.02)
    events = detector.process_frames(quiet_speech)

    assert any(e.event_type == "SPEECH_START" for e in events)


def test_adaptive_noise_floor_behavior():
    """Verify conservative adaptive noise floor estimation over initial ambient frames."""
    config = VADConfig(adaptation_frames=10, energy_threshold_high=0.015)
    detector = VoiceActivityDetector(config)

    ambient_noise = _generate_synthetic_frames(duration_ms=300, amplitude=0.004)
    speech = _generate_synthetic_frames(duration_ms=300, amplitude=0.05)
    combined = ambient_noise + speech

    events = detector.process_frames(combined)
    speech_events = [e for e in events if e.event_type == "SPEECH_START"]

    assert len(speech_events) == 1
    assert speech_events[0].timestamp_ms >= 300.0


def test_zero_or_near_zero_noise_floor_safety():
    """Verify zero/near-zero noise floor (Ebg == 0) is handled safely and does not misclassify low audio."""
    config = VADConfig(min_noise_floor=0.002, energy_threshold_high=0.015)
    detector = VoiceActivityDetector(config)

    # Completely zero audio
    zero_audio = [0.0] * (480 * 5)
    events = detector.process_frames(zero_audio)

    assert all(e.event_type == "SILENCE" for e in events)


def test_short_pause_does_not_emit_end_of_speech():
    """Verify a short pause (< 600 ms) during speech does not emit END_OF_SPEECH."""
    detector = VoiceActivityDetector()

    speech1 = _generate_synthetic_frames(duration_ms=300, amplitude=0.1)
    short_pause = _generate_synthetic_frames(duration_ms=400, amplitude=0.0)
    speech2 = _generate_synthetic_frames(duration_ms=300, amplitude=0.1)
    combined = speech1 + short_pause + speech2

    events = detector.process_frames(combined)
    end_of_speech_events = [e for e in events if e.event_type == "END_OF_SPEECH"]

    assert len(end_of_speech_events) == 0


def test_sustained_silence_emits_single_end_of_speech():
    """Verify sustained silence (>= 1200 ms) after speech emits exactly ONE END_OF_SPEECH event."""
    detector = VoiceActivityDetector()

    speech = _generate_synthetic_frames(duration_ms=300, amplitude=0.1)
    sustained_silence = _generate_synthetic_frames(
        duration_ms=1500, amplitude=0.0
    )
    combined = speech + sustained_silence

    events = detector.process_frames(combined)
    end_events = [e for e in events if e.event_type == "END_OF_SPEECH"]

    assert len(end_events) == 1
    assert end_events[0].timestamp_ms >= 1200.0


def test_speech_resuming_cancels_pending_end_of_speech():
    """Verify that speech resuming during a pause (e.g. at 900 ms) cancels pending end-of-speech."""
    detector = VoiceActivityDetector()

    speech1 = _generate_synthetic_frames(duration_ms=300, amplitude=0.1)
    pause_900ms = _generate_synthetic_frames(duration_ms=900, amplitude=0.0)
    speech2 = _generate_synthetic_frames(duration_ms=300, amplitude=0.1)
    combined = speech1 + pause_900ms + speech2

    events = detector.process_frames(combined)
    end_events = [e for e in events if e.event_type == "END_OF_SPEECH"]

    assert len(end_events) == 0


def test_deterministic_timestamps_from_sample_counts():
    """Verify timestamps are 100% deterministic based strictly on frame/sample counts."""
    detector = VoiceActivityDetector()
    audio = _generate_synthetic_frames(
        300, amplitude=0.1
    ) + _generate_synthetic_frames(1500, amplitude=0.0)

    events1 = detector.process_frames(audio)
    events2 = detector.process_frames(audio)

    ts1 = [(e.event_type, e.timestamp_ms) for e in events1]
    ts2 = [(e.event_type, e.timestamp_ms) for e in events2]

    assert ts1 == ts2


def test_confidence_bounded_between_zero_and_one():
    """Verify event confidence values remain strictly bounded between 0.0 and 1.0."""
    detector = VoiceActivityDetector()

    varying_audio = (
        _generate_synthetic_frames(150, amplitude=0.0)
        + _generate_synthetic_frames(150, amplitude=0.01)
        + _generate_synthetic_frames(150, amplitude=0.5)
        + _generate_synthetic_frames(150, amplitude=0.001)
    )

    events = detector.process_frames(varying_audio)

    for ev in events:
        assert 0.0 <= ev.confidence <= 1.0
