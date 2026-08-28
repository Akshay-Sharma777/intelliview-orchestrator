"use client";

import React, { useEffect, useMemo, useState } from "react";
import { RecordedVideoPlayer } from "@/components/review/RecordedVideoPlayer";
import { swrFetcher } from "@/lib/fetcher";

/**
 * Fallback payload used when no session id is provided, the session cannot be
 * loaded, or the loaded session has no attached recording file. This keeps the
 * review page rendering the player UI cleanly on direct navigation to /review
 * instead of crashing or showing a dead-end "No valid session selected" screen.
 */
const FALLBACK_SESSION = {
  id: "sample-recording",
  status: "Sample",
  video_url:
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
  transcripts: [
    { start: 0, end: 4, text: "Welcome to the candidate interview technical review session." },
    { start: 5, end: 9, text: "Today we will discuss distributed system architecture design." },
    { start: 10, end: 16, text: "Can you explain how you handle cache invalidation in microservices?" },
    { start: 17, end: 24, text: "We use write-through caching combined with pub/sub event channels." },
    { start: 25, end: 32, text: "That prevents stale reads across multiple instance nodes effectively." },
    { start: 33, end: 40, text: "Notice how captions automatically stay synchronized with playback time." },
    { start: 41, end: 50, text: "You can click any timestamp or use seekTo to jump directly." }
  ]
};

/** Best-effort extraction of a playable recording URL from a session payload. */
function getRecordingUrl(session) {
  if (!session) return null;
  const analysis = session.video_analysis || {};
  return (
    session.video_url ||
    session.media_path ||
    session.recording_url ||
    analysis.video_url ||
    analysis.media_path ||
    analysis.recording_url ||
    analysis.file_path ||
    null
  );
}

/** Best-effort extraction of caption/subtitle cues from a session payload. */
function getCaptions(session) {
  if (!session) return null;
  const analysis = session.video_analysis || {};
  const found =
    session.transcripts || session.captions || analysis.transcripts || analysis.captions;
  return Array.isArray(found) && found.length > 0 ? found : null;
}

export default function ReviewPage({ searchParams }) {
  const sessionId = searchParams?.id;
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(() => Boolean(searchParams?.id));
  const [notice, setNotice] = useState(null);

  useEffect(() => {
    let cancelled = false;

    if (!sessionId) {
      setSession(null);
      setLoading(false);
      setNotice(
        "No session id provided - showing a sample recording. Pass ?id=<session_id> to review a real session."
      );
      return () => {
        cancelled = true;
      };
    }

    async function loadSessionData() {
      try {
        setLoading(true);
        setNotice(null);
        const data = await swrFetcher(`/session-status/${sessionId}`);
        if (cancelled) return;
        setSession(data);
        if (!data || !getRecordingUrl(data)) {
          setNotice(
            `Session "${sessionId}" has no attached recording - showing a sample recording.`
          );
        }
      } catch (err) {
        if (!cancelled) {
          setSession(null);
          setNotice(
            `Could not load session "${sessionId}" (${err.message}) - showing a sample recording.`
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadSessionData();
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  // Prefer the real session whenever it exposes a recording URL; otherwise fall
  // back to the sample payload so the player always renders.
  const playbackSession = useMemo(() => {
    if (session && getRecordingUrl(session)) {
      return session;
    }
    return FALLBACK_SESSION;
  }, [session]);

  const videoUrl = getRecordingUrl(playbackSession);
  const captions = useMemo(() => getCaptions(playbackSession) || [], [playbackSession]);

  if (loading) {
    return (
      <main className="min-h-screen bg-zinc-950 p-6 flex items-center justify-center text-zinc-300">
        Loading interview recording...
      </main>
    );
  }

  const displayId =
    session?.session_id || session?.id || sessionId || FALLBACK_SESSION.id;
  const displayStatus = session?.status || "Sample";

  return (
    <main className="min-h-screen bg-zinc-950 p-6 sm:p-10 space-y-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center border-b border-zinc-800 pb-4">
        <h1 className="text-2xl font-bold text-white">
          Session Review #{displayId}
        </h1>
        <span className="px-3 py-1 rounded-full text-xs bg-zinc-800 text-emerald-400">
          {displayStatus}
        </span>
      </div>

      {notice && (
        <div
          data-testid="review-fallback-notice"
          className="flex items-start gap-2.5 px-4 py-3 rounded-lg bg-amber-500/10 border border-amber-500/40 text-amber-300 text-sm"
        >
          <span className="mt-0.5 shrink-0" aria-hidden="true">
            Info
          </span>
          <span>{notice}</span>
        </div>
      )}

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden p-4">
        <RecordedVideoPlayer
          key={videoUrl}
          videoUrl={videoUrl}
          captions={captions}
        />
      </div>
    </main>
  );
}