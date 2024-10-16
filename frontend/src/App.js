import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import './App.css';
import Login from './pages/Login';
import Modal from 'react-modal';
import Home from './Home';
import Dashboard from './pages/Dashboard';
import Modules from './pages/Modules';
import Students from './pages/Students';

Modal.setAppElement('#root');  // Accessibility setting for modals

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/" element= {<Home />} />
          <Route path="/Login" element={<Login />} />
          <Route path="/Dashboard" element = {<Dashboard />} />
          <Route path="/Modules" element = {<Modules />} />
          <Route path="/Students" element = {<Students />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;


