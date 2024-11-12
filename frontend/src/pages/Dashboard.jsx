import React, { useState } from 'react';
import axios from 'axios';
import StudentDistributionFaculty from '../components/StudentDistributionFaculty';
import StudentDistributionMajor from '../components/StudentDistributionMajor';

const Dashboard = () => {
    const [consistencyResults, setConsistencyResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const runConsistencyCheck = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.get('http://localhost:5001/api/check-consistency');
            console.log('Consistency check response:', response.data); // Debug log
            setConsistencyResults(response.data);
        } catch (err) {
            console.error('API Error:', err); // Debug log
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
            <h1>Dashboard</h1>

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
                        backgroundColor: '#2196F3', // Blue color matching the "GET RECOMMENDATIONS" button
                        color: 'white',
                        padding: '8px 16px',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: '500',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                        transition: 'background-color 0.3s'
                    }}
                    onMouseOver={e => e.target.style.backgroundColor = '#1976D2'} // Darker blue on hover
                    onMouseOut={e => e.target.style.backgroundColor = '#2196F3'}
                >
                    {loading ? 'Running Check...' : 'Run Consistency Check'}
                </button>

                {error && (
                    <div style={{
                        color: '#d32f2f',
                        backgroundColor: '#ffebee',
                        padding: '10px',
                        borderRadius: '4px',
                        marginTop: '10px'
                    }}>
                        {error}
                    </div>
                )}

                {consistencyResults && (
                    <div className="results" style={{ marginTop: '20px' }}>
                        {consistencyResults.status === 'inconsistencies_found' ? (
                            Object.entries(consistencyResults.issues).map(([entity, issues]) => (
                                <div key={entity} className="entity-section" style={{
                                    backgroundColor: '#f8f9fa',
                                    padding: '15px',
                                    borderRadius: '4px',
                                    marginBottom: '15px'
                                }}>
                                    <h3 style={{ 
                                        color: '#333',
                                        marginBottom: '10px' 
                                    }}>{entity} Issues:</h3>
                                    {issues.map((issue, index) => (
                                        <div key={index} className="issue-group" style={{
                                            backgroundColor: 'white',
                                            padding: '10px',
                                            borderRadius: '4px',
                                            marginBottom: '10px',
                                            boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                                        }}>
                                            <h4 style={{ 
                                                color: '#666',
                                                marginBottom: '8px' 
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