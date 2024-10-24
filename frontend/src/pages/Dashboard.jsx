import React from 'react';
import StaffDistribution from '../dashboard-components/StaffDistribution'; // Import the component
import StudentDistributionFaculty from '../dashboard-components/StudentDistributionFaculty';
import StudentDistributionMajor from '../dashboard-components/StudentDistributionMajor';


const Dashboard = () => {
    return (
        <div style={{ paddingLeft: '20px' }}>
            <h1>Dashboard</h1>
            <div className="charts">
                
                <div className="chart-container">
                    <StudentDistributionFaculty /> {/* Replace this with another chart component */}
                </div>
                <div className="chart-container">
                    <StudentDistributionMajor /> {/* Replace this with another chart component */}
                </div>
                
            </div>
        </div>
    );
};

export default Dashboard;