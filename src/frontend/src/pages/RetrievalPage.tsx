import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './RetrievalPage.css';

interface LocationState {
  queryImage: File;
  similarImages: string[];
}

const RetrievalPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as LocationState;

  if (!state) {
    return <div className="retrieval-page-main">No image data available</div>;
  }

  const { queryImage, similarImages } = state;

  const handleBackNavigation = () => {
    navigate(-1);
  };

  return (
    <div className="retrieval-page-main">
      <div className="results-section">
        <h2>Similar Images ({similarImages?.length || 0} results)</h2>
        <div className="results-grid">
          {similarImages?.map((image, index) => (
            <div key={index} className="result-item">
              <div className="result-cover">
                <img 
                  src={`http://localhost:8000/album_images/${image}`} 
                  alt={image}
                  style={{
                    maxWidth: "100%",
                    maxHeight: "200px",
                    objectFit: "contain"
                  }}
                />
              </div>
              <div className="result-info">
                <span className="result-name">{image}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="navigation-section">
        <button onClick={handleBackNavigation}>Back</button>
      </div>
    </div>
  );
};

export default RetrievalPage;