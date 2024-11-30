import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";  // Pastikan path ke Navbar benar
import AlbumPage from "./pages/AlbumPage";
import MusicPage from "./pages/MusicPage";

const App = () => {
  return (
    <Router>
      {/* Navbar diletakkan di sini agar selalu muncul */}
      <Navbar />
      
      <Routes>
        {/* Rute untuk AlbumPage sebagai halaman default */}
        <Route path="/" element={<AlbumPage />} />
        {/* Rute untuk MusicPage */}
        <Route path="/music" element={<MusicPage />} />
      </Routes>
    </Router>
  );
};

export default App;
