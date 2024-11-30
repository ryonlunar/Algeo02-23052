import React, { useState } from "react";
import "./Navbar.css";  // Pastikan path file CSS benar
import logo from "../assets/logo.png"; // Pastikan path logo benar

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false); // State untuk menu
  const [isSearchVisible, setIsSearchVisible] = useState(false); // State untuk search bar

  // Fungsi untuk toggle menu dan search bar
  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    setIsSearchVisible(!isSearchVisible); // Toggle search bar bersamaan dengan menu
  };

  return (
    <nav className="navbar">
      {/* Logo dan nama aplikasi */}
      <div className="navbar-logo">
        <img src={logo} alt="Logo" className="logo" />
        <span className="navbar-title">BRRMusic</span>
      </div>

      {/* Tombol hamburger */}
      <button className="hamburger" onClick={toggleMenu}>
        ☰
      </button>

      {/* Search bar */}
      <div className={`navbar-search ${isSearchVisible ? "show" : ""}`}>
        <input type="text" placeholder="Search..." className="search-input" />
        <button className="search-button">🔍</button>
      </div>

      {/* Tombol navigasi */}
      <div className={`navbar-buttons ${isMenuOpen ? "show" : ""}`}>
        <button className="nav-button">Album</button>
        <button className="nav-button">Music</button>
      </div>
    </nav>
  );
};

export default Navbar;
