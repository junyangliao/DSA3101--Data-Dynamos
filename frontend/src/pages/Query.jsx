import React, { useState } from 'react';
import { Button, Typography, Box, TextField, Paper, Table, TableBody, TableCell, TableContainer, TableRow } from '@mui/material';

const QueryProcessor = () => {
  const [error, setError] = useState(null);  
  const [query, setQuery] = useState('');  
  const [response,setResponse] = useState(null);
  const [loadingQuery, setLoadingQuery] = useState(false);

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    setLoadingQuery(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:5001/process_query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      const data = await res.json()
      setResponse(data);
    } catch (err) {
      setError('Failed to get reply: ' + err.message);
    } finally {
      setLoadingQuery(false);
    }
  };

  const renderResponse = () => {
    if (!response) return null;
  
    // Check if response is a list of strings (module codes)
    if (Array.isArray(response) && typeof response[0] === 'string') {
      return (
        <Paper elevation={3} sx={{ mt: 3, p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Response :
          </Typography>
          <ul>
            {response.map((code, index) => (
              <li key={index}>{code}</li>
            ))}
          </ul>
        </Paper>
      );
    }
  
    // Check if response is a list of dictionaries (module details)
    if (Array.isArray(response) && typeof response[0] === 'object') {
      return (
        <Paper elevation={3} sx={{ mt: 3, p: 3 }}>
          {response.map((result, index) => (
            <Box key={index} sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Response {index+1}
              </Typography>
              <TableContainer>
                <Table>
                  <TableBody>
                    {Object.entries(result).map(([key, value]) => (
                      <TableRow key={key}>
                        <TableCell sx={{ fontWeight: 'bold' }}>{key}</TableCell>
                        <TableCell>{value}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          ))}
        </Paper>
      );
    }
  
    // If the response format is unexpected, show a generic message
    return (
      <Typography variant="h6" color="error" sx={{ mt: 2 }}>
        Unsupported response format
      </Typography>
    );
  };
  

  return (
    <div style={{ paddingLeft: '20px', paddingRight: '20px' }}>
      <Box
        display="flex"
        justifyContent="space-between" 
        alignItems="center"
      >
        <Typography variant="h4" gutterBottom style={{ paddingTop: '10px' }}>
          Query Bot
        </Typography>
      </Box>

      <Paper elevation={3} style={{ padding: '20px', marginBottom: '20px' }}>
        <form onSubmit={handleQuerySubmit}>
          <TextField
            label="Input Prompt (*Case sensitive) "
            variant="outlined"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., Tell me about the module DSA3101"
            required
            fullWidth
            style={{ marginBottom: '16px' }}
          />

          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loadingQuery}
          >
            {loadingQuery ? 'Getting Replies...' : 'Get Replies'}
          </Button>
        </form>

        {error && (
          <Typography variant="body1" color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}

        {renderResponse()}
      </Paper>
    </div>
  )
};

export default QueryProcessor;