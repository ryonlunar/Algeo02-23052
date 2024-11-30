import React from 'react';
import './Navbar.css';  // Pastikan path file CSS benar
import logo from '../assets/logo.png'; // Pastikan path logo benar

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      {/* Logo dan nama aplikasi */}
      <div className="navbar-logo">
        <img src={logo} alt="Logo" className="logo" />
        <span className="navbar-title">BRRMusic</span>
      </div>

      {/* Search bar */}
      <div className="navbar-search">
        <input type="text" placeholder="Search..." className="search-input" />
        <button className="search-button">🔍</button>
      </div>

      {/* Tombol navigasi */}
      <div className="navbar-buttons">
        <button className="nav-button">Music</button>
        <button className="nav-button">Album</button>
      </div>
    </nav>
  );
};

export default Navbar;
