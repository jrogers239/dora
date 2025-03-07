import React from 'react';
import './App.css';
import LLM from './components/LLM';
import Integrations from './components/Integrations';

function App() {
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
}

export default App;
