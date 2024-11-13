import React, { useState } from 'react';
import axios from 'axios';
import { TextField, Button, Typography, Box, Dialog, DialogActions, DialogContent, DialogTitle, CircularProgress } from '@mui/material';

const StaffVisualizer = () => {
  const [employeeName, setEmployeeName] = useState('');
  const [error, setError] = useState(null);
  const [iframeUrl, setIframeUrl] = useState('');
  const [open, setOpen] = useState(false);
  const [isDeleteMode, setIsDeleteMode] = useState(false);
  const [isModifyMode, setIsModifyMode] = useState(false); 
  const [progress, setProgress] = useState(0);          
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const fetchVisualization = async (employeeName) => {
    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:5001/visualize-staff', { employee_name: employeeName });
      const { file_url } = response.data;
      setIframeUrl(`http://localhost:5001${file_url}`);
    } catch (err) {
      setError('Failed to load staff visualization');
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

  const handleClickOpen = (mode) => {
    setIsDeleteMode(mode === 'delete');
    setIsModifyMode(mode === 'modify');
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setIsModifyMode(false);
    setStaffData({
      employee_id: '',
      employee_name: '',
      nric: '',
      dob: '',
      doj: '',
      department: '',
      modules_taught: ''
    });
  };

  const handleCreateStaff = async () => {
    try {
      await axios.post('http://localhost:5001/create-staff', staffData);
      console.log('Staff created successfully');
      setOpen(false);
      handleClose();
    } catch (error) {
      console.error('Error creating staff:', error);
    }
  };

  const handleDeleteStaff = async () => {
    try {
      await axios.post('http://localhost:5001/delete-staff', { employee_name: staffData.employee_name });
      console.log('Staff deleted successfully');
      setOpen(false);
      handleClose();
    } catch (error) {
      console.error('Error deleting staff:', error);
    }
  };

  const handleModifyStaff = async () => {
    try {
      await axios.put('http://localhost:5001/modify-staff', staffData);
      console.log('Staff modified successfully');
      setOpen(false);
      handleClose();
    } catch (error) {
      console.error('Error modifying staff:', error);
    }
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (employeeName) {
      fetchVisualization(employeeName);
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
            onClick={() => { handleClickOpen('delete'); }}
            >
            Delete Staff
          </Button>

          <Button
            variant="contained"
            color="primary"
            style={{ marginRight: '10px' }}
            onClick={() => { handleClickOpen('create'); }}
          >
            Create Staff
          </Button>

          <Button
            variant="contained"
            color="warning"
            style={{ marginRight: '10px' }}
            onClick={() => handleClickOpen('modify')}
          >
            Modify Staff
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
        <DialogTitle>
          {isDeleteMode ? 'Delete Staff' : isModifyMode ? 'Modify Staff' : 'Create New Staff'}
        </DialogTitle>
        <DialogContent>
          <TextField
                label="Employee Name"
                name="employee_name"
                fullWidth
                margin="dense"
                onChange={handleChange}
                value={staffData.employee_name}
          />
          {!isDeleteMode && (
            <>
              <TextField
                label="Employee ID"
                name="employee_id"
                fullWidth
                margin="dense"
                onChange={handleChange}
                value={staffData.employee_id}
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
            onClick={isDeleteMode ? handleDeleteStaff : isModifyMode ? handleModifyStaff : handleCreateStaff}
            color={isDeleteMode ? 'error' : 'primary'}
            variant="contained"
          >
            {isDeleteMode ? 'Delete' : isModifyMode ? 'Modify' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <form onSubmit={handleSubmit}>
        <TextField
          label="Staff Employee Name (*Case sensitive)"
          variant="outlined"
          value={employeeName}
          onChange={(e) => setEmployeeName(e.target.value)}
          placeholder="Enter Staff Employee Name"
          required
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
          title="Staff Visualization"
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

export default StaffVisualizer;