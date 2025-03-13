import React from 'react';
import './App.css';
import LLM from './components/LLM';
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
  const { loading } = useAuth();

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Dora AI Assistant</h1>
      </header>
      <main>
        <LLM />
      </main>
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
