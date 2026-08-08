import React from 'react';
import logo from '../../assets/Images/logo.png'; // Adjust the path as necessary
import { Link, useNavigate } from 'react-router-dom';
import { FaBars } from 'react-icons/fa';
import './Navbar.css';

const Navbar = () => {
  const isAuthenticated = localStorage.getItem('jwtoken') ? true : false;
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear user session
    localStorage.removeItem('jwtoken');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo/App Name */}
        <Link to="/" className="navbar-logo">
          <img src={logo} alt="ScholarSeek Logo" className="logo-image" />
        </Link>

        {/* Mobile Menu Toggle */}
        <div className="menu-icon">
          <FaBars />
        </div>

        {/* Navigation Links */}
        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/" className="nav-links">
              Home
            </Link>
          </li>

          {isAuthenticated ? (
            <>
              <li className="nav-item">
                <Link to="/profile" className="nav-links">
                  Profile
                </Link>
              </li>
              <li className="nav-item">
                <button onClick={handleLogout} className="nav-links logout-btn">
                  Logout
                </button>
              </li>
            </>
          ) : (
            <li className="nav-item">
              <Link to="/login" className="nav-links">
                Login/Signup
              </Link>
            </li>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;