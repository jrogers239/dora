import React from 'react';
import './App.css';
import LLM from './components/LLM';
import Auth from './components/Auth/Auth';
import { AuthProvider, useAuth } from './components/Auth/AuthContext';

// Loading component
const Loading = () => (
  <div className="loading">
    <h2>Loading...</h2>
  </div>
);

// Main App content
const AppContent = () => {
  const { loading, user } = useAuth();

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="App">
      {user ? (
        <LLM />
      ) : (
        <Auth />
      )}
    </div>
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
