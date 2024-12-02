import React, { useState } from "react";
import { Link } from "react-router-dom"; // Import Link untuk routing
import "./Navbar.css";  
import logo from "../assets/logo.png"; 

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isSearchVisible, setIsSearchVisible] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    setIsSearchVisible(!isSearchVisible);
  };

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <img src={logo} alt="Logo" className="logo" />
        <span className="navbar-title">BARMusic</span>
      </div>

      <button className="hamburger" onClick={toggleMenu}>
        ☰
      </button>

      <div className={`navbar-search ${isSearchVisible ? "show" : ""}`}>
        <input type="text" placeholder="Search..." className="search-input" />
        <button className="search-button">🔍</button>
      </div>

      <div className={`navbar-buttons ${isMenuOpen ? "show" : ""}`}>
        <Link to="/" className="nav-link">
          <button className="nav-button">Album</button>
        </Link>
        <Link to="/music" className="nav-link">
          <button className="nav-button">Music</button>
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
