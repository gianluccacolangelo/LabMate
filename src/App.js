import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({ name: '', email: '', interests: '', sites_of_interest: '' });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    const response = await axios.get('http://localhost:8000/');
    setUsers(response.data.users);
  };

  const handleInputChange = (e) => {
    setNewUser({ ...newUser, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await axios.post('http://localhost:8000/users/', {
      ...newUser,
      interests: newUser.interests.split(','),
      sites_of_interest: newUser.sites_of_interest.split(',')
    });
    setNewUser({ name: '', email: '', interests: '', sites_of_interest: '' });
    fetchUsers();
  };

  const runReport = async () => {
    const response = await axios.post('http://localhost:8000/run_report/');
    alert(response.data.message);
  };

  return (
    <div>
      <h1>CorrespondentAI</h1>
      <h2>Users:</h2>
      <ul>
        {users.map((user, index) => (
          <li key={index}>{user.name} ({user.email})</li>
        ))}
      </ul>
      <h2>Add User:</h2>
      <form onSubmit={handleSubmit}>
        <input name="name" value={newUser.name} onChange={handleInputChange} placeholder="Name" required />
        <input name="email" value={newUser.email} onChange={handleInputChange} placeholder="Email" required />
        <input name="interests" value={newUser.interests} onChange={handleInputChange} placeholder="Interests (comma-separated)" required />
        <input name="sites_of_interest" value={newUser.sites_of_interest} onChange={handleInputChange} placeholder="Sites of Interest (comma-separated)" required />
        <button type="submit">Add User</button>
      </form>
      <button onClick={runReport}>Run Weekly Report</button>
    </div>
  );
}

export default App;