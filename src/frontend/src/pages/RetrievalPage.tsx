import React, { useState, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./RetrievalPage.css";

interface LocationState {
  queryImage: File;
  similarImages: string[];
  similarityScores: number[];
  executionTime?: number; // Waktu eksekusi dalam ms
}

interface ImageResult {
  filename: string;
  similarity: number;
}

const ITEMS_PER_PAGE = 10;

const RetrievalPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as LocationState;
  const [currentPage, setCurrentPage] = useState(1);

  if (!state) {
    return <div className="retrieval-page-main">No image data available</div>;
  }

  const { queryImage, similarImages, similarityScores, executionTime } = state;

  // Filter dan urutkan hasil dengan similarity >= 50%
  const filteredAndSortedResults: ImageResult[] = useMemo(() => {
    const results = similarImages
      .map((filename, index) => ({
        filename,
        similarity: similarityScores[index] * 100, // Ubah ke persentase
      }))
      .filter((result) => result.similarity >= 50)
      .sort((a, b) => b.similarity - a.similarity);

    const maxPages = Math.ceil(results.length / ITEMS_PER_PAGE);
    if (currentPage > maxPages && maxPages > 0) {
      setCurrentPage(1);
    }

    return results;
  }, [similarImages, similarityScores]);

  if (filteredAndSortedResults.length === 0) {
    return (
      <div className="retrieval-page-main">
        <div className="results-section">
          <h2>No images found with similarity above 50%</h2>
          {executionTime && (
            <p className="execution-time">
              Execution time: {executionTime.toFixed(2)} ms
            </p>
          )}
        </div>
        <div className="navigation-section">
          <button onClick={() => navigate(-1)} className="back-button">
            Back
          </button>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(filteredAndSortedResults.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const paginatedResults = filteredAndSortedResults.slice(startIndex, endIndex);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo(0, 0); // Scroll ke atas setiap ganti halaman
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
          Similar Images ({filteredAndSortedResults.length} results above 50% similarity)
          {totalPages > 1 && ` - Page ${currentPage} of ${totalPages}`}
        </h2>
        {executionTime && (
          <p className="execution-time">
            Execution time: {executionTime.toFixed(2)} ms
          </p>
        )}
        <div className="results-grid">
          {paginatedResults.map((result, index) => (
            <div key={index} className="result-item">
              <div className="result-cover">
                <img
                  src={`http://localhost:8000/album_images/${result.filename}`}
                  alt={result.filename}
                  className="result-image"
                />
              </div>
              <div className="result-info">
                <span className="result-name">{result.filename}</span>
                <span className="result-similarity">
                  Similarity: {result.similarity.toFixed(2)}%
                </span>
              </div>
            </div>
          ))}
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

export default RetrievalPage;
