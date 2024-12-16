import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import DefaultIcon from "../assets/default.jpeg";

interface AudioResult {
  filename: string;
  similarity: number;
}

interface LocationState {
  queryAudio: File;
  similarAudios: string[];
  similarityScores: number[];
  executionTime?: number;
}

const ITEMS_PER_PAGE = 10;

const AudioRetrievalPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as LocationState;
  const [currentPage, setCurrentPage] = useState(1);
  const [playingAudio, setPlayingAudio] = useState<string | null>(null);
  const [mapper, setMapper] = useState<Record<string, string>>({});

  if (!state) {
    return <div className="retrieval-page-main">No audio data available</div>;
  }

  const { queryAudio, similarAudios, similarityScores, executionTime } = state;

  // Fetch the mapper data
  useEffect(() => {
    const fetchMapper = async () => {
      try {
        const response = await fetch("http://localhost:8000/mapper.txt");
        const text = await response.text();
        const mapping: Record<string, string> = {};
        text.split("\n").forEach((line) => {
          const [audioFile, imageFile] = line.split("\t");
          if (audioFile && imageFile) {
            mapping[audioFile.trim()] = imageFile.trim();
          }
        });
        setMapper(mapping);
      } catch (error) {
        console.error("Error fetching mapper file:", error);
      }
    };

    fetchMapper();
  }, []);

  const filteredAndSortedResults: AudioResult[] = similarAudios
    .map((filename, index) => ({
      filename,
      similarity: similarityScores[index] * 100,
    }))
    .sort((a, b) => b.similarity - a.similarity)
    .filter((result) => result.similarity >= 50);

  const totalPages = Math.ceil(filteredAndSortedResults.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const paginatedResults = filteredAndSortedResults.slice(startIndex, endIndex);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo(0, 0);
  };

  const handlePlayAudio = (filename: string) => {
    if (playingAudio === filename) {
      const audioElement = document.getElementById(filename) as HTMLAudioElement;
      if (audioElement.paused) {
        audioElement.play();
      } else {
        audioElement.pause();
      }
    } else {
      if (playingAudio) {
        const prevAudio = document.getElementById(playingAudio) as HTMLAudioElement;
        prevAudio?.pause();
      }
      const audioElement = document.getElementById(filename) as HTMLAudioElement;
      audioElement?.play();
      setPlayingAudio(filename);
    }
  };

  const renderPaginationButtons = () => {
    if (totalPages <= 1) return null;

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
          onClick={() => handlePageChange(i)}
        >
          {i}
        </button>
      );
    }
    return buttons;
  };

  return (
    <div className="retrieval-page-main">
      <div className="results-section">
        <h2>
          {filteredAndSortedResults.length > 0
            ? `Similar Audio Files (${filteredAndSortedResults.length} results)`
            : "No similar audio files found"}
        </h2>
        {executionTime && (
          <p className="execution-time">
            Execution time: {executionTime.toFixed(2)} ms
          </p>
        )}
        <div className="results-grid">
          {paginatedResults.map((result, index) => {
            const imageFile = mapper[result.filename];

            return (
              <div key={index} className="result-item">
                <div className="result-cover">
                <img
                  src={imageFile ? `http://localhost:8000/album_images/${imageFile}` : DefaultIcon}
                  alt={imageFile || "Default image"}
                  className="result-image"
                />
                </div>
                <div className="player-section">
                  <button
                    onClick={() => handlePlayAudio(result.filename)}
                    className="play-button"
                  >
                    {playingAudio === result.filename ? "⏸" : "▶"}
                  </button>
                  <audio
                    id={result.filename}
                    src={`http://localhost:8000/music_audios/${result.filename}`}
                    onEnded={() => setPlayingAudio(null)}
                  />
                </div>
                <div className="result-info">
                  <div className="result-name">{result.filename}</div>
                  <div className="result-similarity">
                    Similarity: {result.similarity.toFixed(2)}%
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {totalPages > 1 && (
          <div className="pagination">
            <button
              className="pagination-button"
              onClick={() => handlePageChange(1)}
              disabled={currentPage === 1}
            >
              {"<<"}
            </button>
            <button
              className="pagination-button"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              {"<"}
            </button>

            {renderPaginationButtons()}

            <button
              className="pagination-button"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              {">"}
            </button>
            <button
              className="pagination-button"
              onClick={() => handlePageChange(totalPages)}
              disabled={currentPage === totalPages}
            >
              {">>"}
            </button>
          </div>
        )}
      </div>

      <div className="navigation-section">
        <button onClick={() => navigate(-1)} className="back-button">
          Back
        </button>
      </div>
    </div>
  );
};

export default AudioRetrievalPage;
