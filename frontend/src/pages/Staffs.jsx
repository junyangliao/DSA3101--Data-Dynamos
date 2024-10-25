import React, { useState } from 'react';
import axios from 'axios';
import { TextField, Button, Typography, Box, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';

const StaffVisualizer = () => {
  const [employeeId, setEmployeeId] = useState('');
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

      const response = await axios.post('http://localhost:5001/upload-staffs-csv', formData, {
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

  const [staffData, setStaffData] = useState({
    employee_id: '',
    employee_name: '',
    nric: '',
    dob: '',
    doj: '',
    department: '',
    modules_taught: ''
  });

  const handleChange = (e) => {
    setStaffData({
      ...staffData,
      [e.target.name]: e.target.value
    });
  };

  const handleClickOpen = (deleteMode = false) => {
    setIsDeleteMode(deleteMode);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleCreateStaff = async () => {
    try {
      await axios.post('http://localhost:5001/staff', staffData);
      console.log('Staff created successfully');
      setOpen(false); 
    } catch (error) {
      console.error('Error creating staff:', error);
    }
  };

  const handleDeleteStaff = async () => {
    try {
      await axios.post('http://localhost:5001/delete-staff', { employee_id: staffData.employee_id });
      console.log('Staff deleted successfully');
      setOpen(false); 
    } catch (error) {
      console.error('Error deleting staff:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5001/visualize-staff', { employee_id: employeeId });
  
      const { file_url } = response.data;
      setIframeUrl(`http://localhost:5001${file_url}`);
    } catch (err) {
      setError('Failed to load staff visualization');
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
          Staff Info 
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
            onClick={() => handleClickOpen(true)}
            >
            Delete Staff
          </Button>

          <Button variant="contained" color="primary" style={{ marginRight: '10px' }} onClick={handleClickOpen}>
            Create Staff
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
        <DialogTitle>{isDeleteMode ? 'Delete Staff' : 'Create New Staff'}</DialogTitle>
        <DialogContent>
          <TextField
            label="Employee ID"
            name="employee_id"
            fullWidth
            margin="dense"
            onChange={handleChange}
            value={staffData.employee_id}
          />
          {!isDeleteMode && (
            <>
              <TextField
                label="Employee Name"
                name="employee_name"
                fullWidth
                margin="dense"
                onChange={handleChange}
                value={staffData.employee_name}
              />
              <TextField
                label="NRIC"
                name="nric"
                fullWidth
                margin="dense"
                onChange={handleChange}
                value={staffData.nric}
              />
              <TextField
                label="Date of Birth"
                name="dob"
                fullWidth
                margin="dense"
                onChange={handleChange}
                value={staffData.dob}
              />
              <TextField
                label="Date of Joining"
                name="doj"
                fullWidth
                margin="dense"
                onChange={handleChange}
                value={staffData.doj}
              />
              <TextField
                label="Department"
                name="department"
                fullWidth
                margin="dense"
                onChange={handleChange}
                value={staffData.department}
              />
              <TextField
                label="Modules Taught"
                name="modules_taught"
                fullWidth
                margin="dense"
                onChange={handleChange}
                value={staffData.modules_taught}
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="secondary">
            Cancel
          </Button>
          <Button
            onClick={isDeleteMode ? handleDeleteStaff : handleCreateStaff}
            color={isDeleteMode ? 'error' : 'primary'}
            variant="contained"
          >
            {isDeleteMode ? 'Delete' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <form onSubmit={handleSubmit}>
        <TextField
          label="Staff Employee ID"
          variant="outlined"
          value={employeeId}
          onChange={(e) => setEmployeeId(e.target.value)}
          placeholder="Enter Staff Employee ID"
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
          title="Staff Visualization"
          width="100%"
          height="750px"
          frameBorder="0"
        />
      )}
    </div>
  );
};

export default StaffVisualizer;