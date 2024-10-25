import React, { useState } from 'react';
import { Button, Typography, Box, CircularProgress,TextField, Container, Card, CardContent} from '@mui/material';

const QueryProcessor = () => {
  const [loading, setLoading] = useState(false);  // For showing loading state     
  const [error, setError] = useState(null);  
  const [query, setQuery] = useState('');     // For error handling
  const [response,setResponse] = useState(null);

  // Handle button click to send query to backend
  const handleQuery = async (e) => {
    e.preventDefault();

    setLoading(true);  
    setError(null);    
    setResponse(null);    
    try {
      const res = await fetch('http://localhost:5001/process_query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Something went wrong');
      }
      
        // Set the response from the backend
        setResponse(data);
      } catch (err) {
        // Set the error message
        setError(err.message);
      }
  };

  return (
    <Container>
        <Typography variant="h4" gutterBottom>Query Processor</Typography>

        <Box component="form" onSubmit={handleQuery} sx={{ mb: 4 }}>
          <TextField
            label="Enter your query"
            variant="outlined"
            fullWidth
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button variant="contained" color="primary" type="submit">Query AI</Button>
        </Box>

        {error && <Typography color="error">{error}</Typography>}

        {response && (
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h5">Response</Typography>
              <Box sx={{
                whiteSpace: 'normal',       // Ensure normal wrapping
                wordWrap: 'break-word',     // Break long words if necessary
                maxHeight: '300px',         // Set a maximum height for the box
                overflowY: 'auto',          // Vertical scrolling if content exceeds maxHeight
                backgroundColor: '#f4f4f4', // Optional: better readability
                padding: '10px',
                borderRadius: '4px'
              }}>
                <pre>{JSON.stringify(response, null, 2)}</pre>
              </Box>
            </CardContent>
          </Card>
        )}
    </Container>
  )
};

export default QueryProcessor;

