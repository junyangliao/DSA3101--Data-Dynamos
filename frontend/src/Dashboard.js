import React from 'react';
import StaffDistribution from './StaffDistribution'; // Import the component
import StudentDistributionFaculty from './StudentDistributionFaculty';
import StudentDistributionMajor from './StudentDistributionMajor';


const Dashboard = () => {
    return (
        <div className="dashboard">
            <h1>Dashboard</h1>
            <div className="charts">
                <div className="chart-container">
                    <StaffDistribution />
                </div>
                <div className="chart-container">
                    <StudentDistributionFaculty /> {/* Replace this with another chart component */}
                </div>
                <div className="chart-container">
                    <StudentDistributionMajor /> {/* Replace this with another chart component */}
                </div>
                <div className="chart-container">
                    <StaffDistribution /> {/* Replace this with another chart component */}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;