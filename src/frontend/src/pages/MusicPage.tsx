import React, { useState } from 'react';
import './MusicPage.css';

const MusicPage: React.FC = () => {
    const musicFiles = Array.from({ length: 50 }, (_, i) => `audio${i + 1}.wav`); // Contoh data lebih banyak
    const itemsPerPage = 18; // Menampilkan 12 item per halaman
    const [currentPage, setCurrentPage] = useState(1);

    // Hitung item yang akan ditampilkan berdasarkan halaman aktif
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentItems = musicFiles.slice(startIndex, endIndex);

    // Hitung jumlah halaman
    const totalPages = Math.ceil(musicFiles.length / itemsPerPage);

    // Fungsi untuk mengubah halaman
    const handlePageChange = (page: number) => {
        setCurrentPage(page);
    };

    return (
        <div className="music-page-main">
            {/* Music Grid */}
            <div className="music-grid">
                {currentItems.map((file, index) => (
                    <div key={index} className="music-item">
                        <div className="music-thumbnail"></div>
                        <p>{file}</p>
                    </div>
                ))}
            </div>

            {/* Pagination */}
            <div className="pagination">
                <button 
                    className="pagination-button" 
                    onClick={() => handlePageChange(currentPage - 1)} 
                    disabled={currentPage === 1}
                >
                    {'<'}
                </button>

                {[...Array(totalPages)].map((_, index) => (
                    <button
                        key={index}
                        className={`pagination-button ${currentPage === index + 1 ? 'active' : ''}`}
                        onClick={() => handlePageChange(index + 1)}
                    >
                        {index + 1}
                    </button>
                ))}

                <button 
                    className="pagination-button" 
                    onClick={() => handlePageChange(currentPage + 1)} 
                    disabled={currentPage === totalPages}
                >
                    {'>'}
                </button>
            </div>
        </div>
    );
};

export default MusicPage;
