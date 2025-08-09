
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const API_BASE = process.env.NODE_ENV === 'production' 
  ? 'https://your-repl-name.replit.app' 
  : 'http://0.0.0.0:5000';

// API service
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Dashboard Component
function Dashboard() {
  const [health, setHealth] = useState(null);
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    // Fetch health status
    api.get('/health').then(res => setHealth(res.data));
    
    // Fetch ESG questions
    api.get('/esg/questions').then(res => setQuestions(res.data));
  }, []);

  return (
    <div className="dashboard">
      <h1>ESG Compliance Dashboard</h1>
      
      {health && (
        <div className="health-status">
          <h2>System Status: {health.status}</h2>
          <p>Version: {health.version}</p>
          <p>Model Provider: {health.model_provider}</p>
        </div>
      )}

      <div className="esg-questions">
        <h2>ESG Assessment Questions ({questions.length})</h2>
        <div className="questions-grid">
          {questions.map((question, index) => (
            <div key={index} className="question-card">
              <h3>{question.category}</h3>
              <p>{question.question}</p>
              <small>Weight: {question.weight}</small>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Login Component
function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [fullName, setFullName] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const endpoint = isRegister ? '/auth/register' : '/auth/login';
      const data = isRegister 
        ? { email, password, full_name: fullName, company_name: companyName, industry }
        : { email, password };
      
      const response = await api.post(endpoint, data);
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        onLogin(response.data);
      }
    } catch (error) {
      alert('Authentication failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="login-form">
      <h2>{isRegister ? 'Register' : 'Login'}</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        
        {isRegister && (
          <>
            <input
              type="text"
              placeholder="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="Company Name"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
            />
            <input
              type="text"
              placeholder="Industry"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
            />
          </>
        )}
        
        <button type="submit">
          {isRegister ? 'Register' : 'Login'}
        </button>
      </form>
      
      <button onClick={() => setIsRegister(!isRegister)}>
        {isRegister ? 'Switch to Login' : 'Switch to Register'}
      </button>
    </div>
  );
}

// ESG Assessment Component
function ESGAssessment() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(null);

  useEffect(() => {
    api.get('/esg/questions').then(res => setQuestions(res.data));
  }, []);

  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: parseInt(value) }));
  };

  const submitAssessment = async () => {
    try {
      const response = await api.post('/esg/questionnaire', { answers });
      setScore(response.data);
    } catch (error) {
      alert('Assessment failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="esg-assessment">
      <h2>ESG Assessment</h2>
      
      {questions.map((question, index) => (
        <div key={index} className="question-item">
          <h3>{question.category}</h3>
          <p>{question.question}</p>
          <select 
            onChange={(e) => handleAnswerChange(index, e.target.value)}
            value={answers[index] || ''}
          >
            <option value="">Select rating</option>
            <option value="1">1 - Poor</option>
            <option value="2">2 - Fair</option>
            <option value="3">3 - Good</option>
            <option value="4">4 - Very Good</option>
            <option value="5">5 - Excellent</option>
          </select>
        </div>
      ))}
      
      <button onClick={submitAssessment} disabled={Object.keys(answers).length !== questions.length}>
        Submit Assessment
      </button>
      
      {score && (
        <div className="score-results">
          <h3>Your ESG Score: {score.overall_score}/100</h3>
          <div className="category-scores">
            <p>Environmental: {score.category_scores?.environmental || 'N/A'}</p>
            <p>Social: {score.category_scores?.social || 'N/A'}</p>
            <p>Governance: {score.category_scores?.governance || 'N/A'}</p>
          </div>
          {score.badge && <div className="badge">Badge: {score.badge}</div>}
          {score.improvement_suggestions && (
            <div className="suggestions">
              <h4>AI Suggestions:</h4>
              <ul>
                {score.improvement_suggestions.map((suggestion, idx) => (
                  <li key={idx}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Main App Component
function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      api.get('/auth/me')
        .then(res => setUser(res.data))
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-brand">
            <Link to="/">ESG Compliance Tracker</Link>
          </div>
          <div className="nav-links">
            <Link to="/">Dashboard</Link>
            <Link to="/assessment">ESG Assessment</Link>
            <button onClick={handleLogout}>Logout</button>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/assessment" element={<ESGAssessment />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
