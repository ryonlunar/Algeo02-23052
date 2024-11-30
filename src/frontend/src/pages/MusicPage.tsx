import React from 'react';
import './MusicPage.css';

const MusicPage: React.FC = () => {
    const musicFiles = Array.from({ length: 12 }, (_, i) => `audio${i + 1}.wav`);

    return (
        <div className="music-page-main">
            {/* Music Grid */}
            <div className="music-grid">
                {musicFiles.map((file, index) => (
                    <div key={index} className="music-item">
                        <div className="music-thumbnail"></div>
                        <p>{file}</p>
                    </div>
                ))}
            </div>

            {/* Pagination */}
            <div className="pagination">
                <button className="pagination-button">{'<'}</button>
                {[1, 2, 3, 4, 5].map((page) => (
                    <button key={page} className="pagination-button">
                        {page}
                    </button>
                ))}
                <button className="pagination-button">{'>'}</button>
            </div>
        </div>
    );
};

export default MusicPage;
