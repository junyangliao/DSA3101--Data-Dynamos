import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../logo.svg';
import backgroundImage from '../background.jpg'

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

    navigate("/dashboard")
  };

  return (
    <div className="mainContainer" style={styles.mainContainer}>
      {/* Blurred Background */}
      <div className="backgroundBlur" style={styles.backgroundBlur}></div>
      <div class="rightContainer" style = {styles.rightContainer}>
        <div className="logoContainer" >
          <img src={logo} alt="Logo" style={styles.logo} />
        </div>
        <div className="sloganContainer">
        <h1>Study with Purpose, Major in Confidence.</h1>
        </div>
      </div>
      <div class="leftContainer"style = {styles.leftContainer}>
      <div className="titleContainer" style={styles.titleContainer}>
        <p>Login</p>
        </div>
        <div className="inputContainer">
        <input
          type="text"
          value={username}
          placeholder="Enter your username here"
          onChange={(ev) => setUsername(ev.target.value)}
          className="inputBox"
        />
        <label className="errorLabel">{usernameError}</label>
      </div>
      <br />
      <div className="inputContainer">
        <input
          type="password"
          value={password}
          placeholder="Enter your password here"
          onChange={(ev) => setPassword(ev.target.value)}
          className="inputBox"
        />
        <label className="errorLabel">{passwordError}</label>
      </div>
      <br />
      <div className="inputContainer">
        <input
          className="inputButton"
          type="button"
          value="Log in"
          onClick={handleLogin}
        />
      </div>
      </div>
    </div>
    
  );
};

export default Login;

const styles = {
  mainContainer: {
    backgroundColor: '#F6F4E8',
    height: '100vh',
    display: 'flex',
    justifyContent: 'space-between',
    padding: '50px',
    flexDirection: 'row' 
    },  backgroundBlur: {
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundImage: `url(${backgroundImage})`, // Add your image path
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      filter: 'blur(8px)', // Apply blur effect
      zIndex: -1, // Send it behind the content
    }, leftContainer: {
      flex: 0.3,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      paddingLeft: '50px',
      backgroundColor: '#FFFFFF'
    },
    rightContainer: {
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      paddingRight: '50px'
    }, logoContainer: {
    alignSelf: 'flex-end',
    marginRight: '20px',
    },logo: {
    width: '300px',
    marginRight: '20px',
    alignSelf: 'flex-end'
  },sloganContainer: {
    marginLeft: '20px',
  },
  slogan: {
    fontSize: '24px',
    color: '#E59560',
    textAlign: 'left',
  },titleContainer: {
    marginBottom: '15px',
  }
}