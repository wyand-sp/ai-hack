
import React, { useState } from 'react';
import Login from './components/Login';
import ChatWindow from './components/ChatWindow';
import UploadForm from './components/UploadForm';

function App() {
  const [username, setUsername] = useState(null);

  return (
    <div>
      {username ? (
        <div>
        <ChatWindow username={username} />
        </div>
      ) : (
        <Login setUsername={setUsername} />
      )}
    </div>
  );
}

export default App;
