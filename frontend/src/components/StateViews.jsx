export function Loading({ label = "Loading…" }) {
  return (
    <div className="state-block">
      <div className="spinner" />
      {label}
    </div>
  );
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="state-block state-error">
      <div className="state-title">Couldn't load this data</div>
      <p>{message}</p>
      {onRetry && (
        <button className="btn" style={{ marginTop: 16 }} onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title, message }) {
  return (
    <div className="state-block">
      <div className="state-title">{title}</div>
      <p>{message}</p>
    </div>
  );
}
