import React, { useState } from 'react';
import { askLabelQuestion } from '../services/api';

export default function LabelChat({ analysisData }) {
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: 'Hello! I am your FoodLens AI label assistant. Ask me anything about this product\'s ingredients, allergens, additives, calories, or regulations.',
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isAsking, setIsAsking] = useState(false);

  const sampleQuestions = [
    'Does this product contain milk?',
    'What preservatives are present?',
    'Why is E211 used?',
    'How much sugar if I eat 40 g?',
    'Which allergens were detected?',
    'Is this product suitable for vegetarians?',
  ];

  const handleSend = async (queryText) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || isAsking) return;

    const userMsg = { sender: 'user', text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setIsAsking(true);

    try {
      const response = await askLabelQuestion(textToSend, analysisData);
      const aiMsg = { sender: 'ai', text: response.answer };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      const errorMsg = { sender: 'ai', text: `Sorry, could not answer right now: ${err.message}` };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <div className="card chat-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">11. Ask About This Label (Interactive Q&A)</h2>
          <span className="card-subtitle">
            Instant grounded answers based strictly on this product's extracted facts
          </span>
        </div>
        <span className="badge badge-accent">Q&A Chat</span>
      </div>

      <div className="card-body">
        {/* Suggestion Chips */}
        <div className="suggestion-chips-row">
          <span className="chips-label">Suggested Questions:</span>
          <div className="chips-list">
            {sampleQuestions.map((q, idx) => (
              <button
                key={idx}
                type="button"
                className="chip-btn"
                onClick={() => handleSend(q)}
                disabled={isAsking}
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Message Thread */}
        <div className="chat-thread">
          {messages.map((m, idx) => (
            <div key={idx} className={`chat-message ${m.sender}`}>
              <div className="chat-avatar">
                {m.sender === 'ai' ? '🤖' : '👤'}
              </div>
              <div className="chat-bubble">
                <p>{m.text}</p>
              </div>
            </div>
          ))}
          {isAsking && (
            <div className="chat-message ai">
              <div className="chat-avatar">🤖</div>
              <div className="chat-bubble typing-bubble">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </div>
            </div>
          )}
        </div>

        {/* Input Form */}
        <form
          className="chat-input-bar"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
        >
          <input
            type="text"
            placeholder="Type your question about ingredients, allergens, or nutrition..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={isAsking}
            className="chat-text-input"
          />
          <button
            type="submit"
            className="btn-primary"
            disabled={!inputQuery.trim() || isAsking}
          >
            Ask AI
          </button>
        </form>
      </div>
    </div>
  );
}
