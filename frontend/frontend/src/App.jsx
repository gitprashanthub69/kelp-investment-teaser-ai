import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-brand-dark text-slate-100 font-sans selection:bg-brand-primary selection:text-white">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Auth type="login" />} />
          <Route path="/signup" element={<Auth type="signup" />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
