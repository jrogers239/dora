import React, { useState, useRef, useEffect } from 'react';
import '../css/LLM.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBomb, faHippo, faPaperPlane } from '@fortawesome/free-solid-svg-icons';

interface Message {
    type: 'user' | 'dora';
    content: string;
}

const LLM: React.FC = () => {
    const [prompt, setPrompt] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const chatHistoryRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (chatHistoryRef.current) {
            chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
        }
    }, [messages]);

    const generateText = async () => {
        if (!prompt.trim()) return;

        const userMessage: Message = { type: 'user', content: prompt };
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
        setPrompt('');
        
        if (textareaRef.current) {
            textareaRef.current.style.height = '36px';
            textareaRef.current.focus();
        }

        try {
            const response = await fetch('http://localhost:8000/generate', {
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
            const doraMessage: Message = { type: 'dora', content: data.generated_text };
            setMessages(prev => [...prev, doraMessage]);
        } catch (error) {
            const errorMessage: Message = { type: 'dora', content: `Error: ${error}` };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        generateText();
    };

    const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            generateText();
        }
    };

    const handleTextAreaInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const textarea = e.target;
        setPrompt(textarea.value);
        
        // Reset height to get accurate scrollHeight
        textarea.style.height = '36px';
        
        // Only adjust height if content requires more space
        if (textarea.scrollHeight > 36) {
            const newHeight = Math.min(textarea.scrollHeight, 200);
            textarea.style.height = `${newHeight}px`;
        }
    };

    return (
        <div className="llm-container">
            <h1>Dora AI Assistant</h1>
            <div className="chat-history" ref={chatHistoryRef}>
                {messages.map((message, index) => (
                    <div key={index} className={`message-row ${message.type}`}>
                        {message.type === 'user' ? (
                            <FontAwesomeIcon icon={faBomb} className="avatar" />
                        ) : (
                            <FontAwesomeIcon icon={faHippo} className="avatar" />
                        )}
                        <div className="bubble-container">
                            <div className="message-bubble">
                                {message.content}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
            <form className="input-form" onSubmit={handleSubmit}>
                <textarea
                    ref={textareaRef}
                    value={prompt}
                    onChange={handleTextAreaInput}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                />
                <button type="submit" className="send-button">
                    <FontAwesomeIcon icon={faPaperPlane} />
                </button>
            </form>
        </div>
    );
};

export default LLM;
