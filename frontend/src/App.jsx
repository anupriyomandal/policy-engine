import React, { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const highlightText = (text, query) => {
  if (!query) return text;
  const tokens = query
    .split(/\s+/)
    .map((t) => t.trim())
    .filter(Boolean)
    .slice(0, 6);
  if (!tokens.length) return text;

  const pattern = new RegExp(`(${tokens.join("|")})`, "i");
  return text.split(pattern).map((part, index) => {
    if (pattern.test(part)) {
      return (
        <mark key={`${part}-${index}`} className="highlight">
          {part}
        </mark>
      );
    }
    return <span key={`${part}-${index}`}>{part}</span>;
  });
};

export default function App() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("Idle");
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [confidence, setConfidence] = useState(0);
  const [sources, setSources] = useState([]);
  const [showSources, setShowSources] = useState(true);
  const [isQuerying, setIsQuerying] = useState(false);

  const confidenceLabel = useMemo(() => {
    if (confidence >= 0.75) return "High";
    if (confidence >= 0.45) return "Medium";
    return "Low";
  }, [confidence]);

  const handleUpload = async (event) => {
    event.preventDefault();
    if (!file) return;

    try {
      setUploadStatus("Uploading...");
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API_BASE}/upload-doc`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Upload failed");
      }
      const data = await response.json();
      setUploadStatus(`Uploaded ${data.filename} (${data.chunks_created} chunks)`);
    } catch (error) {
      setUploadStatus("Upload failed. Check backend logs.");
    }
  };

  const handleQuery = async (event) => {
    event.preventDefault();
    if (!query.trim()) return;

    try {
      setIsQuerying(true);
      const response = await fetch(`${API_BASE}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, include_sources: true }),
      });
      if (!response.ok) {
        throw new Error("Query failed");
      }
      const data = await response.json();
      setAnswer(data.answer || "");
      setConfidence(data.confidence || 0);
      setSources(data.sources || []);
    } catch (error) {
      setAnswer("Query failed. Check backend logs.");
      setConfidence(0);
      setSources([]);
    } finally {
      setIsQuerying(false);
    }
  };

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">Anupriyo Mandal's Policy Intelligence Engine</p>
          <h1>Search policies like a strategist, not a scavenger.</h1>
          <p className="subtitle">
            Upload SOPs, legal policies, or regulatory PDFs. Ask precise questions. Get grounded answers with traceable sources.
          </p>
        </div>
        <div className="hero-card">
          <div className="stat">
            <span>Confidence</span>
            <strong>{Math.round(confidence * 100)}%</strong>
            <small>{confidenceLabel}</small>
          </div>
          <div className="stat">
            <span>Sources</span>
            <strong>{sources.length}</strong>
            <small>Retrieved chunks</small>
          </div>
        </div>
      </header>

      <main className="grid">
        <section className="panel">
          <h2>Upload documents</h2>
          <p className="panel-copy">PDFs and text files are chunked, embedded, and stored in pgvector.</p>
          <form className="upload" onSubmit={handleUpload}>
            <input
              type="file"
              accept=".pdf,.txt,.md"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
            <button type="submit">Upload</button>
          </form>
          <p className="status">{uploadStatus}</p>
        </section>

        <section className="panel">
          <h2>Ask a question</h2>
          <form className="query" onSubmit={handleQuery}>
            <textarea
              placeholder="What are the labeling requirements for dairy exports?"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
            <button type="submit" disabled={isQuerying}>
              {isQuerying ? "Querying..." : "Query"}
            </button>
          </form>
        </section>

        <section className="panel answer">
          <div className="answer-header">
            <h2>Answer</h2>
            <label className="toggle">
              <input
                type="checkbox"
                checked={showSources}
                onChange={() => setShowSources((prev) => !prev)}
              />
              <span>Show retrieved chunks</span>
            </label>
          </div>
          <div className="answer-body">
            {answer ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{answer}</ReactMarkdown>
            ) : (
              <p>Ask a question to see grounded answers here.</p>
            )}
          </div>
        </section>

        <section className="panel sources">
          <h2>Sources</h2>
          {showSources ? (
            sources.length ? (
              <div className="source-list">
                {sources.map((source) => (
                  <article className="source-card" key={source.chunk_id}>
                    <header>
                      <div>
                        <strong>{source.filename}</strong>
                        <span>Page {source.page_number || "N/A"}</span>
                      </div>
                      <span className="score">{Math.round(source.similarity * 100)}%</span>
                    </header>
                    <p>{highlightText(source.content, query)}</p>
                  </article>
                ))}
              </div>
            ) : (
              <p className="empty">No sources to show yet.</p>
            )
          ) : (
            <p className="empty">Sources hidden. Toggle to reveal retrieved chunks.</p>
          )}
        </section>
      </main>

      <footer className="footer">
        <p>Powered by pgvector + OpenAI embeddings + FastAPI.</p>
        <p>© {new Date().getFullYear()} Anupriyo Mandal</p>
      </footer>
    </div>
  );
}
