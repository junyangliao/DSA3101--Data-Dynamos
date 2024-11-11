import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from "react-router-dom";
import './App.css';
import Login from './pages/Login';
import Modal from 'react-modal';
import Dashboard from './pages/Dashboard';
import Modules from './pages/Modules';
import Students from './pages/Students';
import Jobs from './pages/Jobs';
import Query from './pages/Query';
import Staffs from './pages/Staffs';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Dialog, DialogActions, DialogTitle, Button } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu'; // Menu icon for toggle
import DashboardIcon from '@mui/icons-material/Dashboard';
import SchoolIcon from '@mui/icons-material/School';
import PeopleIcon from '@mui/icons-material/People';
import LogoutIcon from '@mui/icons-material/Logout';
import WorkIcon from '@mui/icons-material/Work';
import SearchIcon from '@mui/icons-material/Search';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

Modal.setAppElement('#root');  // Accessibility setting for modals

function App() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const shouldShowDrawer = location.pathname !== '/';

  const openLogoutDialog = () => setIsLogoutDialogOpen(true);
  const closeLogoutDialog = () => setIsLogoutDialogOpen(false);

  // Close drawer when the route changes
  useEffect(() => {
    setIsDrawerOpen(false);
  }, [location]);

  const confirmLogout = () => {
      closeLogoutDialog();
      navigate('/'); // Redirect to login page
  };

  return (
    <div className="App">
    {shouldShowDrawer && (
      <Drawer
        anchor="left"
        open={isDrawerOpen}
        variant="permanent"
        onMouseEnter={() => setIsDrawerOpen(true)}
        onMouseLeave={() => setIsDrawerOpen(false)}
        sx={{
          display: shouldShowDrawer ? 'block' : 'none',
          width: isDrawerOpen ? 180 : 60, // Drawer width when opened/closed
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: isDrawerOpen ? 180 : 60,
            boxSizing: 'border-box',
            transition: 'width 0.3s',
            overflowX: 'hidden', // Smooth transition
            background: '#BACEC1',
          },
        }}
      >
        <div className="drawer-content">
          <List>
            <ListItem className="drawer-toggle-btn" aria-label="Toggle drawer">
              <ListItemIcon className="MuiListItemIcon-root">
                <MenuIcon />
              </ListItemIcon>
              {isDrawerOpen && <ListItemText primary="Menu" className="drawer-list-item-text" />}
            </ListItem>

            <ListItem button onClick={() => { navigate('/Dashboard'); }} className="drawer-list-item">
              <ListItemIcon className="MuiListItemIcon-root">
                <DashboardIcon />
              </ListItemIcon>
              {isDrawerOpen && <ListItemText primary="Dashboard" className="drawer-list-item-text" />} {/* Text shows only when expanded */}
            </ListItem>
            
            <ListItem button onClick={() => { navigate('/Modules'); }} className="drawer-list-item"> 
              <ListItemIcon className="MuiListItemIcon-root">
                <SchoolIcon />
              </ListItemIcon>
              {isDrawerOpen && <ListItemText primary="Modules" className="drawer-list-item-text" />}
            </ListItem>

            <ListItem button onClick={() => { navigate('/Students'); }} className="drawer-list-item">
              <ListItemIcon className="MuiListItemIcon-root">
                <PeopleIcon />
              </ListItemIcon>
              {isDrawerOpen && <ListItemText primary="Students" className="drawer-list-item-text" />}
            </ListItem>

            <ListItem button onClick={() => { navigate('/Staffs'); }} className="drawer-list-item">
              <ListItemIcon className="MuiListItemIcon-root">
                <AdminPanelSettingsIcon />
              </ListItemIcon>
              {isDrawerOpen && <ListItemText primary="Staffs" className="drawer-list-item-text" />}
            </ListItem>

            <ListItem button onClick={() => { navigate('/Jobs'); }} className="drawer-list-item">
              <ListItemIcon className="MuiListItemIcon-root">
                <WorkIcon />
              </ListItemIcon>
              {isDrawerOpen && <ListItemText primary="Jobs" className="drawer-list-item-text" />}
            </ListItem>
          
            <ListItem button onClick={() => { navigate('/Query'); }} className="drawer-list-item">
              <ListItemIcon className="MuiListItemIcon-root">
                <SearchIcon />
              </ListItemIcon>
            {isDrawerOpen && <ListItemText primary="Query" className="drawer-list-item-text" />}
          </ListItem>
          </List>

          <div style={{ flexGrow: 1 }} />
          
          <List>
            <ListItem button onClick={openLogoutDialog} className="drawer-list-item">
              <ListItemIcon className="MuiListItemIcon-root">
                <LogoutIcon />
              </ListItemIcon>
              {isDrawerOpen && <ListItemText primary="Log Out" className="drawer-list-item-text" />}
            </ListItem>
          </List>
        </div>
      </Drawer>
    )}
    <Dialog
        open={isLogoutDialogOpen}
        onClose={closeLogoutDialog}
        aria-labelledby="logout-dialog-title"
        aria-describedby="logout-dialog-description"
      >
        <DialogTitle id="logout-dialog-title">Are you sure you want to logout?</DialogTitle>
        <DialogActions>
          <Button onClick={closeLogoutDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={confirmLogout} color="primary" autoFocus>
            Logout
          </Button>
        </DialogActions>
      </Dialog>

      <div className={`login-content ${isDrawerOpen && shouldShowDrawer ? 'shifted' : ''}`}>
        <Routes>
          <Route path="/" element={<Login />} />
        </Routes>
      </div>
      <div className={`main-content ${isDrawerOpen && shouldShowDrawer ? 'shifted' : ''}`}>
        <Routes>
          <Route path="/Dashboard" element={<Dashboard />} />
          <Route path="/Modules" element={<Modules />} />
          <Route path="/Students" element={<Students />} />
          <Route path="/Staffs" element={<Staffs />} />
          <Route path="/Jobs" element={<Jobs />} />
          <Route path="/Query" element={<Query />} />
        </Routes>
      </div>
    </div>
  );
}

// Wrap App in Router to manage routing correctly
const AppWrapper = () => (
  <Router>
    <App />
  </Router>
);

export default AppWrapper;