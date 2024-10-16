import React, { useState } from 'react';
import axios from 'axios';

function StudentForm({ closeModal }) {
  const [name, setName] = useState('');
  const [matricNumber, setMatricNumber] = useState('');
  const [nric, setNric] = useState('');
  const [year, setYear] = useState('');
  const [major, setMajor] = useState('');
  const [second_major, setSecondMajor] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const studentData = {
      name,
      'matric number': matricNumber,
      nric,
      year,
      major,
      'second major': second_major
    };
    
    try {
      const response = await axios.post('http://localhost:5000/students', studentData);
      console.log(response.data);
      closeModal();  // Close modal after submission
    } catch (error) {
      console.error('There was an error creating the student!', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <input
        type="text"
        placeholder="Matric Number"
        value={matricNumber}
        onChange={(e) => setMatricNumber(e.target.value)}
      />
      <input
        type="text"
        placeholder="NRIC"
        value={nric}
        onChange={(e) => setNric(e.target.value)}
      />
      <input
        type="text"
        placeholder="Year"
        value={year}
        onChange={(e) => setYear(e.target.value)}
      />
      <input
        type="text"
        placeholder="Major"
        value={major}
        onChange={(e) => setMajor(e.target.value)}
      />
      <input
        type="text"
        placeholder="Second Major"
        value={second_major}
        onChange={(e) => setSecondMajor(e.target.value)}
      />
      <button type="submit">Submit</button>
    </form>
  );
}

export default StudentForm;
