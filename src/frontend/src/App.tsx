import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";  // Pastikan path ke Navbar benar
import Sidebar from "./components/Sidebar";  // Import Sidebar
import AlbumPage from "./pages/AlbumPage";
import MusicPage from "./pages/MusicPage";

const App = () => {
  return (
    <Router>
        <Sidebar />
        <Navbar />
          <Routes>
            <Route path="/album" element={<AlbumPage />} />
            <Route path="/music" element={<MusicPage />} />
          </Routes>
    </Router>
  );
};

export default App;
