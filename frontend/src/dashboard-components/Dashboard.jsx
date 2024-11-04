// import React from 'react';
// import StudentDistributionFaculty from '../dashboard-components/StudentDistributionFaculty';
// import StudentDistributionMajor from '../dashboard-components/StudentDistributionMajor';


// const Dashboard = () => {
//     return (
//         <div style={{ paddingLeft: '20px' }}>
//             <h1>Dashboard</h1>
//             <div className="charts">
                
//                 <div className="chart-container">
//                     <StudentDistributionFaculty /> {/* Replace this with another chart component */}
//                 </div>
//                 <div className="chart-container">
//                     <StudentDistributionMajor /> {/* Replace this with another chart component */}
//                 </div>
                
//             </div>
//         </div>
//     );
//   };
  
//   export default Dashboard;
import React from 'react';
import StudentDistributionFaculty from '../dashboard-components/StudentDistributionFaculty';
import StudentDistributionMajor from '../dashboard-components/StudentDistributionMajor';

const Dashboard = () => {
    return (
        <div style={{ padding: '20px' , backgroundColor: '#f7f7f7' }}>
            <h1 style={{ textAlign: 'center', fontFamily: 'Arial, sans-serif', color: '#222', marginBottom: '30px' }}>Dashboard</h1>
            <p style={{ fontSize: '14px', color: '#666', marginBottom: '10px',textAlign: 'center' }}>
                Feel free to hover around to see more details of our stats!
            </p>
            <div className="charts" style={{display: 'flex',
    justifyContent: 'space-around',
    flexWrap: 'wrap',
    gap: '20px', maxWidth: '100%', // Ensure the container doesn't exceed the viewport width
    overflow: 'hidden',marginBottom: '0px'}}>
                <div className="chart-container" style={{maxWidth: '48%',paddingBottom: '0px' }}>
                    <StudentDistributionFaculty />
                </div>
                <div className="chart-container" style={{ maxWidth: '48%',paddingBottom: '0px' }}>
                    <StudentDistributionMajor />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
