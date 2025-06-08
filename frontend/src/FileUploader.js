import React, { useState } from "react";
import { Accordion, Card, Spinner } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import axios from 'axios';

function FileUploader() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [jobId, setJobId] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append('old_file', e.target.old_file.files[0]);
    formData.append('new_file', e.target.new_file.files[0]);

    try {
      const response = await axios.post('http://localhost:5000/analyze', formData, {
        timeout: 300000, // 5 minutes
      });

      if (response.status === 202 && response.data.job_id) {
        setJobId(response.data.job_id);
        pollForResults(response.data.job_id);
      } else if (response.status === 200) {
        setResults(response.data); // Direct result
      } else {
        throw new Error("Unexpected response from server.");
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      setLoading(false);
    }
  };

  const pollForResults = (id) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`http://localhost:5000/results?id=${id}`);
        if (response.data.status === 'complete') {
          clearInterval(interval);
          setResults(response.data.data);
          setLoading(false);
        } else if (response.data.status === 'error') {
          clearInterval(interval);
          setError(response.data.message || "Error during processing");
          setLoading(false);
        }
      } catch (err) {
        clearInterval(interval);
        setError("Polling failed: " + err.message);
        setLoading(false);
      }
    }, 5000); // Poll every 5s
  };

  const renderChangeCard = (change, index, type) => {
    const analysis = results.analysis[type][index];
    return (
      <Card key={`${type}-${index}`} className="mb-3">
        <Card.Header>
          {type.toUpperCase()} Section {index + 1}
          <span className="badge bg-secondary ms-2">
            {analysis?.change_type || type}
          </span>
        </Card.Header>
        <Card.Body>
          {type === 'modified' && (
            <>
              <h5>Original Version:</h5>
              <pre className="bg-light p-2">{change.old}</pre>
              <h5>Modified Version:</h5>
              <pre className="bg-light p-2">{change.new}</pre>
            </>
          )}
          {type !== 'modified' && (
            <pre className="bg-light p-2">{change}</pre>
          )}
          {analysis && (
            <>
              <h5>Analysis:</h5>
              <div className="alert alert-info">
                <strong>Summary:</strong> {analysis.change_summary}
                <br />
                <strong>Impact:</strong> {analysis.potential_impact}
              </div>
            </>
          )}
        </Card.Body>
      </Card>
    );
  };

  return (
    <div className="container mt-4">
      <h1 className="mb-4">Regulatory Change Analyzer</h1>

      <Card className="mb-4">
        <Card.Body>
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label htmlFor="old_file" className="form-label">Original Document:</label>
              <input type="file" className="form-control" id="old_file" name="old_file" accept=".txt" required />
            </div>
            <div className="mb-3">
              <label htmlFor="new_file" className="form-label">Updated Document:</label>
              <input type="file" className="form-control" id="new_file" name="new_file" accept=".txt" required />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (
                <>
                  <Spinner animation="border" size="sm" className="me-2" />
                  Analyzing...
                </>
              ) : 'Analyze Changes'}
            </button>
          </form>
        </Card.Body>
      </Card>

      {error && <div className="alert alert-danger">Error: {error}</div>}

      {results && (
        <div className="mt-4">
          <h2>Analysis Results</h2>

          <div className="mb-4">
            <h3>Added Sections ({results.changes.added.length})</h3>
            {results.changes.added.map((change, index) =>
              renderChangeCard(change, index, 'added')
            )}
          </div>

          <div className="mb-4">
            <h3>Modified Sections ({results.changes.modified.length})</h3>
            {results.changes.modified.map((change, index) =>
              renderChangeCard(change, index, 'modified')
            )}
          </div>

          <div className="mb-4">
            <h3>Deleted Sections ({results.changes.deleted.length})</h3>
            {results.changes.deleted.map((change, index) =>
              renderChangeCard(change, index, 'deleted')
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default FileUploader;
