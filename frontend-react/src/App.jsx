import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './components/LoginPage';
import WelcomePage from './components/WelcomePage';
import HealthCheckPage from './components/HealthCheckPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/welcome" element={<WelcomePage />} />
        <Route path="/health-check" element={<HealthCheckPage />} />
      </Routes>
    </Router>
  );
}

export default App;
