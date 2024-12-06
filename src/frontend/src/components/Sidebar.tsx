import { useState } from "react";
import "./Sidebar.css";

const Sidebar = () => {
  // State untuk mengontrol apakah popup upload muncul
  const [showUploadOptions, setShowUploadOptions] = useState(false);

  // Fungsi untuk men-toggle state showUploadOptions
  const toggleUploadOptions = () => {
    setShowUploadOptions(!showUploadOptions);
  };

  return (
    <div className="sidebar">
      <div className="placeholder">Placeholder</div>

      <button className="sidebar-button" onClick={toggleUploadOptions}>
        Upload
      </button>

      {/* Tampilkan opsi upload jika showUploadOptions true */}
      {showUploadOptions && (
        <div className="upload-options">
          <button className="sidebar-button">Album Images</button>
          <button className="sidebar-button">Music Audios</button>
          <button className="sidebar-button">Mapper</button>
        </div>
      )}

      <button className="sidebar-button">Pictures</button>
      <button className="sidebar-button">Audios</button>
    </div>
  );
};

export default Sidebar;