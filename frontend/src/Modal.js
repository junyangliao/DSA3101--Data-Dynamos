import React, { useState } from 'react';

const Modal = ({ isOpen, onClose }) => {
  const [studentData, setStudentData] = useState({
    name: '',
    age: '',
    major: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setStudentData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('http://localhost:5000/students', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(studentData),
      });

      const result = await response.json();

      if (response.ok) {
        alert(result.message);  // Display success message
      } else {
        alert('Error creating student');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to connect to server.');
    }

    onClose();  // Close the modal after submission
  };

  if (!isOpen) {
    return null;  // Don't render the modal if it's not open
  }

  return (
    <div className="modal">
      <div className="modal-content">
        <h2>Create New Student</h2>
        <form onSubmit={handleSubmit}>
          <div>
            <label>Name: </label>
            <input
              type="text"
              name="name"
              value={studentData.name}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <label>Age: </label>
            <input
              type="number"
              name="age"
              value={studentData.age}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <label>Major: </label>
            <input
              type="text"
              name="major"
              value={studentData.major}
              onChange={handleChange}
              required
            />
          </div>
          <div className="modal-actions">
            <button type="submit">Submit</button>
            <button type="button" onClick={onClose}>Close</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Modal;
