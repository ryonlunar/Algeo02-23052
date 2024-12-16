import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import MIDI from "midi.js";
import "./MusicPage.css";
import musicIcon from "../assets/icon.png";

const MusicPage: React.FC = () => {
  const [musicFiles, setMusicFiles] = useState<any[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;
  const midiPlayers = useRef<Map<number, any>>(new Map());
  const [playingIndex, setPlayingIndex] = useState<number | null>(null);

  useEffect(() => {
    axios
      .get("http://localhost:8000/audios")
      .then((response) => {
        setMusicFiles(response.data);
      })
      .catch((error) => {
        console.error("There was an error fetching the music files!", error);
      });

      MIDI.loadPlugin({
        soundfontUrl: "./soundfont/",
        instrument: "acoustic_grand_piano",
        onsuccess: () => {
            console.log("MIDI.js Plugin loaded.");
        },
    });
 }, []);

  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentMusic = musicFiles.slice(startIndex, endIndex);
  const totalPages = Math.ceil(musicFiles.length / itemsPerPage);

  const handlePlayPause = (index: number, fileName: string) => {
    if (playingIndex === index) {
        MIDI.Player.stop(); // Stop the current playback
        setPlayingIndex(null);
    } else {
        // Load and play the selected MIDI file
        MIDI.Player.stop(); // Stop any currently playing file
        MIDI.Player.loadFile(`http://localhost:8000/music_audios/${fileName}`, () => {
            MIDI.Player.start();
            setPlayingIndex(index);
        });

        // Stop playback when it ends
        MIDI.Player.addListener((data) => {
            if (data.now === data.end) {
                setPlayingIndex(null);
                MIDI.Player.stop();
            }
        });
    }
};

  const renderPaginationButtons = () => {
    const buttons = [];
    const maxVisibleButtons = 5;
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + maxVisibleButtons - 1);
    startPage = Math.max(1, endPage - maxVisibleButtons + 1);

    for (let i = startPage; i <= endPage; i++) {
      buttons.push(
        <button
          key={i}
          className={`pagination-button ${currentPage === i ? "active" : ""}`}
          onClick={() => setCurrentPage(i)}
        >
          {i}
        </button>
      );
    }
    return buttons;
  };

  return (
    <div className="music-page-main">
      <div className="music-grid">
        {currentMusic.map((music, index) => (
          <div key={index} className="music-item">
            <div className="music-icon-wrapper">
              <img src={musicIcon} alt="Music icon" className="music-icon" />
            </div>
            <div className="music-player">
              <button
                className={`play-button ${
                  playingIndex === index ? "playing" : ""
                }`}
                onClick={() => handlePlayPause(index, music.name)}
              >
                {playingIndex === index ? "⏸" : "▶"}
              </button>
            </div>
            <span className="music-link">
                {music.name}
            </span>
          </div>
        ))}
      </div>

      <div className="pagination">
        <button
          className="pagination-button"
          onClick={() => setCurrentPage(1)}
          disabled={currentPage === 1}
        >
          {"<<"}
        </button>
        <button
          className="pagination-button"
          onClick={() => setCurrentPage(currentPage - 1)}
          disabled={currentPage === 1}
        >
          {"<"}
        </button>

        {renderPaginationButtons()}

        <button
          className="pagination-button"
          onClick={() => setCurrentPage(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          {">"}
        </button>
        <button
          className="pagination-button"
          onClick={() => setCurrentPage(totalPages)}
          disabled={currentPage === totalPages}
        >
          {">>"}
        </button>
      </div>
    </div>
  );
};

export default MusicPage;
