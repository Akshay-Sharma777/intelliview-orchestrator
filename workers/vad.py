"""Voice Activity Detection (VAD) Engine.

Handles audio frame processing, speech/silence classification,
conservative adaptive noise floor estimation, hysteresis, short pause tolerance,
sustained silence detection, and END_OF_SPEECH event generation.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import math
import os
import struct
import wave
from typing import Any

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    np = None  # type: ignore
    HAS_NUMPY = False

logger = logging.getLogger(__name__)


@dataclass
class VADConfig:
    """Configuration for Voice Activity Detection sensitivity and frame timing."""

    sample_rate: int = 16000
    frame_duration_ms: int = 30  # 480 samples per frame at 16kHz
    energy_threshold_high: float = 0.010  # Onset threshold for speech
    energy_threshold_low: float = 0.004  # Offset threshold for silence
    max_pause_merge_ms: int = 600  # Max intra-speech pause tolerance
    silence_timeout_ms: int = 1200  # Sustained silence trigger for END_OF_SPEECH
    min_speech_duration_ms: int = 150  # Minimum valid speech duration
    adaptation_frames: int = 10  # Max initial frames for baseline noise floor estimation
    min_noise_floor: float = 0.002  # Safety floor to prevent zero-noise floor issues


@dataclass
class VADEvent:
    """Represents a VAD detection event derived strictly from frame/sample timing."""

    event_type: str  # "SPEECH_START", "SPEECH_CONTINUED", "SILENCE", "END_OF_SPEECH"
    timestamp_ms: float  # Audio position timestamp in milliseconds
    speech_duration_ms: float = 0.0
    confidence: float = 1.0


@dataclass
class SpeechSegment:
    """Extracted speech segment representation for downstream speech tasks."""

    start: float
    end: float
    duration: float
    audio_samples: Any | None = None

    def to_dict(self) -> dict[str, float]:
        return {
            "start": round(self.start, 3),
            "end": round(self.end, 3),
            "duration": round(self.duration, 3),
        }


class VoiceActivityDetector:
    """Frame-based Voice Activity Detector operating deterministically on 16 kHz audio samples."""

    def __init__(self, config: VADConfig | None = None):
        self.config = config or VADConfig()
        self.frame_size = int(
            self.config.sample_rate * (self.config.frame_duration_ms / 1000.0)
        )

    @staticmethod
    def _load_samples(
        audio_path: str, target_sr: int = 16000
    ) -> tuple[Any, int]:
        """Load audio samples from a WAV file as normalized float samples in [-1.0, 1.0]."""
        if not os.path.exists(audio_path):
            return (np.array([], dtype=np.float32) if HAS_NUMPY else []), target_sr
        try:
            with wave.open(audio_path, "rb") as wf:
                sr = wf.getframerate()
                n_channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                n_frames = wf.getnframes()
                raw_bytes = wf.readframes(n_frames)

            if sampwidth == 2:
                if HAS_NUMPY:
                    samples = (
                        np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32)
                        / 32768.0
                    )
                else:
                    count = len(raw_bytes) // 2
                    integers = struct.unpack(f"<{count}h", raw_bytes)
                    samples = [val / 32768.0 for val in integers]
            elif sampwidth == 1:
                if HAS_NUMPY:
                    samples = (
                        np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float32)
                        - 128.0
                    ) / 128.0
                else:
                    samples = [(val - 128) / 128.0 for val in raw_bytes]
            else:
                if HAS_NUMPY:
                    samples = (
                        np.frombuffer(raw_bytes, dtype=np.int32).astype(np.float32)
                        / 2147483648.0
                    )
                else:
                    count = len(raw_bytes) // 4
                    integers = struct.unpack(f"<{count}i", raw_bytes)
                    samples = [val / 2147483648.0 for val in integers]

            if n_channels > 1 and len(samples) > 0:
                samples = samples[::n_channels]

            if sr != target_sr and len(samples) > 0:
                if HAS_NUMPY:
                    num_output_samples = int(len(samples) * target_sr / sr)
                    samples = np.interp(
                        np.linspace(
                            0, len(samples), num_output_samples, endpoint=False
                        ),
                        np.arange(len(samples)),
                        samples,
                    ).astype(np.float32)
                else:
                    num_output = int(len(samples) * target_sr / sr)
                    step = len(samples) / float(num_output)
                    resampled = [
                        samples[int(i * step)]
                        for i in range(num_output)
                        if int(i * step) < len(samples)
                    ]
                    samples = resampled
                sr = target_sr

            return samples, sr
        except Exception as exc:
            logger.warning("Failed to load audio samples from %s: %s", audio_path, exc)
            return (np.array([], dtype=np.float32) if HAS_NUMPY else []), target_sr

    def process_frames(self, samples: Any) -> list[VADEvent]:
        """Process float audio samples frame-by-frame and return VAD events.

        All timing is derived strictly from frame index and sample counts.
        RMS is calculated as sqrt(mean(samples ** 2)).
        """
        if samples is None or len(samples) == 0:
            return []

        frame_size = self.frame_size
        frame_duration_ms = self.config.frame_duration_ms

        total_frames = int(math.ceil(len(samples) / float(frame_size)))

        rms_energies: list[float] = []
        for i in range(total_frames):
            if HAS_NUMPY and isinstance(samples, np.ndarray):
                frame = samples[i * frame_size : (i + 1) * frame_size]
                if len(frame) == 0:
                    continue
                rms = float(np.sqrt(np.mean(frame**2)))
            else:
                frame = samples[i * frame_size : (i + 1) * frame_size]
                if not frame:
                    continue
                sum_sq = sum(float(s) * float(s) for s in frame)
                rms = math.sqrt(sum_sq / float(len(frame)))
            rms_energies.append(rms)

        if not rms_energies:
            return []

        # Conservative adaptive noise floor estimation:
        # Evaluate frames below speech threshold (up to adaptation_frames)
        low_energy_initial = [
            e
            for e in rms_energies[: self.config.adaptation_frames]
            if e < self.config.energy_threshold_high
        ]

        if low_energy_initial:
            measured_bg = sum(low_energy_initial) / float(len(low_energy_initial))
            bg_noise = max(
                self.config.min_noise_floor,
                min(measured_bg, self.config.energy_threshold_low),
            )
        else:
            bg_noise = self.config.min_noise_floor

        # Thresholds with hysteresis
        onset_thresh = max(self.config.energy_threshold_high, bg_noise * 2.5)
        offset_thresh = max(self.config.energy_threshold_low, bg_noise * 1.5)

        events: list[VADEvent] = []

        is_speaking = False
        speech_start_ms = 0.0
        current_speech_duration_ms = 0.0
        accumulated_silence_ms = 0.0
        end_of_speech_emitted = False

        for idx, energy in enumerate(rms_energies):
            current_time_ms = idx * frame_duration_ms

            # Confidence is bounded strictly between 0.0 and 1.0
            if energy >= onset_thresh:
                confidence = min(1.0, max(0.0, energy / (onset_thresh * 2.0)))
            else:
                confidence = (
                    min(1.0, max(0.0, 1.0 - (energy / onset_thresh)))
                    if onset_thresh > 0
                    else 1.0
                )

            if not is_speaking:
                if energy >= onset_thresh:
                    is_speaking = True
                    speech_start_ms = current_time_ms
                    accumulated_silence_ms = 0.0
                    end_of_speech_emitted = False
                    events.append(
                        VADEvent(
                            event_type="SPEECH_START",
                            timestamp_ms=current_time_ms,
                            confidence=round(confidence, 3),
                        )
                    )
                else:
                    events.append(
                        VADEvent(
                            event_type="SILENCE",
                            timestamp_ms=current_time_ms,
                            confidence=round(confidence, 3),
                        )
                    )
            else:
                if energy >= offset_thresh:
                    # Speech resumes or continues — cancel pending end-of-speech and reset accumulated silence!
                    is_speaking = True
                    accumulated_silence_ms = 0.0
                    current_speech_duration_ms = current_time_ms - speech_start_ms
                    events.append(
                        VADEvent(
                            event_type="SPEECH_CONTINUED",
                            timestamp_ms=current_time_ms,
                            speech_duration_ms=current_speech_duration_ms,
                            confidence=round(confidence, 3),
                        )
                    )
                else:
                    accumulated_silence_ms += frame_duration_ms

                    # Gaps <= max_pause_merge_ms are intra-speech pauses and do not trigger END_OF_SPEECH
                    if accumulated_silence_ms >= self.config.silence_timeout_ms:
                        if not end_of_speech_emitted:
                            events.append(
                                VADEvent(
                                    event_type="END_OF_SPEECH",
                                    timestamp_ms=current_time_ms,
                                    speech_duration_ms=current_speech_duration_ms,
                                    confidence=round(confidence, 3),
                                )
                            )
                            end_of_speech_emitted = True
                            is_speaking = False
                    else:
                        events.append(
                            VADEvent(
                                event_type="SILENCE",
                                timestamp_ms=current_time_ms,
                                speech_duration_ms=current_speech_duration_ms,
                                confidence=round(confidence, 3),
                            )
                        )

        return events

    def process_audio(self, audio_path: str) -> list[SpeechSegment]:
        """Process an audio file and extract speech segments (compatible with ai_client.py)."""
        samples, sr = self._load_samples(audio_path, self.config.sample_rate)
        if len(samples) == 0:
            return []

        events = self.process_frames(samples)
        segments: list[SpeechSegment] = []

        seg_start: float | None = None
        for ev in events:
            if ev.event_type == "SPEECH_START" and seg_start is None:
                seg_start = ev.timestamp_ms / 1000.0
            elif ev.event_type == "END_OF_SPEECH" and seg_start is not None:
                seg_end = ev.timestamp_ms / 1000.0
                duration = seg_end - seg_start
                if duration >= (self.config.min_speech_duration_ms / 1000.0):
                    start_idx = int(seg_start * sr)
                    end_idx = min(len(samples), int(seg_end * sr))
                    seg_samples = samples[start_idx:end_idx]
                    segments.append(
                        SpeechSegment(
                            start=seg_start,
                            end=seg_end,
                            duration=duration,
                            audio_samples=seg_samples,
                        )
                    )
                seg_start = None

        if seg_start is not None:
            seg_end = len(samples) / float(sr)
            duration = seg_end - seg_start
            if duration >= (self.config.min_speech_duration_ms / 1000.0):
                start_idx = int(seg_start * sr)
                end_idx = len(samples)
                seg_samples = samples[start_idx:end_idx]
                segments.append(
                    SpeechSegment(
                        start=seg_start,
                        end=seg_end,
                        duration=duration,
                        audio_samples=seg_samples,
                    )
                )

        return segments
