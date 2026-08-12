"use client";

import { useState, useMemo } from "react";
import useSWR from "swr";
import { UserCircle } from "lucide-react";

import Card from "@/components/Card";
import StatsCards from "@/components/StatsCards";
import { StatusBadge, Badge } from "@/components/Badge";
import { Skeleton, ErrorState, EmptyState } from "@/components/States";
import { SearchInput, Table, Thead, Tbody, Tr, Th, Td } from "@/components/ui";
import Pipeline from "@/components/Pipeline";

import {
  formatDate,
  riskColor,
  cn,
} from "@/lib/utils";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ErrorBoundary } from "@/components/ErrorBoundary";

function useCandidateData() {
  const completed = useSWR("/completed-sessions?limit=100", {
    refreshInterval: 10000,
  });

  const failed = useSWR("/failed-sessions?limit=100", {
    refreshInterval: 10000,
  });

  const active = useSWR("/active-sessions", {
    refreshInterval: 5000,
  });

  const registered = useSWR("/candidates?limit=100", {
    refreshInterval: 10000,
  });

  const candidates = useMemo(() => {
    const map = new Map();

    // Add all registered candidates first.
    // candidate_id remains the internal unique identifier,
    // while name is used for display.
    for (const candidate of registered.data?.candidates ?? []) {
      map.set(candidate.candidate_id, {
        ...candidate,
        total_sessions: candidate.total_interviews ?? 0,
        completed_sessions: 0,
        failed_sessions: 0,
        active_sessions: 0,
        risk_scores: [],
        sessions: [],
      });
    }

    const allSessions = [
      ...(completed.data?.sessions ?? []),
      ...(failed.data?.sessions ?? []),
      ...(active.data?.sessions ?? []),
    ];

    // Merge session information into registered candidates.
    for (const s of allSessions) {
      const id = s.candidate_id || "unknown";

      if (!map.has(id)) {
        map.set(id, {
          candidate_id: id,
          name: null,
          total_sessions: 0,
          completed_sessions: 0,
          failed_sessions: 0,
          active_sessions: 0,
          risk_scores: [],
          sessions: [],
        });
      }

      const c = map.get(id);

      c.total_sessions += 1;
      c.sessions.push(s);

      if (s.status === "COMPLETED") {
        c.completed_sessions += 1;
      } else if (
        s.status === "FAILED" ||
        s.status === "TIMEOUT"
      ) {
        c.failed_sessions += 1;
      } else {
        c.active_sessions += 1;
      }

      if (s.risk_score != null) {
        c.risk_scores.push(s.risk_score);
      }
    }

    return Array.from(map.values())
      .map((c) => ({
        ...c,
        avg_risk_score:
          c.risk_scores.length > 0
            ? c.risk_scores.reduce((a, b) => a + b, 0) /
              c.risk_scores.length
            : null,

        latest_session: c.sessions.sort(
          (a, b) =>
            new Date(b.updated_at || 0) -
            new Date(a.updated_at || 0)
        )[0],
      }))
      .sort((a, b) => b.total_sessions - a.total_sessions);
  }, [
    completed.data,
    failed.data,
    active.data,
    registered.data,
  ]);

  return {
    candidates,

    isLoading:
      registered.isLoading &&
      completed.isLoading &&
      failed.isLoading,

    error:
      registered.error ||
      completed.error ||
      failed.error,

    mutate: () => {
      registered.mutate();
      completed.mutate();
      failed.mutate();
      active.mutate();
    },
  };
}

export default function CandidatesPage() {
  const {
    candidates,
    isLoading,
    error,
    mutate,
  } = useCandidateData();

  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState(null);

  // Search by candidate name OR candidate ID.
  const filtered = useMemo(() => {
    if (!search.trim()) {
      return candidates;
    }

    const q = search.toLowerCase();

    return candidates.filter(
      (c) =>
        (c.name || "").toLowerCase().includes(q) ||
        c.candidate_id.toLowerCase().includes(q)
    );
  }, [candidates, search]);

  const selected = candidates.find(
    (c) => c.candidate_id === selectedId
  );

  const statusData = useMemo(() => {
    if (!selected) {
      return [];
    }

    const counts = {};

    for (const s of selected.sessions) {
      counts[s.status] = (counts[s.status] || 0) + 1;
    }

    return Object.entries(counts).map(
      ([status, count]) => ({
        status,
        count,
      })
    );
  }, [selected]);

  return (
    <ErrorBoundary>
      <div className="space-y-6 animate-fade-in">

        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-zinc-50">
              Candidates
            </h1>

            <p className="text-sm text-muted">
              Candidate profiles, interview history, and
              performance analytics.
            </p>
          </div>

          <div className="text-xs text-muted">
            {candidates.length} candidates
          </div>
        </div>

        {/* Statistics */}
        <StatsCards
          data={{
            totalCandidates: candidates.length,

            pendingReview: candidates.reduce(
              (a, c) => a + c.active_sessions,
              0
            ),

            completed: candidates.reduce(
              (a, c) => a + c.completed_sessions,
              0
            ),

            activeNow: candidates.filter(
              (c) => c.active_sessions > 0
            ).length,
          }}
        />

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">

          {/* Candidate List */}
          <div className="lg:col-span-1">
            <Card
              title="Candidate List"
              description={`${filtered.length} candidates`}
              action={
                <SearchInput
                  value={search}
                  onChange={setSearch}
                  placeholder="Search candidates..."
                  className="w-48"
                />
              }
            >
              {error ? (
                <ErrorState
                  error={error}
                  onRetry={mutate}
                />
              ) : isLoading ? (
                <Skeleton className="h-48 w-full" />
              ) : filtered.length === 0 ? (
                <EmptyState
                  title="No candidates"
                  description="Candidate data will appear after candidates are registered."
                />
              ) : (
                <div className="max-h-[500px] space-y-1 overflow-y-auto">
                  {filtered.map((c) => (
                    <button
                      key={c.candidate_id}
                      onClick={() =>
                        setSelectedId(c.candidate_id)
                      }
                      className={cn(
                        "flex w-full items-center justify-between rounded-md px-3 py-2.5 text-left text-sm transition-colors",

                        selectedId === c.candidate_id
                          ? "bg-accent/15 text-accent-light"
                          : "text-zinc-300 hover:bg-bg-card"
                      )}
                    >
                      <div className="min-w-0">

                        {/* REAL CANDIDATE NAME */}
                        <div className="truncate text-sm font-medium text-zinc-200">
                          {c.name || c.candidate_id}
                        </div>

                        {/* Candidate ID shown below the name */}
                        <div className="truncate font-mono text-[10px] text-muted">
                          {c.candidate_id}
                        </div>

                        <div className="text-[10px] text-muted">
                          {c.total_sessions}{" "}
                          session
                          {c.total_sessions !== 1
                            ? "s"
                            : ""}
                        </div>
                      </div>

                      {c.avg_risk_score != null && (
                        <Badge
                          variant={riskColor(
                            c.avg_risk_score
                          )}
                        >
                          {c.avg_risk_score.toFixed(2)}
                        </Badge>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </Card>
          </div>

          {/* Candidate Details */}
          <div className="lg:col-span-2">

            {!selected ? (
              <Card>
                <div className="flex flex-col items-center justify-center py-16 text-center">
                  <UserCircle
                    size={48}
                    className="mb-3 text-muted opacity-30"
                  />

                  <p className="text-sm text-zinc-300">
                    Select a candidate to view details
                  </p>

                  <p className="mt-1 text-xs text-muted">
                    Click on a candidate from the list to see
                    their profile
                  </p>
                </div>
              </Card>
            ) : (
              <div className="space-y-4">

                {/* Candidate Profile */}
                <Card
                  title={
                    selected.name ||
                    selected.candidate_id
                  }
                  description={
                    selected.name
                      ? selected.candidate_id
                      : "Candidate profile and performance"
                  }
                >
                  <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">

                    {/* Total */}
                    <div className="rounded-md border border-border bg-bg-card px-3 py-2.5">
                      <div className="text-[10px] uppercase tracking-wide text-muted">
                        Total
                      </div>

                      <div className="mt-1 text-lg font-semibold text-zinc-50">
                        {selected.total_sessions}
                      </div>
                    </div>

                    {/* Completed */}
                    <div className="rounded-md border border-border bg-bg-card px-3 py-2.5">
                      <div className="text-[10px] uppercase tracking-wide text-muted">
                        Completed
                      </div>

                      <div className="mt-1 text-lg font-semibold text-emerald-400">
                        {selected.completed_sessions}
                      </div>
                    </div>

                    {/* Failed */}
                    <div className="rounded-md border border-border bg-bg-card px-3 py-2.5">
                      <div className="text-[10px] uppercase tracking-wide text-muted">
                        Failed
                      </div>

                      <div className="mt-1 text-lg font-semibold text-rose-400">
                        {selected.failed_sessions}
                      </div>
                    </div>

                    {/* Average Risk */}
                    <div className="rounded-md border border-border bg-bg-card px-3 py-2.5">
                      <div className="text-[10px] uppercase tracking-wide text-muted">
                        Avg Risk
                      </div>

                      <div className="mt-1 text-lg font-semibold text-zinc-50">
                        {selected.avg_risk_score != null
                          ? selected.avg_risk_score.toFixed(3)
                          : "—"}
                      </div>
                    </div>

                  </div>
                </Card>

                {/* Session Status Distribution */}
                {statusData.length > 0 && (
                  <Card title="Session Status Distribution">
                    <ResponsiveContainer
                      width="100%"
                      height={200}
                    >
                      <BarChart data={statusData}>
                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="#27272a"
                        />

                        <XAxis
                          dataKey="status"
                          stroke="#71717a"
                          fontSize={11}
                        />

                        <YAxis
                          stroke="#71717a"
                          fontSize={11}
                        />

                        <Tooltip
                          contentStyle={{
                            background: "#12121a",
                            border: "1px solid #27272a",
                            borderRadius: 8,
                          }}
                        />

                        <Bar
                          dataKey="count"
                          fill="#6366f1"
                          radius={[4, 4, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </Card>
                )}

                {/* Interview History */}
                <Card
                  title="Interview History"
                  description="All sessions for this candidate"
                >
                  <Table>
                    <Thead>
                      <Tr>
                        <Th>Session</Th>
                        <Th>Pipeline</Th>
                        <Th>Status</Th>
                        <Th>Risk</Th>
                        <Th>Worker</Th>
                        <Th>Updated</Th>
                      </Tr>
                    </Thead>

                    <Tbody>
                      {selected.sessions
                        .sort(
                          (a, b) =>
                            new Date(
                              b.updated_at || 0
                            ) -
                            new Date(
                              a.updated_at || 0
                            )
                        )
                        .map((s) => (
                          <Tr key={s.session_id}>

                            {/* Session */}
                            <Td className="font-mono text-xs text-zinc-300">
                              {s.session_id}
                            </Td>

                            {/* Pipeline */}
                            <Td>
                              <Pipeline
                                current={s.status}
                              />
                            </Td>

                            {/* Status */}
                            <Td>
                              <StatusBadge
                                status={s.status}
                              />
                            </Td>

                            {/* Risk */}
                            <Td>
                              {s.risk_score != null ? (
                                <Badge
                                  variant={riskColor(
                                    s.risk_score
                                  )}
                                >
                                  {s.risk_score.toFixed(2)}
                                </Badge>
                              ) : (
                                <span className="text-muted">
                                  —
                                </span>
                              )}
                            </Td>

                            {/* Worker */}
                            <Td className="font-mono text-xs text-muted">
                              {s.assigned_node ?? "—"}
                            </Td>

                            {/* Updated */}
                            <Td className="text-muted">
                              {formatDate(
                                s.updated_at ??
                                  s.end_time
                              )}
                            </Td>

                          </Tr>
                        ))}
                    </Tbody>
                  </Table>
                </Card>

              </div>
            )}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}