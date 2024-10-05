import React, { useState, useEffect, useRef } from 'react';

function ChatWindow({ username }) {
  const ws = useRef(null);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);

  useEffect(() => {

    // Create a new WebSocket connection
    //ws.current = new WebSocket(`wss://tabcrunch.com:5001/ws/${username}`);
    ws.current = new WebSocket(`${process.env.REACT_APP_WEBSOCKET_URL}/${username}`);

    // ws.current.readyState == WebSocket.OPEN;
    // console.log("ready", ws.current.readyState);

    // ws.current.onerror = error => {
    //     console.error('WebSocket error:', error);
    //   };
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

  return (
    <div>
      <div>
        {messages.map((msg, idx) => (
          <p
            key={idx}
            style={{ textAlign: msg.sender === 'user' ? 'right' : 'left' }}
          >
            <strong>{msg.sender}:</strong> {msg.text}
          </p>
        ))}
      </div>
      <input
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Type a message..."
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default ChatWindow;
