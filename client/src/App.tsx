import React, { useState } from 'react';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const generateText = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/generate', {  // Added /generate endpoint
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          max_length: 100
        })
      });
      
      const data = await response.json();
      setResult(data.generated_text);
    } catch (error) {
      setResult(`Error: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>GPT-2 Text Generator</h1>
      </header>
      <main>
        <textarea 
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt here..."
        />
        <button onClick={generateText} disabled={isLoading}>
          {isLoading ? 'Generating...' : 'Generate'}
        </button>
        <div className="result">
          {result}
        </div>
      </main>
    </div>
  );
}

export default App;