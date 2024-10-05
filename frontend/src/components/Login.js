import React, { useState } from 'react';
import axios from 'axios';

function Login({ setUsername }) {
  const [input, setInput] = useState('');

  const handleLogin = () => {
    axios.post(`${process.env.REACT_APP_BACKEND_URL}/login`, { username: input })
    .then(() => setUsername(input))
    .catch(err => console.error(err));
  };

  return (
    <div>
      <h1>Please login</h1>
      <input value={input} onChange={e => setInput(e.target.value)} placeholder="Username" />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
}

export default Login;