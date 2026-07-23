import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listIncidents } from "../services/api";
import SeverityBadge from "../components/SeverityBadge";
import StatusBadge from "../components/StatusBadge";
import { Loading, ErrorState, EmptyState } from "../components/StateViews";

function formatDate(value) {
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function IncidentList() {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [severityFilter, setSeverityFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");
  const [typeFilter, setTypeFilter] = useState("All");

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await listIncidents();
      setIncidents(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const types = useMemo(
    () => Array.from(new Set(incidents.map((i) => i.incident_type))).sort(),
    [incidents]
  );

  const filtered = incidents.filter((incident) => {
    if (severityFilter !== "All" && incident.severity !== severityFilter)
      return false;
    if (statusFilter !== "All" && incident.status !== statusFilter)
      return false;
    if (typeFilter !== "All" && incident.incident_type !== typeFilter)
      return false;
    return true;
  });

  if (loading) return <Loading label="Loading incidents…" />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Incidents</h1>
          <p className="page-subtitle">
            {incidents.length} incident{incidents.length === 1 ? "" : "s"} on
            record.
          </p>
        </div>
      </div>

      {incidents.length === 0 ? (
        <div className="panel">
          <EmptyState
            title="No incidents yet"
            message="Upload authentication logs and run threat analysis to generate incidents."
          />
        </div>
      ) : (
        <>
          <div className="filter-bar">
            <select
              className="filter-select"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="All">All severities</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
            <select
              className="filter-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="All">All statuses</option>
              <option value="Open">Open</option>
              <option value="Investigating">Investigating</option>
              <option value="Resolved">Resolved</option>
              <option value="False Positive">False Positive</option>
            </select>
            <select
              className="filter-select"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="All">All types</option>
              {types.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          <div className="panel">
            {filtered.length === 0 ? (
              <EmptyState
                title="No matching incidents"
                message="Try clearing one or more filters."
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
                  {filtered.map((incident) => (
                    <tr
                      key={incident.incident_id}
                      onClick={() =>
                        navigate(`/incidents/${incident.incident_id}`)
                      }
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
        </>
      )}
    </div>
  );
}
