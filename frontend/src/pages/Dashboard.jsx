import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getDashboardSummary, listIncidents } from "../services/api";
import SeverityBadge from "../components/SeverityBadge";
import StatusBadge from "../components/StatusBadge";
import { Loading, ErrorState, EmptyState } from "../components/StateViews";

const RECENT_LIMIT = 8;

function formatDate(value) {
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [summaryData, incidentData] = await Promise.all([
        getDashboardSummary(),
        listIncidents(),
      ]);
      setSummary(summaryData);
      setIncidents(incidentData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) return <Loading label="Loading dashboard…" />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  const typeEntries = Object.entries(summary.incidents_by_type || {}).sort(
    (a, b) => b[1] - a[1]
  );
  const maxTypeCount = typeEntries.length
    ? Math.max(...typeEntries.map(([, count]) => count))
    : 1;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p className="page-subtitle">
            Live incident metrics from the SentinelAI detection engine.
          </p>
        </div>
      </div>

      <div className="metric-grid">
        <div className="metric-card">
          <div className="metric-label">Total Incidents</div>
          <div className="metric-value">{summary.total_incidents}</div>
        </div>
        <div className="metric-card accent-open">
          <div className="metric-label">Open</div>
          <div className="metric-value">{summary.open_incidents}</div>
        </div>
        <div className="metric-card accent-high">
          <div className="metric-label">High Severity</div>
          <div className="metric-value">{summary.high_incidents}</div>
        </div>
        <div className="metric-card accent-medium">
          <div className="metric-label">Medium Severity</div>
          <div className="metric-value">{summary.medium_incidents}</div>
        </div>
        <div className="metric-card accent-low">
          <div className="metric-label">Low Severity</div>
          <div className="metric-value">{summary.low_incidents}</div>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1.7fr 1fr",
          gap: 16,
          alignItems: "start",
        }}
      >
        <div className="panel">
          <div className="panel-header">
            <h2>Recent Incidents</h2>
          </div>
          {incidents.length === 0 ? (
            <EmptyState
              title="No incidents yet"
              message="Upload authentication logs and run threat analysis to generate incidents."
            />
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Incident ID</th>
                  <th>Type</th>
                  <th>Username</th>
                  <th>Severity</th>
                  <th>Risk</th>
                  <th>Status</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {incidents.slice(0, RECENT_LIMIT).map((incident) => (
                  <tr
                    key={incident.incident_id}
                    onClick={() => navigate(`/incidents/${incident.incident_id}`)}
                  >
                    <td className="mono">{incident.incident_id}</td>
                    <td>{incident.incident_type}</td>
                    <td>{incident.username}</td>
                    <td>
                      <SeverityBadge severity={incident.severity} />
                    </td>
                    <td className="mono">{incident.risk_score}</td>
                    <td>
                      <StatusBadge status={incident.status} />
                    </td>
                    <td>{formatDate(incident.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2>By Detection Type</h2>
          </div>
          <div className="panel-body">
            {typeEntries.length === 0 ? (
              <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>
                No detections recorded yet.
              </p>
            ) : (
              typeEntries.map(([type, count]) => (
                <div className="type-bar-row" key={type}>
                  <span>{type}</span>
                  <div className="type-bar-track">
                    <div
                      className="type-bar-fill"
                      style={{ width: `${(count / maxTypeCount) * 100}%` }}
                    />
                  </div>
                  <span className="type-bar-count">{count}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
