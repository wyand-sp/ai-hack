// Login.js
import React, { useState } from 'react';
import axios from 'axios';
import logo from './logo1.png';

function Login({ setUsername }) {
  const [input, setInput] = useState('');

  const handleLogin = () => {
    axios.post(`${process.env.REACT_APP_BACKEND_URL}/login`, { username: input })
      .then(() => setUsername(input))
      .catch(err => console.error(err));
  };
  const logoStyle = {
    width: '100px',
    height: 'auto',
    marginBottom: '10px',
  };
  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '10px',
    maxWidth: '300px',
    margin: '0 auto'
  };

  return (
    <div style={containerStyle}>
      <img src={logo} alt="Logo" style={logoStyle} />
      <h1>Please login</h1>
      <input
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Username"
        style={{ width: '100%', padding: '8px' }}
      />
      <button onClick={handleLogin} style={{ width: '100%', padding: '5px', backgroundColor: '#4CAF50', color: 'white', borderRadius: '4px', fontSize: '16px',cursor: 'pointer', border: 'none',}}>
        Login
      </button>
    </div>
  );
}

export default Login;