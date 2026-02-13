import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './ChatInterface.css';

const ChatInterface = ({ apiUrl }) => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [triageComplete, setTriageComplete] = useState(false);
  const [isEmergency, setIsEmergency] = useState(false);
  const [result, setResult] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Start new session
  const startSession = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${apiUrl}/api/session/start`);
      setSessionId(response.data.session_id);
      setMessages([
        {
          id: 1,
          role: 'assistant',
          content: response.data.greeting,
          timestamp: new Date()
        }
      ]);
      setTriageComplete(false);
      setIsEmergency(false);
      setResult(null);
    } catch (error) {
      alert('Error starting session: ' + error.message);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Send message
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || !sessionId) return;

    const userMessage = input;
    setInput('');
    setLoading(true);

    try {
      // Add user message to display
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'user',
        content: userMessage,
        timestamp: new Date()
      }]);

      // Send to backend
      const response = await axios.post(`${apiUrl}/api/conversation`, {
        session_id: sessionId,
        user_message: userMessage
      });

      // Add assistant response
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'assistant',
        content: response.data.assistant_message,
        timestamp: new Date()
      }]);

      // Check if emergency
      if (response.data.is_emergency) {
        setIsEmergency(true);
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          role: 'system',
          content: '🚨 EMERGENCY DETECTED - CALL 911 IMMEDIATELY!',
          timestamp: new Date()
        }]);
      }

      // Check if triage complete
      if (!response.data.should_continue) {
        setTriageComplete(true);
        await getAdvancedAnalysis();
      }

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'system',
        content: '❌ Error: ' + error.message,
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Get advanced analysis (Grok + Gemini)
  const getAdvancedAnalysis = async () => {
    try {
      setAnalysisLoading(true);
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'system',
        content: '⏳ Generating advanced analysis with AI...',
        timestamp: new Date()
      }]);

      const response = await axios.post(
        `${apiUrl}/api/advanced-analysis/${sessionId}`
      );

      setResult(response.data);

      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'assistant',
        content: '✅ Analysis Complete! Scroll down to see detailed report.',
        timestamp: new Date()
      }]);

    } catch (error) {
      console.error('Error getting analysis:', error);
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'system',
        content: '⚠️ Could not generate advanced analysis: ' + error.message,
        timestamp: new Date()
      }]);
    } finally {
      setAnalysisLoading(false);
    }
  };

  // New assessment
  const handleNewAssessment = () => {
    setSessionId(null);
    setMessages([]);
    setTriageComplete(false);
    setIsEmergency(false);
    setResult(null);
    setInput('');
  };

  // Download report
  const downloadReport = () => {
    if (!result) return;

    const reportText = `
HEALTHMATE ADVANCED - TRIAGE ASSESSMENT REPORT
Generated: ${new Date().toLocaleString()}

URGENCY LEVEL: ${result.urgency_level.toUpperCase()}

=== GROK AI ANALYSIS ===
${result.grok_analysis}

=== FINAL GEMINI REPORT ===
${result.final_report}

=== MODELS USED ===
- Grok AI: Advanced symptom analysis
- Gemini: Professional report generation

MEDICAL DISCLAIMER:
This assessment is for triage guidance only.
It is NOT a medical diagnosis.
Always consult qualified healthcare professionals.
In emergencies, CALL 911 IMMEDIATELY.
    `;

    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(reportText));
    element.setAttribute('download', `healthmate_report_${sessionId}.txt`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="chat-interface">
      {!sessionId ? (
        <div className="start-screen">
          <div className="start-screen-content">
            <h2>Welcome to HealthMate Advanced</h2>
            <p>Get emergency medical triage assessment</p>
            <p className="features">
              Features:
              <ul>
                <li>✓ Grok AI-powered symptom analysis</li>
                <li>✓ Professional Gemini-generated reports</li>
                <li>✓ Triage-based diagnostic questions</li>
                <li>✓ Urgency classification</li>
              </ul>
            </p>
            <button
              onClick={startSession}
              disabled={loading}
              className="start-btn"
            >
              {loading ? '⏳ Starting...' : '🚀 Start Assessment'}
            </button>
          </div>
        </div>
      ) : (
        <div className="chat-active">
          {/* Messages */}
          <div className="messages-container">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message message-${msg.role}`}>
                <div className="message-content">
                  {msg.role === 'system' && <span className="system-icon">ℹ️</span>}
                  {msg.role === 'user' && <span className="user-icon">👤</span>}
                  {msg.role === 'assistant' && <span className="assistant-icon">🩺</span>}
                  <span className="message-text">{msg.content}</span>
                </div>
                <small className="message-time">
                  {msg.timestamp.toLocaleTimeString()}
                </small>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          {!triageComplete && !isEmergency && (
            <form onSubmit={sendMessage} className="input-area">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your response..."
                disabled={loading}
                className="chat-input"
                autoFocus
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="send-btn"
              >
                {loading ? '⏳' : '📤 Send'}
              </button>
            </form>
          )}

          {/* Emergency Alert */}
          {isEmergency && (
            <div className="emergency-alert">
              <h3>🚨 EMERGENCY DETECTED</h3>
              <p>CALL 911 IMMEDIATELY or go to the nearest emergency room!</p>
              <p>Do not drive if symptoms present.</p>
              <button onClick={handleNewAssessment} className="new-btn">
                Start New Assessment
              </button>
            </div>
          )}

          {/* Results Section */}
          {triageComplete && result && (
            <div className="results-section">
              <div className="urgency-badge" data-level={result.urgency_level}>
                Urgency Level: <strong>{result.urgency_level.toUpperCase()}</strong>
              </div>

              {/* Grok Analysis */}
              <div className="analysis-box">
                <h3>🤖 Grok AI Analysis</h3>
                <div className="analysis-content">
                  <pre>{result.grok_analysis}</pre>
                </div>
              </div>

              {/* Final Report */}
              <div className="report-box">
                <h3>📋 Final Gemini Report</h3>
                <div className="report-content">
                  <pre>{result.final_report}</pre>
                </div>
              </div>

              {/* Actions */}
              <div className="results-actions">
                <button
                  onClick={downloadReport}
                  className="download-btn"
                >
                  📥 Download Report
                </button>
                <button
                  onClick={handleNewAssessment}
                  className="new-btn"
                >
                  🔄 New Assessment
                </button>
              </div>
            </div>
          )}

          {/* Loading Analysis */}
          {analysisLoading && (
            <div className="loading-analysis">
              <p>⏳ Generating advanced AI analysis...</p>
              <div className="loading-spinner"></div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ChatInterface;
