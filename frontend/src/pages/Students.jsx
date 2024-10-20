import React, { useState } from 'react';
import axios from 'axios';
import { TextField, Button, Typography, Box, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';

const StudentVisualizer = () => {
  const [matricNumber, setMatricNumber] = useState('');
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

      const response = await axios.post('http://localhost:5000/upload-student-csv', formData, {
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

  const [studentData, setStudentData] = useState({
    name: '',
    matric_number: '',
    nric: '',
    year: '',
    faculty: '',
    major: '',
    second_major: '',
    modules_completed: '',
    grades: ''
  });

  const handleChange = (e) => {
    setStudentData({
      ...studentData,
      [e.target.name]: e.target.value
    });
  };

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleCreateStudent = async () => {
    try {
      await axios.post('http://localhost:5000/student', studentData);
      console.log('Student created successfully');
      setOpen(false); 
    } catch (error) {
      console.error('Error creating student:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/visualize-student', { matric_number: matricNumber });
  
      const { file_url } = response.data;
      setIframeUrl(`http://localhost:5000${file_url}`);
    } catch (err) {
      setError('Failed to load student visualization');
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
          Student Info 
        </Typography>

        <Box
          display="flex"
          justifyContent="flex-end"
          alignItems="center"
        >
          <Button variant="contained" color="primary" style={{ marginRight: '10px' }} onClick={handleClickOpen}>
            Create Student
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
        <DialogTitle>Create New Student</DialogTitle>
        <DialogContent>
          <TextField
            label="Name"
            name="name"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={studentData.name}
          />
          <TextField
            label="Matric Number"
            name="matric_number"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={studentData.matric_number}
          />
          <TextField
            label="NRIC"
            name="nric"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={studentData.nric}
          />
          <TextField
            label="Year"
            name="year"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={studentData.year}
          />
          <TextField
            label="Faculty"
            name="faculty"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={studentData.faculty}
          />
          <TextField
            label="Major"
            name="major"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={studentData.major}
          />
          <TextField
            label="Second Major"
            name="second_major"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={studentData.second_major}
          />
          <TextField
            label="Modules Completed"
            name="modules_completed"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={studentData.modules_completed}
          />
          <TextField
            label="Grades"
            name="grades"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={studentData.grades}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="secondary">
            Cancel
          </Button>
          <Button onClick={handleCreateStudent} color="primary" variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      <form onSubmit={handleSubmit}>
        <TextField
          label="Student Matric Number"
          variant="outlined"
          value={matricNumber}
          onChange={(e) => setMatricNumber(e.target.value)}
          placeholder="Enter Student Matric Number"
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