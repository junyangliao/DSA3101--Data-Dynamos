import React, { useState } from 'react';
import axios from 'axios';
import StudentDistributionFaculty from '../components/StudentDistributionFaculty';
import StudentDistributionMajor from '../components/StudentDistributionMajor';
import {Button, Typography, Box } from '@mui/material';

const Dashboard = () => {
    const [consistencyResults, setConsistencyResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);   

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

        const response = await axios.post('http://localhost:5001/upload-csv', formData, {
            headers: {
            'Content-Type': 'multipart/form-data',
            },
        });

        if (response.status === 201) {
            setError(null); 
            alert('File uploaded successfully and data integrated.');
        }
        } catch (err) {
        setError('Failed to upload file or process data.');
        }
    };

    const runConsistencyCheck = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.get('http://localhost:5001/api/check-consistency');
            console.log('Consistency check response:', response.data); 
            setConsistencyResults(response.data);
        } catch (err) {
            console.error('API Error:', err); 
            setError(
                err.response?.status === 404 
                    ? "Consistency check endpoint not found. Please check the API configuration."
                    : err.response?.data?.error || 
                      "An unexpected error occurred. Please try again later."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ paddingLeft: '20px' }}>
            <Box
                display="flex"
                justifyContent="space-between"  
                alignItems="center"
            >
                <Typography variant="h4" gutterBottom style={{ paddingTop: '10px' }}>
                Dashboard
                </Typography>

                <Box>
                <Button
                    variant="contained"
                    sx={{
                    marginRight: '20px',
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

            <div className="charts" style={{ 
                display: 'flex',
                gap: '20px',
                marginBottom: '40px',
                height: 'auto'       
            }}>
                <div className="chart-container" style={{ flex: 1 }}>
                    <StudentDistributionFaculty />
                </div>
                <div className="chart-container" style={{ flex: 1 }}>
                    <StudentDistributionMajor />
                </div>
            </div>

            <div style={{
                borderBottom: '1px solid #ddd',
                margin: '20px 0'
            }}></div>
            
            <div className="consistency-checker" style={{
                backgroundColor: 'white',
                padding: '20px',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                marginTop: '20px'
            }}>
                <h2 style={{
                    fontSize: '24px',
                    marginBottom: '20px'
                }}>Knowledge Graph Consistency Check</h2>
                
                <button 
                    onClick={runConsistencyCheck}
                    disabled={loading}
                    style={{
                        backgroundColor: '#2196F3',
                        color: 'white',
                        padding: '12px 20px', 
                        border: 'none',
                        borderRadius: '6px', 
                        cursor: 'pointer',
                        fontSize: '16px',
                        fontWeight: '600',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.1)', 
                        display: 'flex', 
                        alignItems: 'center',
                        gap: '8px',
                        transition: 'background-color 0.3s'
                    }}
                    onMouseOver={e => e.target.style.backgroundColor = '#1976D2'}
                    onMouseOut={e => e.target.style.backgroundColor = '#2196F3'}
                >
                    {loading ? (
                        <>
                            <span className="spinner" style={{
                                width: '16px',
                                height: '16px',
                                border: '2px solid #ffffff',
                                borderTop: '2px solid transparent',
                                borderRadius: '50%',
                                animation: 'spin 1s linear infinite'
                            }}></span>
                            Running Check...
                        </>
                    ) : (
                        <>
                            Run Consistency Check
                        </>
                    )}
                </button>

                {error && (
                    <div style={{
                        color: '#d32f2f',
                        backgroundColor: '#ffebee',
                        padding: '12px',
                        borderRadius: '6px',
                        marginTop: '15px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px'
                    }}>
                        <span style={{ fontSize: '18px' }}>⚠️</span>
                        {error}
                    </div>
                )}

                {consistencyResults && (
                    <div className="results" style={{ marginTop: '20px' }}>
                        {consistencyResults.status === 'inconsistencies_found' ? (
                            Object.entries(consistencyResults.issues).map(([entity, issues]) => (
                                <div key={entity} className="entity-section" style={{
                                    backgroundColor: '#f8f9fa',
                                    padding: '20px',
                                    borderRadius: '6px',
                                    marginBottom: '20px',
                                    boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                                }}>
                                    <h3 style={{ 
                                        color: '#333',
                                        marginBottom: '10px',
                                        fontSize: '18px',
                                        fontWeight: 'bold'
                                    }}>{entity} Issues:</h3>
                                    {issues.map((issue, index) => (
                                        <div key={index} className="issue-group" style={{
                                            backgroundColor: 'white',
                                            padding: '10px',
                                            borderRadius: '4px',
                                            marginBottom: '15px',
                                            boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                                        }}>
                                            <h4 style={{ 
                                                color: '#666',
                                                marginBottom: '8px',
                                                fontSize: '16px',
                                                fontWeight: '600' 
                                            }}>{issue.type}</h4>
                                            <ul style={{ 
                                                listStyleType: 'disc',
                                                paddingLeft: '20px',
                                                margin: '0'
                                            }}>
                                                {issue.details.map((detail, i) => (
                                                    <li key={i} style={{ 
                                                        color: '#666',
                                                        marginBottom: '4px'
                                                    }}>{detail}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    ))}
                                </div>
                            ))
                        ) : (
                            <div className="success-message" style={{ 
                                color: '#155724',
                                backgroundColor: '#d4edda',
                                padding: '15px',
                                borderRadius: '4px',
                                marginTop: '10px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px'
                            }}>
                                <span style={{ fontSize: '18px' }}>✅</span>
                                <span>No inconsistencies found</span>
                            </div>
                        )}
                    </div>
                )}
            </div>

        </div>
    );
};

export default Dashboard;