import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

/* #F6F4E8 , #E59560*/

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [usernameError, setUsernameError] = useState('');
  const [passwordError, setPasswordError] = useState('');

  const navigate = useNavigate();

  const handleLogin = () => {
    if (!username) {
      setUsernameError('Username is required');
      return;
    } else {
      setUsernameError('');
    }

    if (!password) {
      setPasswordError('Password is required');
      return;
    } else {
      setPasswordError('');
    }

    if (username === 'datadynamos' && password === 'DSA3101isdabest') {
      navigate('/', { replace: true });
    } else {
      setUsernameError('Invalid username');
      setPasswordError('Invalid credentials');
    }

    navigate("/students")
  };

  return (
    <div className={'mainContainer'} style={{ backgroundColor: '#BACEC1', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <div className={'titleContainer'}>
        <div>Login</div>
      </div>
      <br />
      <div className={'inputContainer'}>
        <input
          type="text"
          value={username}
          placeholder="Enter your username here"
          onChange={(ev) => setUsername(ev.target.value)}
          className={'inputBox'}
        />
        <label className="errorLabel">{usernameError}</label>
      </div>
      <br />
      <div className={'inputContainer'}>
        <input
          type="password"
          value={password}
          placeholder="Enter your password here"
          onChange={(ev) => setPassword(ev.target.value)}
          className={'inputBox'}
        />
        <label className="errorLabel">{passwordError}</label>
      </div>
      <br />
      <div className={'inputContainer'}>
        <input
          className={'inputButton'}
          type="button"
          value={'Log in'}
          onClick={handleLogin}
        />
      </div>
    </div>
  );
};

export default Login;
