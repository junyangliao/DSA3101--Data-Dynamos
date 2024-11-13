import React, { useState } from 'react';
import axios from 'axios';
import { TextField, Button, Typography, Box, Dialog, DialogActions, DialogContent, DialogTitle, CircularProgress } from '@mui/material';

const StudentVisualizer = () => {
  const [matricNumber, setMatricNumber] = useState('');
  const [error, setError] = useState(null);
  const [iframeUrl, setIframeUrl] = useState('');
  const [open, setOpen] = useState(false);
  const [isDeleteMode, setIsDeleteMode] = useState(false);
  const [isModifyMode, setIsModifyMode] = useState(false); 
  const [progress, setProgress] = useState(0);          
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const fetchVisualization = async (matricNumber) => {
    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:5001/visualize-student', { matric_number: matricNumber });
      const { file_url } = response.data;
      setIframeUrl(`http://localhost:5001${file_url}`);
    } catch (err) {
      setError('Failed to load student visualization');
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

  const handleClickOpen = (mode) => {
    setIsDeleteMode(mode === 'delete');
    setIsModifyMode(mode === 'modify');
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setIsModifyMode(false);
    setStudentData({
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
  };

  const handleCreateStudent = async () => {
    try {
      await axios.post('http://localhost:5001/create-student', studentData);
      console.log('Student created successfully');
      setOpen(false); 
      handleClose();
    } catch (error) {
      console.error('Error creating student:', error);
    }
  };

  const handleDeleteStudent = async () => {
    try {
      await axios.post('http://localhost:5001/delete-student', { matric_number: studentData.matric_number });
      console.log('Student deleted successfully');
      setOpen(false);
      handleClose();
    } catch (error) {
      console.error('Error deleting Student:', error);
    }
  };

  const handleModifyStudent = async () => {
    try {
      await axios.put('http://localhost:5001/modify-student', studentData);
      console.log('Student modified successfully');
      setOpen(false);
      handleClose();
    } catch (error) {
      console.error('Error modifying student:', error);
    }
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (matricNumber) {
      fetchVisualization(matricNumber);
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
          <Button
            variant="contained"
            color="secondary"
            style={{ marginRight: '10px' }}
            onClick={() => { handleClickOpen('delete'); }}
            >
            Delete Student
          </Button>

          <Button
            variant="contained"
            color="primary"
            style={{ marginRight: '10px' }}
            onClick={() => { handleClickOpen('create'); }}
          >
            Create Student
          </Button>

          <Button
            variant="contained"
            color="warning"
            style={{ marginRight: '10px' }}
            onClick={() => handleClickOpen('modify')}
          >
            Modify Student
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
        <Box sx={{ width: '100%', marginTop: '10px' }}>
          <Typography variant="body2">Upload Progress: {progress}%</Typography>
        </Box>
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
        <DialogTitle>
          {isDeleteMode ? 'Delete Student' : isModifyMode ? 'Modify Student' : 'Create New Student'}
        </DialogTitle>
        <DialogContent>
          <TextField
            label="Matric Number"
            name="matric_number"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={studentData.matric_number}
          />
          {!isDeleteMode && (
            <>
              <TextField
                label="Name"
                name="name"
                fullWidth
                margin="dense"
                onChange={handleChange}
                value={studentData.name}
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
        </>
      )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="secondary">
            Cancel
          </Button>
          <Button
            onClick={isDeleteMode ? handleDeleteStudent : isModifyMode ? handleModifyStudent : handleCreateStudent}
            color={isDeleteMode ? 'error' : 'primary'}
            variant="contained"
          >
            {isDeleteMode ? 'Delete' : isModifyMode ? 'Modify' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <form onSubmit={handleSubmit}>
        <TextField
          label="Student Matric Number"
          variant="outlined"
          value={matricNumber}
          onChange={(e) => setMatricNumber(e.target.value)}
          placeholder="e.g., A0255150H"
          required
          fullWidth
          style={{ marginBottom: '16px' }} 
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
          title="Student Visualization"
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

export default StudentVisualizer;