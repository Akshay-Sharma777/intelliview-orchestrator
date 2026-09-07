"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import useSWR from "swr";
import {
  Video,
  VideoOff,
  Mic,
  MicOff,
  Phone,
  PhoneOff,
  Pause,
  Play,
  AlertTriangle,
  Activity,
  Radio,
  Volume2,
} from "lucide-react";
import Card from "@/components/Card";
import { Badge } from "@/components/Badge";
import { Skeleton, ErrorState, EmptyState } from "@/components/States";
import VideoPlayer from "@/components/VideoPlayer";
import { endpoints } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { toast } from "@/lib/toast";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useMomentTracking } from "@/hooks/useMomentTracking";
import RiskTimeline from "@/components/RiskTimeline";
import { cn, riskColor } from "@/lib/utils";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { useAudioPlayback } from "@/hooks/useAudioPlayback";
import AudioIndicator from "@/components/AudioIndicator";

// Persisted so a refresh doesn't silently drop a paused interview back to
// the "start a new one" screen. Only UI state is restored here (not the
// camera/mic stream, which the browser can't hand back without a fresh
// getUserMedia call) — risk-scoring is untouched by any of this.
const SESSION_STORAGE_KEY = "iv_interview_session_state";

function readPersistedSession() {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(SESSION_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || !parsed.isLive) return null;
    return parsed;
  } catch {
    return null;
  }
}

export default function InterviewPage() {
  const token = useAppStore((s) => s.token);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const audioCtxRef = useRef(null);
  const animFrameRef = useRef(null);

  const persisted = useRef(typeof window !== "undefined" ? readPersistedSession() : null);

  const [videoEnabled, setVideoEnabled] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [isPaused, setIsPaused] = useState(() => persisted.current?.isPaused ?? false);
  const [isLive, setIsLive] = useState(() => persisted.current?.isLive ?? false);
  const [activeSession, setActiveSession] = useState(() => persisted.current?.activeSession ?? null);
  const [riskScore, setRiskScore] = useState(0);
  const [feedback, setFeedback] = useState([]);
  const [audioLevels, setAudioLevels] = useState(new Array(32).fill(0));
  const [candidate, setCandidate] = useState(() => persisted.current?.candidate ?? "");
  const [starting, setStarting] = useState(false);

  // 💡 Task B3: State loop context tracker definition for active question data strings
  const [currentQuestion, setCurrentQuestion] = useState({
    text: "Welcome to your AI Interview. Please review the instructions and answer clearly.",
    audioUrl: ""
  });

  // 🔊 Task B3: Hook evaluation lifecycle deployment logic sequence
  const { isPlaying } = useAudioPlayback(currentQuestion?.audioUrl, () => {
    console.log("Question audio playback complete. Advancing turn machine states.");
    // If a transition trigger parameter exists within parent props, invoke it here
  });

  // Keep the persisted copy in sync while an interview is live; clear it
  // once the interview ends so a later refresh doesn't resurrect it.
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!isLive) {
      window.localStorage.removeItem(SESSION_STORAGE_KEY);
      return;
    }
    window.localStorage.setItem(
      SESSION_STORAGE_KEY,
      JSON.stringify({ isLive, isPaused, activeSession, candidate })
    );
  }, [isLive, isPaused, activeSession, candidate]);

  const {
    moments,
    isTracking,
    startTracking,
    stopTracking,
    trackEvent,
  } = useMomentTracking(activeSession);

  const { connected } = useWebSocket({
    path: "/monitoring/ws/metrics",
    enabled: !!token && isLive,
    onMessage: (data) => {
      if (data?.risk_score != null) setRiskScore(data.risk_score);
      if (data?.feedback) setFeedback((prev) => [...prev, data.feedback].slice(-20));
    },
  });

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: "user" },
        audio: true,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setVideoEnabled(true);

      audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioCtxRef.current.createMediaStreamSource(stream);
      const analyzer = audioCtxRef.current.createAnalyser();
      analyzer.fftSize = 64;
      source.connect(analyzer);

      const dataArray = new Uint8Array(analyzer.frequencyBinCount);
      const draw = () => {
        analyzer.getByteFrequencyData(dataArray);
        setAudioLevels(Array.from(dataArray));
        animFrameRef.current = requestAnimationFrame(draw);
      };
      draw();
    } catch (err) {
      toast.error("Camera access denied", err instanceof Error ? err.message : String(err));
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (audioCtxRef.current) {
      audioCtxRef.current.close();
      audioCtxRef.current = null;
    }
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    if (videoRef.current) videoRef.current.srcObject = null;
    setVideoEnabled(false);
    setAudioLevels(new Array(32).fill(0));
  }, []);

  useEffect(() => {
    return () => stopCamera();
  }, [stopCamera]);

  const toggleAudio = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getAudioTracks().forEach((t) => {
        t.enabled = !audioEnabled;
      });
    }
    setAudioEnabled((v) => !v);
  }, [audioEnabled]);

  const handleStart = async () => {
    if (!candidate.trim()) {
      toast.warn("Enter a candidate ID", "Required to start the interview");
      return;
    }
    setStarting(true);
    try {
      const r = await endpoints.startInterview({ candidate_id: candidate.trim(), priority: "high" });
      setActiveSession(r.session_id);
      setIsLive(true);
      await startCamera();
      startTracking();
      trackEvent("session_start", { candidate_id: candidate.trim() });
      toast.success("Interview started", `Session ${r.session_id}`);
    } catch (err) {
      toast.error("Failed to start", err instanceof Error ? err.message : String(err));
    } finally {
      setStarting(false);
    }
  };

  const handleStop = () => {
    trackEvent("session_end", { duration: moments.length * 1000 });
    stopTracking();
    stopCamera();
    setIsLive(false);
    setActiveSession(null);
    setIsPaused(false);
    setRiskScore(0);
    setFeedback([]);
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(SESSION_STORAGE_KEY);
    }
    toast.info("Interview ended");
  };

  const handlePause = () => {
    setIsPaused((v) => !v);
    if (streamRef.current) {
      streamRef.current.getVideoTracks().forEach((t) => {
        t.enabled = isPaused;
      });
    }
    toast.info(isPaused ? "Resumed" : "Paused");
  };

  const maxLevel = Math.max(...audioLevels, 1);

  return (
    <ErrorBoundary>
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-xl font-semibold text-zinc-50 sm:text-2xl">Live Interview</h1>
            <p className="text-sm text-muted">Real-time video feed with AI-powered analysis.</p>
          </div>
          {isLive && (
            <div className="flex items-center gap-2">
              <Radio size={12} className="text-emerald-400 animate-pulse" />
              <span className="text-xs text-emerald-400">LIVE</span>
              {isPaused && (
                <Badge variant="warn" className="ml-1">
                  Paused
                </Badge>
              )}
            </div>
          )}
        </div>

        {isLive && isPaused && (
          <div className="flex items-center gap-2 rounded-md border border-amber-500/40 bg-amber-500/10 px-3 py-2.5 text-sm text-amber-300 sm:gap-3">
            <Pause size={16} className="shrink-0" />
            <span className="font-medium">Interview Paused</span>
          </div>
        )}

        {/* 🔊 Task B3: Visual Audio Playback State Component Layout Render */}
        <Card className="p-6 bg-zinc-900 border-zinc-800">
          <div className="mb-4">
            <AudioIndicator isPlaying={isPlaying} />
            <h3 className="text-xl font-semibold text-zinc-100 mt-3">
              {currentQuestion?.text}
            </h3>
          </div>
        </Card>
      </div>
    </ErrorBoundary>
  );
}
