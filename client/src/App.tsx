import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import LLM from './components/LLM';
import LoginForm from './components/auth/LoginForm';
import SignupForm from './components/auth/SignupForm';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import { useAuth } from './context/AuthContext';

// Loading component
const Loading = () => (
  <div className="loading">
    <h2>Loading...</h2>
  </div>
);

// Main App content
const AppContent = () => {
  const { user, loading, logout } = useAuth();

  if (loading) {
    return <Loading />;
  }

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Dora AI Assistant</h1>
          {user && (
            <button onClick={handleLogout} className="auth-button">
              Logout
            </button>
          )}
        </header>
        <main>
          <Routes>
            <Route path="/login" element={user ? <Navigate to="/" /> : <LoginForm />} />
            <Route path="/signup" element={user ? <Navigate to="/" /> : <SignupForm />} />
            <Route path="/" element={
              <ProtectedRoute>
                <LLM />
              </ProtectedRoute>
            } />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
