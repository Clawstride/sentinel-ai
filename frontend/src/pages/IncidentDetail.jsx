import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  getIncident,
  getIncidentInvestigation,
  updateIncidentStatus,
  updateIncidentNotes,
} from "../services/api";
import SeverityBadge from "../components/SeverityBadge";
import StatusBadge from "../components/StatusBadge";
import RiskGauge from "../components/RiskGauge";
import { Loading, ErrorState } from "../components/StateViews";

const STATUS_OPTIONS = ["Open", "Investigating", "Resolved", "False Positive"];

function formatDateTime(value) {
  return new Date(value).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function IncidentDetail() {
  const { incidentId } = useParams();

  const [incident, setIncident] = useState(null);
  const [investigation, setInvestigation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [statusSaving, setStatusSaving] = useState(false);
  const [statusError, setStatusError] = useState(null);

  const [notesDraft, setNotesDraft] = useState("");
  const [notesSaving, setNotesSaving] = useState(false);
  const [notesError, setNotesError] = useState(null);
  const [notesSaved, setNotesSaved] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [incidentData, investigationData] = await Promise.all([
        getIncident(incidentId),
        getIncidentInvestigation(incidentId),
      ]);
      setIncident(incidentData);
      setInvestigation(investigationData);
      setNotesDraft(incidentData.notes || "");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [incidentId]);

  async function handleStatusChange(newStatus) {
    setStatusSaving(true);
    setStatusError(null);
    try {
      const updated = await updateIncidentStatus(incidentId, newStatus);
      setIncident(updated);
      setInvestigation((prev) => (prev ? { ...prev, status: updated.status } : prev));
    } catch (err) {
      setStatusError(err.message);
    } finally {
      setStatusSaving(false);
    }
  }

  async function handleSaveNotes() {
    setNotesSaving(true);
    setNotesError(null);
    setNotesSaved(false);
    try {
      const updated = await updateIncidentNotes(incidentId, notesDraft);
      setIncident(updated);
      setNotesSaved(true);
    } catch (err) {
      setNotesError(err.message);
    } finally {
      setNotesSaving(false);
    }
  }

  if (loading) return <Loading label="Loading investigation…" />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!incident || !investigation) return null;

  return (
    <div>
      <Link
        to="/incidents"
        style={{
          fontSize: 12.5,
          color: "var(--text-secondary)",
          textDecoration: "none",
          display: "inline-block",
          marginBottom: 14,
        }}
      >
        ← Back to Incidents
      </Link>

      {/* ---- Header ---- */}
      <div
        className="panel"
        style={{ padding: 22, display: "flex", gap: 24, marginBottom: 20 }}
      >
        <RiskGauge score={investigation.risk_score} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              flexWrap: "wrap",
              marginBottom: 6,
            }}
          >
            <span className="mono" style={{ color: "var(--text-secondary)", fontSize: 13 }}>
              {investigation.incident_id}
            </span>
            <SeverityBadge severity={investigation.severity} />
            <StatusBadge status={incident.status} />
          </div>
          <h1 style={{ fontSize: 17, marginBottom: 10 }}>{investigation.title}</h1>
          <div
            style={{
              display: "flex",
              gap: 24,
              fontSize: 12.5,
              color: "var(--text-secondary)",
              flexWrap: "wrap",
            }}
          >
            <span>
              Type: <strong style={{ color: "var(--text-primary)" }}>{investigation.incident_type}</strong>
            </span>
            <span>
              Username: <strong className="mono" style={{ color: "var(--text-primary)" }}>{investigation.username}</strong>
            </span>
            {incident.source_ip && (
              <span>
                Source IP: <strong className="mono" style={{ color: "var(--text-primary)" }}>{incident.source_ip}</strong>
              </span>
            )}
            <span>Created: {formatDateTime(incident.created_at)}</span>
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.7fr 1fr", gap: 16, alignItems: "start" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* ---- AI Investigation Summary ---- */}
          <div className="panel">
            <div className="panel-header">
              <h2>AI Investigation Summary</h2>
              <span
                className="badge"
                style={{
                  background: "var(--accent-soft)",
                  color: "var(--accent-strong)",
                }}
              >
                {investigation.ai_summary.generated_by === "ai" ? "AI-generated" : "Deterministic fallback"}
              </span>
            </div>
            <div className="panel-body">
              <p style={{ fontSize: 13.5, lineHeight: 1.7 }}>
                {investigation.ai_summary.summary}
              </p>
            </div>
          </div>

          {/* ---- Why Flagged ---- */}
          <div className="panel">
            <div className="panel-header">
              <h2>Why SentinelAI Flagged This</h2>
            </div>
            <div className="panel-body">
              <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 10 }}>
                {investigation.indicators.map((indicator, idx) => (
                  <li key={idx} style={{ display: "flex", gap: 10, fontSize: 13.5 }}>
                    <span style={{ color: "var(--accent-strong)", flexShrink: 0 }}>✓</span>
                    <span>{indicator}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* ---- Timeline ---- */}
          <div className="panel">
            <div className="panel-header">
              <h2>Event Timeline / Evidence</h2>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>IP Address</th>
                  <th>Country</th>
                  <th>Device</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {investigation.timeline.map((event, idx) => (
                  <tr key={idx} style={{ cursor: "default" }}>
                    <td className="mono">{formatDateTime(event.timestamp)}</td>
                    <td className="mono">{event.ip_address}</td>
                    <td>{event.country}</td>
                    <td>{event.device}</td>
                    <td>
                      <span
                        style={{
                          color:
                            event.login_status?.toLowerCase() === "success" ||
                            event.login_status?.toLowerCase() === "successful"
                              ? "var(--status-resolved-fg)"
                              : "var(--severity-high-fg)",
                          fontWeight: 600,
                        }}
                      >
                        {event.login_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* ---- Recommended Actions ---- */}
          <div className="panel">
            <div className="panel-header">
              <h2>Recommended Investigation Actions</h2>
            </div>
            <div className="panel-body">
              <ul style={{ margin: 0, paddingLeft: 18, display: "flex", flexDirection: "column", gap: 8 }}>
                {investigation.recommended_actions.map((action, idx) => (
                  <li key={idx} style={{ fontSize: 13.5 }}>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* ---- Right column: status + notes ---- */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="panel">
            <div className="panel-header">
              <h2>Incident Status</h2>
            </div>
            <div className="panel-body">
              <select
                className="filter-select"
                style={{ width: "100%" }}
                value={incident.status}
                disabled={statusSaving}
                onChange={(e) => handleStatusChange(e.target.value)}
              >
                {STATUS_OPTIONS.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
              {statusSaving && (
                <p style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 8 }}>
                  Saving…
                </p>
              )}
              {statusError && (
                <p style={{ fontSize: 12, color: "var(--severity-high-fg)", marginTop: 8 }}>
                  {statusError}
                </p>
              )}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2>Analyst Notes</h2>
            </div>
            <div className="panel-body">
              <textarea
                value={notesDraft}
                onChange={(e) => {
                  setNotesDraft(e.target.value);
                  setNotesSaved(false);
                }}
                maxLength={2000}
                rows={6}
                placeholder="Add investigation notes…"
                style={{
                  width: "100%",
                  resize: "vertical",
                  background: "var(--bg-surface-raised)",
                  border: "1px solid var(--border-strong)",
                  borderRadius: "var(--radius-sm)",
                  color: "var(--text-primary)",
                  padding: 10,
                  fontSize: 13,
                  fontFamily: "inherit",
                }}
              />
              <button
                className="btn btn-primary"
                style={{ marginTop: 10 }}
                disabled={notesSaving || notesDraft.trim().length === 0}
                onClick={handleSaveNotes}
              >
                {notesSaving ? "Saving…" : "Save Notes"}
              </button>
              {notesSaved && (
                <p style={{ fontSize: 12, color: "var(--status-resolved-fg)", marginTop: 8 }}>
                  Notes saved.
                </p>
              )}
              {notesError && (
                <p style={{ fontSize: 12, color: "var(--severity-high-fg)", marginTop: 8 }}>
                  {notesError}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
