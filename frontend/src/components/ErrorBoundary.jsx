import { Component } from "react";

export default class ErrorBoundary extends Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("SentinelAI UI error:", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 40 }}>
          <div className="panel" style={{ maxWidth: 480, margin: "0 auto" }}>
            <div className="panel-body state-block state-error">
              <div className="state-title">Something went wrong</div>
              <p>
                This page hit an unexpected error. Try reloading — the rest of
                SentinelAI is unaffected.
              </p>
              <button
                className="btn"
                style={{ marginTop: 16 }}
                onClick={() => window.location.reload()}
              >
                Reload
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
