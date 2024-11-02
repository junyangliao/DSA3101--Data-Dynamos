import React, { useState } from 'react';
import axios from 'axios';
import { TextField, Button, Typography, Box, Dialog, DialogActions, DialogContent, DialogTitle, Divider, Paper, Chip, List, ListItem, ListItemText, Alert, Skeleton } from '@mui/material';

const RecommendationResults = ({ data }) => {
  if (!data) return null;

  // Add scroll handler function
  const scrollToSkill = (skillName) => {
    const element = document.getElementById(`skill-${skillName.replace(/\s+/g, '-')}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <Paper elevation={3} sx={{ mt: 3, p: 3 }}>
      {data.success ? (
        <>
          <Typography variant="h5" gutterBottom>
            Job: {data.job.title}
          </Typography>

          <Box sx={{ my: 2 }}>
            <Typography variant="h6" gutterBottom>
              Required Skills:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {data.job.skills.map((skill) => (
                <Chip 
                  key={skill} 
                  label={skill} 
                  color="primary"
                  onClick={() => scrollToSkill(skill)}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </Box>

          {data.student.matricNumber && (
            <Typography variant="subtitle1" color="text.secondary" gutterBottom>
              Recommendations for: {data.student.matricNumber}
            </Typography>
          )}

          <Divider sx={{ my: 3 }} />

          {Object.entries(data.skillBreakdown).map(([skill, breakdown]) => (
            <Paper 
              key={skill} 
              id={`skill-${skill.replace(/\s+/g, '-')}`}
              sx={{ mb: 2, p: 2, backgroundColor: '#f5f5f5' }}
            >
              <Typography variant="h6" color="primary" gutterBottom>
                {skill}
              </Typography>

              {breakdown.completed.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" color="success.main">
                    Completed Modules:
                  </Typography>
                  <List dense>
                    {breakdown.completed.map((module) => (
                      <ListItem key={module.code}>
                        <ListItemText
                          primary={`${module.code}: ${module.title}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {breakdown.recommended.length > 0 && (
                <Box>
                  <Typography variant="subtitle1" color="info.main">
                    {breakdown.completed.length > 0 
                      ? 'For further learning:' 
                      : 'Recommended Modules:'}
                  </Typography>
                  <List dense>
                    {breakdown.recommended.map((module) => (
                      <ListItem key={module.code}>
                        <ListItemText
                          primary={`${module.code}: ${module.title}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {breakdown.recommended.length === 0 && 
               breakdown.completed.length === 0 && (
                <Alert severity="info">
                  No modules found for this skill
                </Alert>
              )}
            </Paper>
          ))}
        </>
      ) : (
        <Alert severity="error">{data.error}</Alert>
      )}
    </Paper>
  );
};

const LoadingSkeleton = () => (
  <Paper elevation={3} sx={{ mt: 3, p: 3 }}>
    <Skeleton variant="text" width={300} height={40} sx={{ mb: 2 }} />
    
    <Typography variant="h6" gutterBottom>
      Required Skills:
    </Typography>
    <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
      {[1, 2, 3, 4, 5].map((i) => (
        <Skeleton key={i} variant="rounded" width={100} height={32} />
      ))}
    </Box>
    
    {[1, 2, 3].map((section) => (
      <Paper key={section} sx={{ mb: 2, p: 2, backgroundColor: '#f5f5f5' }}>
        <Skeleton variant="text" width={150} height={32} sx={{ mb: 2 }} />
        
        {[1, 2].map((module) => (
          <Box key={module} sx={{ mb: 1 }}>
            <Skeleton variant="text" width="90%" height={24} />
          </Box>
        ))}
      </Paper>
    ))}
  </Paper>
);

const JobVisualizer = () => {
  const [error, setError] = useState(null);
  const [open, setOpen] = useState(false);
  const [isDeleteMode, setIsDeleteMode] = useState(false);
  const [jobDescription, setJobDescription] = useState('');
  const [matricNumber, setMatricNumber] = useState('');
  const [recommendations, setRecommendations] = useState(null);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

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
      const response = await axios.post('http://localhost:5001/upload-jobs-csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
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

  const handleRecommendationSubmit = async (e) => {
    e.preventDefault();
    setLoadingRecommendations(true);
    setError(null);
    try {
      const response = await axios.post('http://localhost:5001/api/job-recommendations', {
        jobDescription,
        matricNumber: matricNumber || undefined
      });
      setRecommendations(response.data.recommendations);
    } catch (err) {
      setError('Failed to get job recommendations: ' + err.message);
    } finally {
      setLoadingRecommendations(false);
    }
  };

  return (
    <div style={{ paddingLeft: '20px', paddingRight: '20px' }}>
      {error && <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>}
      <Box
        display="flex"
        justifyContent="space-between" 
        alignItems="center"
      >
        <Typography variant="h4" gutterBottom style={{ paddingTop: '10px' }}>
          Job Recommendations
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

      <Paper elevation={3} style={{ padding: '20px', marginBottom: '20px' }}>
        <form onSubmit={handleRecommendationSubmit}>
          <TextField
            label="Job Description"
            variant="outlined"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="e.g., data scientist"
            required
            fullWidth
            style={{ marginBottom: '16px' }}
          />

          <TextField
            label="Matric Number (Optional)"
            variant="outlined"
            value={matricNumber}
            onChange={(e) => setMatricNumber(e.target.value)}
            placeholder="e.g., A0255150H"
            fullWidth
            style={{ marginBottom: '16px' }}
          />

          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loadingRecommendations}
          >
            {loadingRecommendations ? 'Getting Recommendations...' : 'Get Recommendations'}
          </Button>
        </form>

        {loadingRecommendations ? (
          <LoadingSkeleton />
        ) : recommendations ? (
          <RecommendationResults data={recommendations} />
        ) : null}

      </Paper>
      
    </div>
  );
};

export default JobVisualizer;