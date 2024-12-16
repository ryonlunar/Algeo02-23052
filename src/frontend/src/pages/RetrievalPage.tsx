import React, { useState, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import AudioDetailsModal from "./AudioDetail";
import "./RetrievalPage.css";

interface LocationState {
  queryImage: File;
  similarImages: string[];
  similarityScores: number[];
  executionTime?: number;
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
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  if (!state) {
    return <div className="retrieval-page-main">No image data available</div>;
  }

  const { similarImages, similarityScores, executionTime } = state;

  // Filter dan urutkan hasil
  const filteredAndSortedResults: ImageResult[] = useMemo(() => {
    const allResults = similarImages
      .map((filename, index) => ({
        filename,
        similarity: similarityScores[index] * 100,
      }))
      .sort((a, b) => b.similarity - a.similarity);

    const filteredResults = allResults.filter((result) => result.similarity >= 70);

    if (filteredResults.length === 0 && allResults.length > 0) {
      filteredResults.push(allResults[0]);
    }

    return filteredResults;
  }, [similarImages, similarityScores]);

  const totalPages = Math.ceil(filteredAndSortedResults.length / ITEMS_PER_PAGE);

  // Data untuk halaman saat ini
  const paginatedResults = filteredAndSortedResults.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const handlePageChange = (page: number) => {
    console.log("Changing page to:", page); // Debugging
    setCurrentPage(page);
    window.scrollTo(0, 0);
  };

  const openModal = (filename: string) => {
    setSelectedImage(filename);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedImage(null);
  };

  return (
    <div className="retrieval-page-main">
      <div className="results-section">
        <h2>
          {filteredAndSortedResults.some((result) => result.similarity >= 70)
            ? `Similar Images (${filteredAndSortedResults.length} results above 70% similarity)`
            : `Showing the most similar image (no results above 70% similarity)`}
          {totalPages > 1 && ` - Page ${currentPage} of ${totalPages}`}
        </h2>
        {executionTime && (
          <p className="execution-time">
            Execution time: {executionTime.toFixed(2)} ms
          </p>
        )}

        <div className="results-grid">
          {paginatedResults.map((result, index) => (
            <div
              key={index}
              className="result-item"
              onClick={() => openModal(result.filename)}
              style={{ cursor: "pointer" }}
            >
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

        {/* Pagination */}
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
            {[...Array(totalPages)].map((_, i) => (
              <button
                key={i}
                className={`pagination-button ${currentPage === i + 1 ? "active" : ""}`}
                onClick={() => handlePageChange(i + 1)}
              >
                {i + 1}
              </button>
            ))}
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

      {/* AudioDetailsModal */}
      <AudioDetailsModal
        imageFile={selectedImage}
        isOpen={isModalOpen}
        onClose={closeModal}
      />
    </div>
  );
};

export default RetrievalPage;


