import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

// Register necessary components for Chart.js
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const StudentDistributionMajor = () => {
    const [chartData, setChartData] = useState(null); // Initialize with null
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        axios.get('http://localhost:5001/student-distribution-major')
            .then(response => {
                // Log the response data to verify it's as expected
                console.log("API Response: ", response.data);

                const majors = response.data.map(item => item.major);
                const studentCounts = response.data.map(item => item.student_count);

                // Check that the arrays are populated
                console.log("Majors: ", majors);
                console.log("Student Counts: ", studentCounts);

                // Set chart data if the response is valid
                setChartData({
                    labels: majors,
                    datasets: [
                        {
                            label: 'Student Count by Major',
                            data: studentCounts,
                            backgroundColor: 'rgba(75, 192, 192, 0.6)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1,
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
        <div className="chart">
            <h2>Student Distribution by Major</h2>
            <Bar data={chartData} />
        </div>
    );
};

export default StudentDistributionMajor;