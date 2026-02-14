import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './ChatInterface.css';

const ChatInterface = ({ apiUrl }) => {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [triageComplete, setTriageComplete] = useState(false);
  const [isEmergency, setIsEmergency] = useState(false);
  const [result, setResult] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load sessions from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('healthmate_sessions');
    if (saved) {
      setSessions(JSON.parse(saved));
    }
  }, []);

  // Save sessions to localStorage
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem('healthmate_sessions', JSON.stringify(sessions));
    }
  }, [sessions]);

  // Start new session
  const startSession = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${apiUrl}/api/session/start`);
      const sessionId = response.data.session_id;
      
      setCurrentSessionId(sessionId);
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

      // Add to sessions
      const newSession = {
        id: sessionId,
        timestamp: new Date().toLocaleString(),
        messages: [
          {
            id: 1,
            role: 'assistant',
            content: response.data.greeting,
            timestamp: new Date()
          }
        ],
        completed: false,
        result: null
      };
      setSessions([newSession, ...sessions]);
    } catch (error) {
      alert('Error starting session: ' + error.message);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Load previous session
  const loadSession = (sessionId) => {
    const session = sessions.find(s => s.id === sessionId);
    if (session) {
      setCurrentSessionId(sessionId);
      setMessages(session.messages);
      setTriageComplete(session.completed);
      setResult(session.result);
      setShowHistory(false);
    }
  };

  // Send message
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || !currentSessionId) return;

    const userMessage = input;
    setInput('');
    setLoading(true);

    try {
      // Add user message to display
      const newMessages = [...messages, {
        id: messages.length + 1,
        role: 'user',
        content: userMessage,
        timestamp: new Date()
      }];
      setMessages(newMessages);

      // Send to backend
      const response = await axios.post(`${apiUrl}/api/conversation`, {
        session_id: currentSessionId,
        user_message: userMessage
      });

      // Add assistant response
      const assistantMessage = {
        id: newMessages.length + 1,
        role: 'assistant',
        content: response.data.assistant_message,
        timestamp: new Date()
      };
      const updatedMessages = [...newMessages, assistantMessage];
      setMessages(updatedMessages);

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

      // Update session in history
      updateSessionHistory(currentSessionId, updatedMessages, false, null);

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

  // Get advanced analysis
  const getAdvancedAnalysis = async () => {
    try {
      setAnalysisLoading(true);
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'system',
        content: '⏳ Generating advanced analysis with Grok AI + Gemini...',
        timestamp: new Date()
      }]);

      const response = await axios.post(
        `${apiUrl}/api/advanced-analysis/${currentSessionId}`
      );

      setResult(response.data);

      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'system',
        content: '✅ Analysis Complete! See results below.',
        timestamp: new Date()
      }]);

      // Update session with result
      updateSessionHistory(currentSessionId, messages, true, response.data);

    } catch (error) {
      console.error('Error getting analysis:', error);
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'system',
        content: '⚠️ Error generating analysis: ' + error.message,
        timestamp: new Date()
      }]);
    } finally {
      setAnalysisLoading(false);
    }
  };

  // Update session in history
  const updateSessionHistory = (sessionId, msgs, completed, resultData) => {
    setSessions(sessions.map(s =>
      s.id === sessionId
        ? {
            ...s,
            messages: msgs,
            completed: completed,
            result: resultData
          }
        : s
    ));
  };

  // New assessment
  const handleNewChat = () => {
    startSession();
  };

  // Delete session
  const deleteSession = (sessionId) => {
    setSessions(sessions.filter(s => s.id !== sessionId));
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null);
      setMessages([]);
      setTriageComplete(false);
      setResult(null);
    }
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

=== SESSION INFO ===
Session ID: ${currentSessionId}
Models Used: Grok + Gemini
Timestamp: ${new Date().toLocaleString()}

MEDICAL DISCLAIMER:
This assessment is for triage guidance only.
It is NOT a medical diagnosis.
Always consult qualified healthcare professionals.
In emergencies, CALL 911 IMMEDIATELY.
    `;

    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(reportText));
    element.setAttribute('download', `healthmate_report_${currentSessionId.slice(0, 8)}.txt`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="chat-interface">
      {!currentSessionId ? (
        <div className="start-screen">
          <div className="start-screen-content">
            <h2>Welcome to HealthMate Advanced</h2>
            <p>Emergency medical triage assessment system</p>
            <div className="features">
              <ul>
                <li>✓ Grok AI-powered symptom analysis</li>
                <li>✓ Professional Gemini-generated reports</li>
                <li>✓ Triage-based diagnostic questions</li>
                <li>✓ Urgency classification</li>
                <li>✓ Chat history & previous assessments</li>
              </ul>
            </div>
            <button
              onClick={handleNewChat}
              disabled={loading}
              className="start-btn"
            >
              {loading ? '⏳ Starting...' : '🚀 Start New Assessment'}
            </button>
          </div>
        </div>
      ) : (
        <div className="chat-active">
          {/* Sidebar with Chat History */}
          <div className={`sidebar ${showHistory ? 'open' : ''}`}>
            <div className="sidebar-header">
              <h3>📋 Chat History</h3>
              <button 
                className="close-sidebar"
                onClick={() => setShowHistory(false)}
              >
                ✕
              </button>
            </div>
            
            <button
              className="new-chat-btn"
              onClick={() => {
                handleNewChat();
                setShowHistory(false);
              }}
            >
              ➕ New Assessment
            </button>

            <div className="sessions-list">
              {sessions.map((session) => (
                <div key={session.id} className="session-item">
                  <button
                    className={`session-button ${currentSessionId === session.id ? 'active' : ''}`}
                    onClick={() => loadSession(session.id)}
                  >
                    <div className="session-time">
                      {new Date(session.timestamp).toLocaleTimeString()}
                    </div>
                    <div className="session-preview">
                      {session.messages[1]?.content.substring(0, 30)}...
                    </div>
                    {session.completed && <span className="completed-badge">✓</span>}
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => deleteSession(session.id)}
                    title="Delete session"
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Main Chat Area */}
          <div className="chat-main">
            {/* Header */}
            <div className="chat-header">
              <button
                className="history-toggle"
                onClick={() => setShowHistory(!showHistory)}
              >
                ☰ History ({sessions.length})
              </button>
              <h3>HealthMate Assessment</h3>
              <button
                className="new-chat-header-btn"
                onClick={handleNewChat}
                title="Start new assessment"
              >
                ➕ New
              </button>
            </div>

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
                <button onClick={handleNewChat} className="new-btn">
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
                    onClick={handleNewChat}
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
        </div>
      )}
    </div>
  );
};

export default ChatInterface;
