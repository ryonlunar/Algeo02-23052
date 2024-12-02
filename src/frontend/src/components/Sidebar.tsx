import React from "react";
import { useLocation } from "react-router-dom";
import "./Sidebar.css";

const Sidebar = () => {
  const location = useLocation(); // Mendapatkan lokasi path saat ini

  return (
    <div className="sidebar">
      <div className="placeholder">Placeholder</div>
      <button className="sidebar-button">Upload</button>
      {location.pathname === "/" ? (
        <button className="sidebar-button">Pictures</button>
      ) : location.pathname === "/music" ? (
        <button className="sidebar-button">Audios</button>
      ) : null}
    </div>
  );
};

export default Sidebar;
