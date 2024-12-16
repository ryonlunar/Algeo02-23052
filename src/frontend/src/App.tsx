// App.tsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import AlbumPage from "./pages/AlbumPage";
import MusicPage from "./pages/MusicPage";
import RetrievalPage from "./pages/RetrievalPage";
import AudioRetrievalPage from "./pages/AudioResult";

const App = () => {
  return (
    <Router>
      <Sidebar />
      <Navbar />
      <Routes>
        <Route path="/" element={<AlbumPage />} />
        <Route path="/music" element={<MusicPage />} />
        <Route path="/retrieval" element={<RetrievalPage />} />
        <Route path="/audio-retrieval" element={<AudioRetrievalPage />} />
      </Routes>
    </Router>
  );
};

export default App;