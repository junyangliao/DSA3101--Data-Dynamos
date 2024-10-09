import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setUsernameError] = useState('');
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
  };

  return (
    <div className={'mainContainer'}>
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
        <label className="errorLabel">{emailError}</label>
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
