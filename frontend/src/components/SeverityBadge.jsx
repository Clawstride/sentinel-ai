const CLASS_BY_SEVERITY = {
  High: "badge badge-severity-high",
  Medium: "badge badge-severity-medium",
  Low: "badge badge-severity-low",
};

export default function SeverityBadge({ severity }) {
  const className = CLASS_BY_SEVERITY[severity] || "badge";
  return <span className={className}>{severity}</span>;
}
