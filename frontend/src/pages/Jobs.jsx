import React, { useState } from 'react';
import axios from 'axios';
import { TextField, Button, Typography, Box, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';

const JobVisualizer = () => {
  const [jobTitle, setJobTitle] = useState('');
  const [error, setError] = useState(null);
  const [iframeUrl, setIframeUrl] = useState('');
  const [open, setOpen] = useState(false);
  const [isDeleteMode, setIsDeleteMode] = useState(false);
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

      const response = await axios.post('http://localhost:5001/upload-jobs-csv', formData, {
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

  const [jobData, setJobData] = useState({
    job_title: '',
    skills: ''
  });

  const handleChange = (e) => {
    setJobData({
      ...jobData,
      [e.target.name]: e.target.value
    });
  };

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleCreateJob = async () => {
    try {
      await axios.post('http://localhost:5001/job', jobData);
      console.log('Job created successfully');
      setOpen(false); 
    } catch (error) {
      console.error('Error creating job:', error);
    }
  };

  const handleDeleteJob = async () => {
    try {
      await axios.post('http://localhost:5001/delete-job', { job_title: jobData.job_title });
      console.log('Job deleted successfully');
      setOpen(false); 
    } catch (error) {
      console.error('Error deleting Job:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5001/visualize-job', { job_title: jobTitle });
  
      const { file_url } = response.data;
      setIframeUrl(`http://localhost:5001${file_url}`);
    } catch (err) {
      setError('Failed to load Job visualization');
    }
  };

  return (
    <div style={{ paddingLeft: '20px', paddingRight: '20px' }}>
      <Box
        display="flex"
        justifyContent="space-between" 
        alignItems="center"
      >
        <Typography variant="h4" gutterBottom style={{ paddingTop: '10px' }}>
          Job Info 
        </Typography>

        <Box
          display="flex"
          justifyContent="flex-end"
          alignItems="center"
        >
          <Button
            variant="contained"
            color="secondary"
            style={{ marginRight: '10px' }}
            onClick={() => { setIsDeleteMode(true); handleClickOpen(); }}
            >
            Delete Job
          </Button>

          <Button
            variant="contained"
            color="primary"
            style={{ marginRight: '10px' }}
            onClick={() => { setIsDeleteMode(false); handleClickOpen(); }}
          >
            Create Job
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
      <DialogTitle>{isDeleteMode ? 'Delete Job' : 'Create New Job'}</DialogTitle>
        <DialogContent>
          <TextField
            label="Job Title"
            name="job_title"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={jobData.job_title}
          />
          {!isDeleteMode && (
            <>
              <TextField
                label="Skills"
                name="skills"
                fullWidth
                margin="dense"
                onChange={handleChange}
                value={jobData.skills}
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="secondary">
            Cancel
          </Button>
          <Button
            onClick={isDeleteMode ? handleDeleteJob : handleCreateJob}
            color={isDeleteMode ? 'error' : 'primary'}
            variant="contained"
          >
            {isDeleteMode ? 'Delete' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <form onSubmit={handleSubmit}>
        <TextField
          label="Job Title"
          variant="outlined"
          value={jobTitle}
          onChange={(e) => setJobTitle(e.target.value)}
          placeholder="Enter Job Title"
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
          title="Job Visualization"
          width="100%"
          height="750px"
          frameBorder="0"
        />
      )}
    </div>
  );
};

export default JobVisualizer;