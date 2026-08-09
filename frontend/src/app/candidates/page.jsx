"use client";
import { useState, useMemo } from "react";
import { endpoints } from "@/lib/api";
import useSWR from "swr";
import {
  UserCircle,
  Search,
  BarChart3,
  Activity,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import Card from "@/components/Card";
import Stat from "@/components/Stat";
import StatsCards from "@/components/StatsCards";
import { StatusBadge, Badge } from "@/components/Badge";
import { Skeleton, ErrorState, EmptyState } from "@/components/States";
import { SearchInput, Table, Thead, Tbody, Tr, Th, Td } from "@/components/ui";
import Pipeline from "@/components/Pipeline";
import {
  formatDate,
  formatRelative,
  riskColor,
  formatPercent,
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
  const completed = useSWR("/completed-sessions?limit=100", { refreshInterval: 10000 });
  const failed = useSWR("/failed-sessions?limit=100", { refreshInterval: 10000 });
  const active = useSWR("/active-sessions", { refreshInterval: 5000 });

  const candidates = useMemo(() => {
    const map = new Map();
    const allSessions = [
      ...(completed.data?.sessions ?? []),
      ...(failed.data?.sessions ?? []),
      ...(active.data?.sessions ?? []),
    ];

    for (const s of allSessions) {
      const id = s.candidate_id || "unknown";
      if (!map.has(id)) {
        map.set(id, {
          candidate_id: id,
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
      if (s.status === "COMPLETED") c.completed_sessions += 1;
      else if (s.status === "FAILED" || s.status === "TIMEOUT") c.failed_sessions += 1;
      else c.active_sessions += 1;
      if (s.risk_score != null) c.risk_scores.push(s.risk_score);
    }

    return Array.from(map.values())
      .map((c) => ({
        ...c,
        avg_risk_score:
          c.risk_scores.length > 0
            ? c.risk_scores.reduce((a, b) => a + b, 0) / c.risk_scores.length
            : null,
        latest_session: c.sessions.sort(
          (a, b) => new Date(b.updated_at || 0) - new Date(a.updated_at || 0)
        )[0],
      }))
      .sort((a, b) => b.total_sessions - a.total_sessions);
  }, [completed.data, failed.data, active.data]);

  return {
    candidates,
    isLoading: completed.isLoading && failed.isLoading,
    error: completed.error || failed.error,
    mutate: () => {
      completed.mutate();
      failed.mutate();
      active.mutate();
    },
  };
}

export default function CandidatesPage() {
  const { candidates, isLoading, error, mutate } = useCandidateData();
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState(null);

  const filtered = useMemo(() => {
    if (!search.trim()) return candidates;
    const q = search.toLowerCase();
    return candidates.filter((c) => c.candidate_id.toLowerCase().includes(q));
  }, [candidates, search]);

  const selected = candidates.find((c) => c.candidate_id === selectedId);

  const statusData = useMemo(() => {
    if (!selected) return [];
    const counts = {};
    for (const s of selected.sessions) {
      counts[s.status] = (counts[s.status] || 0) + 1;
    }
    return Object.entries(counts).map(([status, count]) => ({ status, count }));
  }, [selected]);

  return (
    <ErrorBoundary>
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-zinc-50">Candidates</h1>
            <p className="text-sm text-muted">Candidate profiles, interview history, and performance analytics.</p>
          </div>
          <div className="text-xs text-muted">
            {candidates.length} candidates
          </div>
        </div>
        <CandidateRegistrationForm onRegistered={mutate} />

        <StatsCards
          data={{
            totalCandidates: candidates.length,
            pendingReview: candidates.reduce((a, c) => a + c.active_sessions, 0),
            completed: candidates.reduce((a, c) => a + c.completed_sessions, 0),
            activeNow: candidates.filter((c) => c.active_sessions > 0).length,
          }}
        />

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
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
                <ErrorState error={error} onRetry={mutate} />
              ) : isLoading ? (
                <Skeleton className="h-48 w-full" />
              ) : filtered.length === 0 ? (
                <EmptyState
                  title="No candidates"
                  description="Candidate data will appear after sessions are completed."
                />
              ) : (
                <div className="max-h-[500px] space-y-1 overflow-y-auto">
                  {filtered.map((c) => (
                    <button
                      key={c.candidate_id}
                      onClick={() => setSelectedId(c.candidate_id)}
                      className={cn(
                        "flex w-full items-center justify-between rounded-md px-3 py-2.5 text-left text-sm transition-colors",
                        selectedId === c.candidate_id
                          ? "bg-accent/15 text-accent-light"
                          : "text-zinc-300 hover:bg-bg-card"
                      )}
                    >
                      <div className="min-w-0">
                        <div className="truncate font-mono text-xs text-zinc-200">
                          {c.candidate_id}
                        </div>
                        <div className="text-[10px] text-muted">
                          {c.total_sessions} session{c.total_sessions !== 1 ? "s" : ""}
                        </div>
                      </div>
                      {c.avg_risk_score != null && (
                        <Badge variant={riskColor(c.avg_risk_score)}>
                          {c.avg_risk_score.toFixed(2)}
                        </Badge>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </Card>
          </div>

          <div className="lg:col-span-2">
            {!selected ? (
              <Card>
                <div className="flex flex-col items-center justify-center py-16 text-center">
                  <UserCircle size={48} className="mb-3 text-muted opacity-30" />
                  <p className="text-sm text-zinc-300">Select a candidate to view details</p>
                  <p className="mt-1 text-xs text-muted">
                    Click on a candidate from the list to see their profile
                  </p>
                </div>
              </Card>
            ) : (
              <div className="space-y-4">
                <Card title={selected.candidate_id} description="Candidate profile and performance">
                  <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                    <div className="rounded-md border border-border bg-bg-card px-3 py-2.5">
                      <div className="text-[10px] uppercase tracking-wide text-muted">Total</div>
                      <div className="mt-1 text-lg font-semibold text-zinc-50">
                        {selected.total_sessions}
                      </div>
                    </div>
                    <div className="rounded-md border border-border bg-bg-card px-3 py-2.5">
                      <div className="text-[10px] uppercase tracking-wide text-muted">Completed</div>
                      <div className="mt-1 text-lg font-semibold text-emerald-400">
                        {selected.completed_sessions}
                      </div>
                    </div>
                    <div className="rounded-md border border-border bg-bg-card px-3 py-2.5">
                      <div className="text-[10px] uppercase tracking-wide text-muted">Failed</div>
                      <div className="mt-1 text-lg font-semibold text-rose-400">
                        {selected.failed_sessions}
                      </div>
                    </div>
                    <div className="rounded-md border border-border bg-bg-card px-3 py-2.5">
                      <div className="text-[10px] uppercase tracking-wide text-muted">Avg Risk</div>
                      <div className="mt-1 text-lg font-semibold text-zinc-50">
                        {selected.avg_risk_score != null ? selected.avg_risk_score.toFixed(3) : "—"}
                      </div>
                    </div>
                  </div>
                </Card>

                {statusData.length > 0 && (
                  <Card title="Session Status Distribution">
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={statusData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                        <XAxis dataKey="status" stroke="#71717a" fontSize={11} />
                        <YAxis stroke="#71717a" fontSize={11} />
                        <Tooltip
                          contentStyle={{
                            background: "#12121a",
                            border: "1px solid #27272a",
                            borderRadius: 8,
                          }}
                        />
                        <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </Card>
                )}

                <Card title="Interview History" description="All sessions for this candidate">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="text-left text-xs uppercase tracking-wide text-muted">
                        <tr>
                          <th className="py-2 pr-4">Session</th>
                          <th className="py-2 pr-4">Pipeline</th>
                          <th className="py-2 pr-4">Status</th>
                          <th className="py-2 pr-4">Risk</th>
                          <th className="py-2 pr-4">Worker</th>
                          <th className="py-2 pr-4">Updated</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selected.sessions
                          .sort(
                            (a, b) =>
                              new Date(b.updated_at || 0) - new Date(a.updated_at || 0)
                          )
                          .map((s) => (
                            <tr key={s.session_id} className="border-t border-border">
                              <td className="py-2 pr-4 font-mono text-xs text-zinc-300">
                                {s.session_id}
                              </td>
                              <td className="py-2 pr-4">
                                <Pipeline current={s.status} />
                              </td>
                              <td className="py-2 pr-4">
                                <StatusBadge status={s.status} />
                              </td>
                              <td className="py-2 pr-4">
                                {s.risk_score != null ? (
                                  <Badge variant={riskColor(s.risk_score)}>
                                    {s.risk_score.toFixed(2)}
                                  </Badge>
                                ) : (
                                  <span className="text-muted">—</span>
                                )}
                              </td>
                              <td className="py-2 pr-4 font-mono text-xs text-muted">
                                {s.assigned_node ?? "—"}
                              </td>
                              <td className="py-2 pr-4 text-muted">
                                {formatDate(s.updated_at ?? s.end_time)}
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              </div>
            )}
          </div>
        </div>

        <div className="lg:col-span-2">
          {!selected ? (
            <Card>
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <UserCircle size={48} className="mb-3 text-muted opacity-30" />
                <p className="text-sm text-zinc-300">Select a candidate to view details</p>
                <p className="mt-1 text-xs text-muted">
                  Click on a candidate from the list to see their profile
                </p>
              </div>
            </Card>
          ) : (
            <div className="space-y-4">
              <Card title={selected.candidate_id} description="Candidate profile and performance">
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  <div className="rounded-md border border-border bg-bg-card px-3 py-2.5">
                    <div className="text-[10px] uppercase tracking-wide text-muted">Total</div>
                    <div className="mt-1 text-lg font-semibold text-zinc-50">
                      {selected.total_sessions}
                    </div>
                  </div>
                  <div className="rounded-md border border-border bg-bg-card px-3 py-2.5">
                    <div className="text-[10px] uppercase tracking-wide text-muted">Completed</div>
                    <div className="mt-1 text-lg font-semibold text-emerald-400">
                      {selected.completed_sessions}
                    </div>
                  </div>
                  <div className="rounded-md border border-border bg-bg-card px-3 py-2.5">
                    <div className="text-[10px] uppercase tracking-wide text-muted">Failed</div>
                    <div className="mt-1 text-lg font-semibold text-rose-400">
                      {selected.failed_sessions}
                    </div>
                  </div>
                  <div className="rounded-md border border-border bg-bg-card px-3 py-2.5">
                    <div className="text-[10px] uppercase tracking-wide text-muted">Avg Risk</div>
                    <div className="mt-1 text-lg font-semibold text-zinc-50">
                      {selected.avg_risk_score != null ? selected.avg_risk_score.toFixed(3) : "—"}
                    </div>
                  </div>
                </div>
              </Card>

              {statusData.length > 0 && (
                <Card title="Session Status Distribution">
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={statusData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                      <XAxis dataKey="status" stroke="#71717a" fontSize={11} />
                      <YAxis stroke="#71717a" fontSize={11} />
                      <Tooltip
                        contentStyle={{
                          background: "#12121a",
                          border: "1px solid #27272a",
                          borderRadius: 8,
                        }}
                      />
                      <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              )}

              <Card title="Interview History" description="All sessions for this candidate">
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
                          new Date(b.updated_at || 0) - new Date(a.updated_at || 0)
                      )
                      .map((s) => (
                        <Tr key={s.session_id}>
                          <Td className="font-mono text-xs text-zinc-300">{s.session_id}</Td>
                          <Td><Pipeline current={s.status} /></Td>
                          <Td><StatusBadge status={s.status} /></Td>
                          <Td>
                            {s.risk_score != null ? (
                              <Badge variant={riskColor(s.risk_score)}>
                                {s.risk_score.toFixed(2)}
                              </Badge>
                            ) : (
                              <span className="text-muted">—</span>
                            )}
                          </Td>
                          <Td className="font-mono text-xs text-muted">{s.assigned_node ?? "—"}</Td>
                          <Td className="text-muted">{formatDate(s.updated_at ?? s.end_time)}</Td>
                        </Tr>
                      ))}
                  </Tbody>
                </Table>
              </Card>
            </div>
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
}

function CandidateRegistrationForm({ onRegistered }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [skills, setSkills] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const submit = async (event) => {
    event.preventDefault();

    setSubmitting(true);
    setError("");
    setSuccess("");

    try {
      const candidate = await endpoints.createCandidate({
        name: name.trim(),
        email: email.trim(),
        resume_text: resumeText.trim() || null,
        skills: skills
          .split(",")
          .map((skill) => skill.trim())
          .filter(Boolean),
      });

      setSuccess(
        `Candidate ${candidate.candidate_id ?? candidate.name ?? name.trim()} registered successfully.`
      );

      setName("");
      setEmail("");
      setResumeText("");
      setSkills("");

      onRegistered?.(candidate);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to register candidate"
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card
      title="Candidate Registration"
      description="Create a new candidate profile."
    >
      <form
        onSubmit={submit}
        noValidate={false}
        className="space-y-4"
      >
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label
              htmlFor="candidate-name"
              className="block text-xs font-medium text-muted"
            >
              Name
            </label>

            <input
              id="candidate-name"
              name="name"
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
              minLength={1}
              maxLength={200}
              placeholder="Jane Doe"
              className="mt-1 w-full rounded-md border border-border bg-bg-card px-3 py-2 text-sm text-zinc-100 placeholder:text-muted focus:border-accent focus:outline-none"
            />
          </div>

          <div>
            <label
              htmlFor="candidate-email"
              className="block text-xs font-medium text-muted"
            >
              Email
            </label>

            <input
              id="candidate-email"
              name="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              maxLength={255}
              placeholder="jane@example.com"
              className="mt-1 w-full rounded-md border border-border bg-bg-card px-3 py-2 text-sm text-zinc-100 placeholder:text-muted focus:border-accent focus:outline-none"
            />
          </div>
        </div>

        <div>
          <label
            htmlFor="candidate-resume"
            className="block text-xs font-medium text-muted"
          >
            Resume
          </label>

          <textarea
            id="candidate-resume"
            name="resume"
            value={resumeText}
            onChange={(event) => setResumeText(event.target.value)}
            rows={4}
            placeholder="Candidate resume information..."
            className="mt-1 w-full rounded-md border border-border bg-bg-card px-3 py-2 text-sm text-zinc-100 placeholder:text-muted focus:border-accent focus:outline-none"
          />
        </div>

        <div>
          <label
            htmlFor="candidate-skills"
            className="block text-xs font-medium text-muted"
          >
            Skills
          </label>

          <input
            id="candidate-skills"
            name="skills"
            type="text"
            value={skills}
            onChange={(event) => setSkills(event.target.value)}
            placeholder="Java, Python, React"
            className="mt-1 w-full rounded-md border border-border bg-bg-card px-3 py-2 text-sm text-zinc-100 placeholder:text-muted focus:border-accent focus:outline-none"
          />

          <p className="mt-1 text-[10px] text-muted">
            Enter skills separated by commas.
          </p>
        </div>

        {error && (
          <div
            role="alert"
            className="rounded-md border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-400"
          >
            {error}
          </div>
        )}

        {success && (
          <div
            role="status"
            className="rounded-md border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-xs text-emerald-400"
          >
            {success}
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white transition-opacity disabled:cursor-not-allowed disabled:opacity-50"
          >
            {submitting ? "Registering..." : "Register Candidate"}
          </button>
        </div>
      </form>
    </Card>
  );
}
