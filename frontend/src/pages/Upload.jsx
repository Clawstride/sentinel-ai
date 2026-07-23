import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { uploadLogFile, generateIncidents } from "../services/api";

export default function Upload() {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  const [generating, setGenerating] = useState(false);
  const [generateResult, setGenerateResult] = useState(null);
  const [generateError, setGenerateError] = useState(null);

  function handleFileChange(event) {
    const file = event.target.files?.[0] || null;
    setSelectedFile(file);
    setUploadResult(null);
    setUploadError(null);
    setGenerateResult(null);
    setGenerateError(null);
  }

  async function handleUpload() {
    if (!selectedFile) return;
    setUploading(true);
    setUploadError(null);
    setUploadResult(null);
    try {
      const result = await uploadLogFile(selectedFile);
      setUploadResult(result);
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleGenerate() {
    setGenerating(true);
    setGenerateError(null);
    setGenerateResult(null);
    try {
      const result = await generateIncidents();
      setGenerateResult(result);
    } catch (err) {
      setGenerateError(err.message);
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Upload Logs</h1>
          <p className="page-subtitle">
            Import authentication events, then run threat analysis to
            generate incidents.
          </p>
        </div>
      </div>

      <div className="panel" style={{ maxWidth: 640 }}>
        <div className="panel-header">
          <h2>Step 1 · Upload Authentication Logs</h2>
        </div>
        <div className="panel-body">
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              marginBottom: 16,
            }}
          >
            <button className="btn" onClick={() => fileInputRef.current?.click()}>
              Choose CSV File
            </button>
            <span
              style={{
                color: selectedFile ? "var(--text-primary)" : "var(--text-muted)",
                fontSize: 13,
              }}
            >
              {selectedFile ? selectedFile.name : "No file selected"}
            </span>
          </div>

          <button
            className="btn btn-primary"
            disabled={!selectedFile || uploading}
            onClick={handleUpload}
          >
            {uploading ? "Uploading…" : "Upload"}
          </button>

          {uploadError && (
            <p
              style={{
                color: "var(--severity-high-fg)",
                marginTop: 14,
                fontSize: 13,
              }}
            >
              {uploadError}
            </p>
          )}

          {uploadResult && (
            <div
              style={{
                marginTop: 16,
                padding: "12px 14px",
                background: "var(--status-resolved-bg)",
                color: "var(--status-resolved-fg)",
                borderRadius: "var(--radius-sm)",
                fontSize: 13.5,
              }}
            >
              {uploadResult.rows_imported} authentication events imported.
            </div>
          )}
        </div>
      </div>

      {uploadResult && (
        <div className="panel" style={{ maxWidth: 640, marginTop: 20 }}>
          <div className="panel-header">
            <h2>Step 2 · Run Threat Analysis</h2>
          </div>
          <div className="panel-body">
            <p
              style={{
                color: "var(--text-secondary)",
                fontSize: 13,
                marginBottom: 16,
              }}
            >
              Runs brute force, impossible travel, new device, and privileged
              login detection over the stored logs, then creates incidents
              for anything not already flagged.
            </p>

            <button
              className="btn btn-primary"
              disabled={generating}
              onClick={handleGenerate}
            >
              {generating ? "Analyzing…" : "Run Threat Analysis"}
            </button>

            {generateError && (
              <p
                style={{
                  color: "var(--severity-high-fg)",
                  marginTop: 14,
                  fontSize: 13,
                }}
              >
                {generateError}
              </p>
            )}

            {generateResult && (
              <div style={{ marginTop: 16 }}>
                <div
                  style={{
                    padding: "12px 14px",
                    background: "var(--status-resolved-bg)",
                    color: "var(--status-resolved-fg)",
                    borderRadius: "var(--radius-sm)",
                    fontSize: 13.5,
                    marginBottom: 12,
                  }}
                >
                  {generateResult.incidents_created} new incident
                  {generateResult.incidents_created === 1 ? "" : "s"} generated.
                </div>
                <Link to="/incidents" className="btn">
                  View Incidents
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
