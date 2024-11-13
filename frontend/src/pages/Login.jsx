import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Paper, TextField, Button, Typography } from '@mui/material';
import logo from '../logo.svg';
import backgroundImage from '../components/background.jpg'

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

    if (username === 'data dynamos' && password === 'DSA3101isdabest') {
      navigate('/dashboard', { replace: true });
    } else {
      setUsernameError('Invalid username');
      setPasswordError('Invalid credentials');
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleLogin();
    }
  }

  return (
    <Box
      sx={{
        backgroundImage: `url(${backgroundImage})`,
        backgroundSize: 'cover',
        height: '100vh',
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
        padding: 4,
        position: 'relative',
      }}
    >
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          padding: 4,
        }}
      >
        <Paper
          sx={{
            padding: 4,
            backgroundColor: 'rgba(255, 255, 255, 0.9)', // White background with transparency
            textAlign: 'center',
          }}
          elevation={3}
        >
          <Box sx={{ mb: 3 }}>
            <img src={logo} alt="Logo" style={{ width: '200px' }} />
          </Box>
          <Typography variant="h4" color="secondary" sx={{ fontWeight: 'bold' }}>
            Study with Purpose, Major in Confidence.
          </Typography>
        </Paper>
      </Box>

      <Box
        sx={{
          flex: 0.4,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#ffffff',
          padding: 4,
          borderRadius: 2,
          boxShadow: 3,
        }}
      >
        <Typography
          variant="h4"
          sx={{
            mb: 2,
            color: 'primary.main',
            fontWeight: 'bold',
            fontFamily: 'Roboto, sans-serif',
            letterSpacing: 1.5,
          }}
        >
          Welcome Back!
        </Typography>
        <Box component="form" noValidate autoComplete="off" sx={{ width: '100%' }}>
          <TextField
            label="Username"
            variant="outlined"
            fullWidth
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyDown={handleKeyDown}
            error={!!usernameError}
            helperText={usernameError}
            sx={{ mb: 2 }}
          />
          <TextField
            label="Password"
            type="password"
            variant="outlined"
            fullWidth
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={handleKeyDown}
            error={!!passwordError}
            helperText={passwordError}
            sx={{ mb: 3 }}
          />
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={handleLogin}
            sx={{ fontSize: '1rem', padding: '10px' }}
          >
            Log in
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default Login;