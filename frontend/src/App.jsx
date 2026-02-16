import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  const [apiUrl] = useState(
    process.env.REACT_APP_API_URL || 'http://localhost:8000'
  );

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>🩺 HealthMate Advanced</h1>
          <p>Emergency Medical Triage & Assessment System</p>
          <p className="subtitle">Powered by Grok AI + Gemini Reports</p>
        </div>
      </header>

      <main className="app-main">
        <div className="app-container">
          <ChatInterface apiUrl={apiUrl} />
        </div>
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <p className="disclaimer">
            ⚠️ <strong>Medical Disclaimer:</strong> This system is for emergency triage guidance only.
            It is NOT a substitute for professional medical diagnosis or treatment.
            Always consult qualified healthcare professionals. In emergencies, CALL 911 IMMEDIATELY.
          </p>
          <p className="version">HealthMate Advanced v2.0.0 | Grok + Gemini Powered</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
