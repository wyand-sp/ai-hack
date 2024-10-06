
import React, { useState } from 'react';
import Login from './components/Login';
import ChatWindow from './components/ChatWindow';
import UploadForm from './components/UploadForm';

function App() {
    const [username, setUsername] = useState(null);
    const [showUploadForm, setShowUploadForm] = useState(false);

    const toggleUploadForm = () => {
      setShowUploadForm(prevState => !prevState);
    };

    return (
      <div style={styles.container}>
        {username ? (
          <div style={styles.loggedInContainer}>
            <button style={styles.toggleButton} onClick={toggleUploadForm}>
              {showUploadForm ? 'X' : 'Upload files?'}
            </button>

            {showUploadForm && <UploadForm username={username} />}

            <ChatWindow username={username} />
          </div>
        ) : (
          <Login setUsername={setUsername} />
        )}
      </div>
    );
  }

  const styles = {
    container: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      fontFamily: 'Arial, sans-serif',
    },
    loggedInContainer: {
      textAlign: 'center',
    },
    toggleButton: {
      padding: '5px 5px',
      backgroundColor: '#4CAF50',
      color: '#fff',
      border: 'none',
      borderRadius: '5px',
      cursor: 'pointer',
    }
  };


export default App;
