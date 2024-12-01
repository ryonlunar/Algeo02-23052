import React, { useState } from 'react';
import { Link } from 'react-router-dom';  // Import Link untuk navigasi
import './AlbumPage.css';

const AlbumPage: React.FC = () => {
    const albumData = Array.from({ length: 50 }, (_, i) => ({
        albumName: `Album ${i + 1}`,
        coverImage: `album-cover-${i + 1}.jpg`,
        musicFiles: Array.from({ length: 5 }, (_, j) => `audio${i * 5 + j + 1}.wav`), 
    }));
    
    const itemsPerPage = 18; 
    const [currentPage, setCurrentPage] = useState(1);

    // Hitung album yang akan ditampilkan berdasarkan halaman aktif
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentAlbums = albumData.slice(startIndex, endIndex);

    // Hitung jumlah halaman
    const totalPages = Math.ceil(albumData.length / itemsPerPage);

    // Fungsi untuk mengubah halaman
    const handlePageChange = (page: number) => {
        setCurrentPage(page);
    };

    return (
        <div className="album-page-main">
            {/* Album Grid */}
            <div className="album-grid">
                {currentAlbums.map((album, index) => (
                    <div key={index} className="album-item">
                        <div className="album-cover">
                            <img src={album.coverImage} alt={album.albumName} />
                        </div>
                        {/* Link ke halaman album untuk melihat musik terkait */}
                        <Link to={`/album/${album.albumName}`} className="album-link">
                            <h3>{album.albumName}</h3>
                        </Link>
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

export default AlbumPage;
