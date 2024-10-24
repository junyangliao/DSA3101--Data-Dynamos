import React, { useState } from 'react';
import axios from 'axios';
import { Button, Typography, Box, CircularProgress,TextField} from '@mui/material';

const StudentVisualizer = () => {
  const [loading, setLoading] = useState(false);  // For showing loading state
  const [output, setOutput] = useState('');       // For storing backend response
  const [error, setError] = useState(null);  
  const [query, setQuery] = useState('');     // For error handling

  // Handle button click to send query to backend
  const handleQuery = async () => {
    if (!query) {
      setError('Please enter a query.');
      return;
    }
    setLoading(true);  // Start loading
    setError(null);    // Reset error
    setOutput('');     // Clear previous output
    try {
      // Send a request to your backend (replace with your actual endpoint)
      const response = await axios.get('http://localhost:5000/ai-query');  // Example endpoint
      
      // Update output with backend response
      setOutput(response.data.output);  
      setLoading(false); // Stop loading
    } catch (err) {
      setError('Failed to get output from backend.');
      setLoading(false); // Stop loading
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
      >
        {/* Input field for the user to type query */}
         <TextField
          label="Enter your query"
          variant="outlined"
          fullWidth
          value={query}
          onChange={(e) => setQuery(e.target.value)}  // Update query state
          style={{ marginBottom: '20px' }}
        />
        {/* Button to trigger query */}
        <Button
          variant="contained"
          color="primary"
          onClick={handleQuery}
          sx={{
            padding: '10px 20px',
            fontSize: '18px',
          }}
        >
          Query AI
        </Button>

        {/* Show loading spinner when fetching data */}
        {loading && <CircularProgress style={{ marginTop: '20px' }} />}

        {/* Show output from backend */}
        {output && (
          <Typography variant="body1" style={{ marginTop: '20px' }}>
            {output}
          </Typography>
        )}

        {/* Show error message if request fails */}
        {error && (
          <Typography variant="body1" style={{ color: 'red', marginTop: '20px' }}>
            {error}
          </Typography>
        )}
      </Box>
    </div>
  );
};

export default StudentVisualizer;

