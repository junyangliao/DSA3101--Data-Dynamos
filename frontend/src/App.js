import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import './App.css';
import Login from './Login';
import Modal from 'react-modal';
import Home from './Home';
import Dashboard from './Dashboard';
import StudentForm from './StudentForm';  // Import the StudentForm component

Modal.setAppElement('#root');  // Accessibility setting for modals

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Function to open modal
  const openModal = () => setIsModalOpen(true);

  // Function to close modal
  const closeModal = () => setIsModalOpen(false);

  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/" element= {<Home />} />
          <Route path="/Login" element={<Login />} />
          <Route path="/Dashboard" element = {<Dashboard />} />
          <Route
            path="/students"
            element={
              <div>
                <button onClick={openModal}>Open Pop-Up Box</button>
                
                <Modal
                  isOpen={isModalOpen}
                  onRequestClose={closeModal}
                  contentLabel="Student Creation"
                  style={{
                    content: {
                      top: '50%',
                      left: '50%',
                      right: 'auto',
                      bottom: 'auto',
                      marginRight: '-50%',
                      transform: 'translate(-50%, -50%)',
                    },
                  }}
                >
                  <h2>Create Student</h2>

                  {/* Render the StudentForm component here */}
                  <StudentForm closeModal={closeModal} />

                  <button onClick={closeModal}>Close</button>
                </Modal>
              </div>
            }
          />
        </Routes>
      </Router>
    </div>
  );
}

export default App;


