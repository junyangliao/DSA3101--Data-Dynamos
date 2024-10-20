import React, { useState } from 'react';
import axios from 'axios';
import { TextField, Button, Typography, Box, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';

const ModuleVisualizer = () => {
  const [moduleCode, setModuleCode] = useState('');
  const [error, setError] = useState(null);
  const [iframeUrl, setIframeUrl] = useState('');
  const [open, setOpen] = useState(false);
  const [progress, setProgress] = useState(0);          
  const [message, setMessage] = useState('');           

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    
    if (selectedFile) {
      handleUpload(selectedFile);
    }
  };

  // Handle CSV upload
  const handleUpload = async (selectedFile) => {
    if (!selectedFile) {
      setError("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      setProgress(0);
      setMessage('');

      const response = await axios.post('http://localhost:5000/upload-modules-csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`File upload progress: ${percentCompleted}%`);
        }
      });

      if (response.status === 201) {
        setError(null); 
        alert('File uploaded successfully and data integrated.');
      }
    } catch (err) {
      setError('Failed to upload file or process data.');
    }
  };

  const [moduleData, setModuleData] = useState({
  });

  const handleChange = (e) => {
    setModuleData({
      ...moduleData,
      [e.target.name]: e.target.value
    });
  };

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleCreateModule = async () => {
    try {
      await axios.post('http://localhost:5000/module', moduleData);
      console.log('Module created successfully');
      setOpen(false); 
    } catch (error) {
      console.error('Error creating module:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Make sure to point the request to the Flask backend on port 5000
      const response = await axios.post('http://localhost:5000/visualize-module', { module_code: moduleCode });
  
      // Create a URL from the blob response
      const { file_url } = response.data;
      setIframeUrl(`http://localhost:5000${file_url}`);  // Set the iframe URL
    } catch (err) {
      setError('Failed to load module visualization');
    }
  };

  return (
    <div style={{ paddingLeft: '20px', paddingRight: '20px' }}>
      <Box
        display="flex"
        justifyContent="space-between"  // Space between title and buttons
        alignItems="center"
      >
        <Typography variant="h4" gutterBottom style={{ paddingTop: '10px' }}>
          Module Info 
        </Typography>

        <Box>
          <Button variant="contained" color="primary" style={{ marginRight: '10px' }} onClick={handleClickOpen}>
            Create Module
          </Button>

          <Button
            variant="contained"
            sx={{
              backgroundColor: 'green', 
              color: 'white',            
              '&:hover': {
                backgroundColor: 'darkgreen',
              },
            }}
            component="label"  
          >
            Upload CSV
            <input type="file" hidden onChange={handleFileChange} />
          </Button>
        </Box>
      </Box>

      {progress > 0 && (
        <Typography variant="body2" style={{ marginTop: '10px' }}>
          Upload Progress: {progress}%
        </Typography>
      )}

      {message && (
        <Typography variant="body2" style={{ marginTop: '10px', color: 'green' }}>
          {message}
        </Typography>
      )}
      {error && (
        <Typography variant="body2" style={{ marginTop: '10px', color: 'red' }}>
          {error}
        </Typography>
      )}

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Create New Module</DialogTitle>
        <DialogContent>
          <TextField
            label="Module Code"
            name="module_code"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={moduleData.moduleCode}
          />
          <TextField
            label="Title"
            name="title"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={moduleData.title}
          />
          <TextField
            label="Description"
            name="description"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={moduleData.description}
          />
          <TextField
            label="Module Credit"
            name="module_credit"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={moduleData.moduleCredit}
          />
          <TextField
            label="Department"
            name="department"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={moduleData.department}
          />
          <TextField
            label="Faculty"
            name="faculty"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={moduleData.faculty}
          />
          <TextField
            label="Prerequisites (Input in nested list format)"
            name="prerequisites"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={moduleData.prerequisites}
          />
          <TextField
            label="Preclusions (Input in list format)"
            name="preclusions"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={moduleData.preclusions}
          />
          <TextField
            label="Semesters (Input in list format)"
            name="semesters"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={moduleData.semesters}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="secondary">
            Cancel
          </Button>
          <Button onClick={handleCreateModule} color="primary" variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Form with Material UI TextField and Button */}
      <form onSubmit={handleSubmit}>
        <TextField
          label="Module Code Here"
          variant="outlined"
          value={moduleCode}
          onChange={(e) => setModuleCode(e.target.value)}
          placeholder="Enter Module Code"
          required
          fullWidth
          style={{ marginBottom: '16px' }} // Add some spacing
        />

        <Button type="submit" variant="contained" color="primary">
          Submit
        </Button>
      </form>
      
      {iframeUrl && (
        <iframe
          src={iframeUrl}
          title="Module Visualization"
          width="100%"
          height="750px"
          frameBorder="0"
        />
      )}
    </div>
  );
};

export default ModuleVisualizer;




