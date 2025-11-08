import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function UploadPage() {
  const [file, setFile] = useState(null);
  const [option, setOption] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // ✅ Use environment variable (set in Docker/Kubernetes) or fallback for local dev
  const backendUrl =
    process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleAnalyze = async () => {
    if (!file || !option) {
      alert("Please select a video and model type before analyzing.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("model_name", option);

      console.log("📡 Sending request to backend:", `${backendUrl}/analyze`);

      const response = await fetch(`${backendUrl}/analyze`, {
        method: "POST",
        body: formData,
      });

      // Check if backend is reachable
      if (!response.ok) {
        const errText = await response.text();
        throw new Error(
          `Server responded with ${response.status}: ${errText || "Unknown error"}`
        );
      }

      const data = await response.json();

      // Navigate with backend results
      navigate("/result", {
        state: {
          fileName: data.filename,
          isReal: data.aggregate.mean < 0.5,
          option,
          analysis: {
            face: Math.round(data.aggregate.mean * 100),
            temporal: Math.round(data.aggregate.median * 100),
            artifact: Math.round(data.aggregate.majority_ratio * 100),
            lipsync: Math.round(data.aggregate.mean * 100),
          },
          thumbnails: data.thumbnails?.slice(0, 10) || [],
        },
      });
    } catch (err) {
      console.error("❌ Error analyzing video:", err);
      alert(`Failed to analyze video.\nReason: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1 className="title">Deep Fake Video Detection</h1>
      <p className="subtitle">
        AI-powered analysis to detect manipulated video content with precision
        and reliability.
      </p>

      <div className="upload-box">
        <input type="file" accept="video/*" onChange={handleFileChange} />

        <div className="dropdown">
          <label>Select Analysis Type:</label>
          <select
            value={option}
            onChange={(e) => setOption(e.target.value)}
            disabled={loading}
          >
            <option value="">-- Choose an option --</option>
            <option value="efficientnet_ffpp">EfficientNet FF++ Model</option>
          </select>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={!file || !option || loading}
          className="btn"
        >
          {loading ? "Analyzing..." : "Analyze Video"}
        </button>
      </div>
    </div>
  );
}

export default UploadPage;
