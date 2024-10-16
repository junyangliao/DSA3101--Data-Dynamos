import React, { useState } from 'react';
import axios from 'axios';

const StudentVisualizer = () => {
  const [matricNumber, setMatricNumber] = useState('');
  const [error, setError] = useState(null);
  const [iframeUrl, setIframeUrl] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Make sure to point the request to the Flask backend on port 5000
      const response = await axios.post('http://localhost:5000/visualize-student', { matric_number: matricNumber });
  
      // Create a URL from the blob response
      const { file_url } = response.data;
      setIframeUrl(`http://localhost:5000${file_url}`);  // Set the iframe URL
    } catch (err) {
      setError('Failed to load student visualization');
    }
  };

  return (
    <div>
      <h1>Student Visualizer</h1>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={matricNumber} 
          onChange={(e) => setMatricNumber(e.target.value)} 
          placeholder="Enter Student Matric Number" 
          required 
        />
        <button type="submit">Visualize</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      {iframeUrl && (
        <iframe
          src={iframeUrl}
          title="Student Visualization"
          width="100%"
          height="750px"
          frameBorder="0"
        />
      )}
    </div>
  );
};

export default StudentVisualizer;