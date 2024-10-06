import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

function UploadForm({ username }) {
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback(
    (acceptedFiles) => {
      setUploading(true);
      const file = acceptedFiles[0];
      const formData = new FormData();
      formData.append('file', file);
      formData.append('username', username);

      axios
        .post(`${process.env.REACT_APP_BACKEND_URL}/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'x-username': username,
          },
        })
        .then(() => {
          setUploading(false);
          alert('File uploaded successfully.');
        })
        .catch((err) => {
          setUploading(false);
          console.error(err);
          alert(err.message);
        });
    },
    [username]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <div>
      <div {...getRootProps()} style={styles.dropzone}>
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the files here ...</p>
        ) : (
            <p>
                Drag 'n' drop a file here, or click to select a file to upload.
            </p>
        )}
      </div>
      {uploading && <p>Uploading...</p>}
    </div>
  );
}

const styles = {
  dropzone: {
    border: '2px dashed #888',
    borderRadius: '5px',
    padding: '5px',
    textAlign: 'center',
    cursor: 'pointer',
    margin: '5px 0',
  },
};

export default UploadForm;