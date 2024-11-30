import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";  // Pastikan path ke Navbar benar
import Sidebar from "./components/Sidebar";  // Import Sidebar
import AlbumPage from "./pages/AlbumPage";
import MusicPage from "./pages/MusicPage";

const App = () => {
  return (
    <Router>
      <div style={{ display: "flex" }}>
        {/* Sidebar tetap di kiri */}
        <Sidebar />
        
        <div style={{ flex: 1, marginLeft: "20px"}}> {/* Memberikan margin kiri agar konten utama tidak tumpang tindih */}
          <Navbar />
          <Routes>
            <Route path="/" element={<AlbumPage />} />
            <Route path="/music" element={<MusicPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;
