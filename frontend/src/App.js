import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import UploadPage from "./UploadPage";
import ResultPage from "./ResultPage";
import "./styles.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/result" element={<ResultPage />} />
      </Routes>
    </Router>
  );
}

export default App;
