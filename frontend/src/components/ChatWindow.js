// ChatWindow.js
import React, { useState, useEffect, useRef } from 'react';

function ChatWindow({ username }) {
  const ws = useRef(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    ws.current = new WebSocket(`${process.env.REACT_APP_WEBSOCKET_URL}/${username}`);

    ws.current.onopen = () => {
      console.log('WebSocket connection established');
    };

    ws.current.onmessage = event => {
      setMessages(prev => [...prev, { sender: 'bot', text: event.data }]);
    };

    ws.current.onclose = () => {
      console.log('WebSocket connection closed');
    };

    ws.current.onerror = error => {
      console.error('WebSocket error:', error);
    };

    // Cleanup function to close the WebSocket when the component unmounts or username changes
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [username]);

  // Effect to scroll to the bottom whenever messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Auto-focus the input field on component mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const sendMessage = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(input);
      setMessages(prev => [...prev, { sender: 'user', text: input }]);
      setInput('');
    } else {
      console.error('WebSocket is not open. Ready state:', ws.current.readyState);
      alert('Unable to send message. WebSocket connection is not open.');
    }
  };

  // Inline Styles
  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    height: '80vh',
    width: '400px',
    border: '1px solid #ccc',
    borderRadius: '8px',
    padding: '16px',
    boxSizing: 'border-box',
    margin: '20px auto',
    backgroundColor: '#f9f9f9',
  };

  const messagesContainerStyle = {
    flex: 1,
    overflowY: 'auto',
    marginBottom: '16px',
    padding: '8px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    backgroundColor: '#fff',
  };


    const messageStyle = sender => ({
        textAlign: sender === 'user' ? 'right' : 'left',
        margin: '8px 0',
        padding: '8px',
        borderRadius: '4px',
        backgroundColor: sender === 'user' ? '#dcf8c6' : '#ececec',
        display: 'block',
        maxWidth: '100%',
        wordBreak: 'break-word',
    });

  const inputStyle = {
    width: '100%',
    padding: '10px',
    boxSizing: 'border-box',
    marginBottom: '8px',
    border: '1px solid #ccc',
    borderRadius: '4px',
    fontSize: '16px',
  };

  const buttonStyle = {
    width: '100%',
    padding: '10px',
    backgroundColor: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  };

  const buttonHoverStyle = {
    backgroundColor: '#45a049',
  };
  const displayNames = {
    bot: 'External Brain',
    user: 'You',
  };

  return (
    <div style={containerStyle}>
      <div style={messagesContainerStyle}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={messageStyle(msg.sender)}
            dangerouslySetInnerHTML={{
              __html: `<strong>${displayNames[msg.sender]}:</strong><br> ${msg.text}`,
            }}
          />
        ))}
        <div ref={messagesEndRef} /> {/* Dummy div to scroll into view */}
      </div>
      <input
        type="text"
        ref={inputRef}
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Look for..."
        style={inputStyle}
        onKeyPress={e => {
          if (e.key === 'Enter' && input.trim()) {
            sendMessage();
          }
        }}
      />
      <button
        onClick={sendMessage}
        style={buttonStyle}
        onMouseOver={e => (e.currentTarget.style.backgroundColor = buttonHoverStyle.backgroundColor)}
        onMouseOut={e => (e.currentTarget.style.backgroundColor = buttonStyle.backgroundColor)}
        disabled={!input.trim()}
        aria-label="Send message"
      >
        Send
      </button>
    </div>
  );
}

export default ChatWindow;