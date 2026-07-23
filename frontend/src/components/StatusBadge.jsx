const CLASS_BY_STATUS = {
  Open: "badge badge-status-open",
  Investigating: "badge badge-status-investigating",
  Resolved: "badge badge-status-resolved",
  "False Positive": "badge badge-status-falsepositive",
};

export default function StatusBadge({ status }) {
  const className = CLASS_BY_STATUS[status] || "badge";
  return <span className={className}>{status}</span>;
}
