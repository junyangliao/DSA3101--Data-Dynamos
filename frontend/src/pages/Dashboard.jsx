import React, { useState } from 'react';
import StudentDistributionFaculty from '../dashboard-components/StudentDistributionFaculty';
import StudentDistributionMajor from '../dashboard-components/StudentDistributionMajor';
import { TextField, Button, Typography, Container, Box, Card, CardContent } from '@mui/material';


const Dashboard = () => {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState(null);
    const [error, setError] = useState(null);
  
    const handleSubmit = async (e) => {
      e.preventDefault();
  
      // Clear previous error and response
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
<<<<<<< Updated upstream
        <div style={{ paddingLeft: '20px' }}>
            <h1>Dashboard</h1>
            <div className="charts">
                
                <div className="chart-container">
                    <StudentDistributionFaculty /> {/* Replace this with another chart component */}
                </div>
                <div className="chart-container">
                    <StudentDistributionMajor /> {/* Replace this with another chart component */}
                </div>
                
            </div>
        </div>
=======
      <Container>
        <Typography variant="h4" gutterBottom>Query Processor</Typography>
  
        <Box component="form" onSubmit={handleSubmit} sx={{ mb: 4 }}>
          <TextField
            label="Enter your query"
            variant="outlined"
            fullWidth
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button variant="contained" color="primary" type="submit">Submit</Button>
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
  
        <Typography variant="h4" gutterBottom>Dashboard</Typography>
  
        <Box display="flex" gap={2} flexWrap="wrap">
          <Box flex={1}>
            <StudentDistributionFaculty />
          </Box>
          <Box flex={1}>
            <StudentDistributionMajor />
          </Box>
        </Box>
      </Container>
>>>>>>> Stashed changes
    );
  };
  
  export default Dashboard;