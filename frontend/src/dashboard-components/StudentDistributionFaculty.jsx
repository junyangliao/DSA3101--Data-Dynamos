import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

// Register necessary components for Chart.js
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const StudentDistributionFaculty = () => {
    const [chartData, setChartData] = useState(null); // Initialize with null
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        axios.get('http://localhost:5001/student-distribution-faculty')
            .then(response => {
                // Log the response data to verify it's as expected
                console.log("API Response: ", response.data);

                const faculties = response.data.map(item => item.faculty);
                const studentCounts = response.data.map(item => item.student_count);

                // Check that the arrays are populated
                console.log("Faculties: ", faculties);
                console.log("Student Counts: ", studentCounts);

                // Set chart data if the response is valid
                setChartData({
                    labels: faculties,
                    datasets: [
                        { label:'',
                            data: studentCounts,
                            backgroundColor: 'rgba(75, 192, 192, 0.6)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1,
                            maxBarThickness: 15
                        }
                    ]
                });
                setLoading(false);
            })
            .catch(error => {
                console.error("Error fetching data: ", error);
                setError("Failed to load data.");
                setLoading(false);
            });
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>{error}</div>;
    }

    // Ensure chartData is defined before rendering Bar component
    if (!chartData || !chartData.labels || !chartData.datasets) {
        return <div>No data available for the chart.</div>;
    }

    return (
        <div style={{className:"chart-container",
            maxWidth: '1000px', // Adjust to control the size of each chart
            width: '100%', // Adjust the width as needed
            margin: '0 auto', // Center the chart horizontally
            padding: '15px',
            border: '1px solid #ddd',
            borderRadius: '8px',
            backgroundColor: '#fff',
            boxShadow: '0 0 10px rgba(0,0,0,0.1)'}}>
            <h2 style={{ textAlign: 'center', color: '#333', fontFamily: 'Arial, sans-serif' }}>Student Distribution by faculties</h2>
            <Bar data={chartData}
            options={{ scales:
                {x: {
                    display: false, // Hides the X-axis labels
                    grid: { display: false } // Optionally hide the X-axis grid lines
                },
                y: {
                    title: {
                        display: true,
                        text: 'Student Count',
                        color: '#666',
                        font: { family: 'Arial', size: 12 }
                        },
                    min: 0,
                    max: 500,
                    ticks: { color: '#444' },
                    grid: { color: 'rgba(200, 200, 200, 0.3)' } // Make grid lines subtle
                    }, 
                },plugins: {
                    legend: {
                        display: false // Hides the legend if not needed
                    },
                    tooltip: {
                        enabled: true, // Ensures tooltips are enabled
                        callbacks: {
                            title: (tooltipItems) => {
                                // Customize the tooltip title to show the X-axis label (major)
                                return tooltipItems[0].label;
                            },
                            label: (tooltipItem) => {
                                // Customize the tooltip label to show student count
                                return `Student Count: ${tooltipItem.raw}`;
                            }
                        }
                    }
                }
            }
        }/>
                </div>
            );
        }

export default StudentDistributionFaculty;