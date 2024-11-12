import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TextField, Button, Typography, Box, Dialog, DialogActions, DialogContent, DialogTitle, CircularProgress } from '@mui/material';

const ModuleVisualizer = () => {
  const [moduleCode, setModuleCode] = useState('');
  const [error, setError] = useState(null);
  const [iframeUrl, setIframeUrl] = useState('');
  const [open, setOpen] = useState(false);
  const [isDeleteMode, setIsDeleteMode] = useState(false);
  const [progress, setProgress] = useState(0);          
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  useEffect(() => {
    fetchVisualization('CS1010S');
  }, []);

  const fetchVisualization = async (code) => {
    setIsLoading(true);
    try {
      console.log(`Fetching visualization for ${code}`);
      const response = await axios.post('http://localhost:5001/visualize-module', { module_code: code });
      const { file_url } = response.data;
      setIframeUrl(`http://localhost:5001${file_url}`);
      console.log(`Iframe URL set to: http://localhost:5001${file_url}`);
    } catch (err) {
      console.error("Error loading module visualization:", err);
      setError('Failed to load module visualization');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    
    if (selectedFile) {
      handleUpload(selectedFile);
    }
  };

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

      const response = await axios.post('http://localhost:5001/upload-csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted)
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
    module_code: '',
    title: '',
    description: '',
    module_credit: '',
    department: '',
    faculty: '',
    prerequisites: '',
    preclusions: '',
    semesters: '',
    skills: ''
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
    const parsedModuleData = {
      ...moduleData,
      prerequisites: JSON.parse(moduleData.prerequisites || "[]"),
      preclusions: JSON.parse(moduleData.preclusions || "[]"),
      semesters: JSON.parse(moduleData.semesters || "[]"),
      skills: JSON.parse(moduleData.skills || "[]")
    };

    try {
      await axios.post('http://localhost:5001/create-module', parsedModuleData);
      console.log('Module created successfully');
      setOpen(false); 
    } catch (error) {
      console.error('Error creating module:', error);
    }
  };

  const handleDeleteModule = async () => {
    try {
      await axios.post('http://localhost:5001/delete-module', { module_code: moduleData.module_code });
      console.log('Module deleted successfully');
      setOpen(false); 
    } catch (error) {
      console.error('Error deleting module:', error);
    }
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (moduleCode) {
      fetchVisualization(moduleCode);
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
          <Button
            variant="contained"
            color="secondary"
            style={{ marginRight: '10px' }}
            onClick={() => { setIsDeleteMode(true); handleClickOpen(); }}
            >
            Delete Module
          </Button>

          <Button
            variant="contained"
            color="primary"
            style={{ marginRight: '10px' }}
            onClick={() => { setIsDeleteMode(false); handleClickOpen(); }}
          >
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
      <DialogTitle>{isDeleteMode ? 'Delete Module' : 'Create New Module'}</DialogTitle>
        <DialogContent>
          <TextField
            label="Module Code"
            name="module_code"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={moduleData.moduleCode}
          />
          {!isDeleteMode && (
            <>
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
              <TextField
                label="Skills (Input in list format)"
                name="skills"
                fullWidth
                margin="dense"
                onChange={handleChange}
                value={moduleData.skills}
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
        <Button onClick={handleClose} color="secondary">
            Cancel
          </Button>
          <Button
            onClick={isDeleteMode ? handleDeleteModule : handleCreateModule}
            color={isDeleteMode ? 'error' : 'primary'}
            variant="contained"
          >
            {isDeleteMode ? 'Delete' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <form onSubmit={handleSubmit}>
        <TextField
          label="Module Code Here"
          variant="outlined"
          value={moduleCode}
          onChange={(e) => setModuleCode(e.target.value)}
          placeholder="Enter Module Code"
          fullWidth
          style={{ marginBottom: '16px' }} // Add some spacing
        />

        <Button type="submit" variant="contained" color="primary">
          Submit
        </Button>
      </form>
      
      {isLoading ? (
        <Box display="flex" justifyContent="center" alignItems="center" height="500px">
          <CircularProgress />  
          <Typography variant="body1" style={{ marginLeft: '10px' }}>Loading visualization...</Typography>
        </Box>
      ) : iframeUrl ? (
        <iframe
          src={iframeUrl}
          title="Module Visualization"
          width="100%"
          height="750px"
          frameBorder="0"
          loading="lazy"
        />
      ) : error ? (
        <Typography variant="body2" color="error" style={{ marginTop: '10px' }}>
          {error}
        </Typography>
      ) : null}
    </div>
  );
};

export default ModuleVisualizer;




