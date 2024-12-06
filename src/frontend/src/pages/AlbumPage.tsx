import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './AlbumPage.css';

const AlbumPage: React.FC = () => {
    const [albums, setAlbums] = useState<any[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 18;

    useEffect(() => {
        // Fetch albums from the backend API
        axios.get('http://localhost:8000/albums')
            .then(response => {
                setAlbums(response.data);
            })
            .catch(error => {
                console.error("There was an error fetching the albums!", error);
            });
    }, []);

    // Hitung album yang akan ditampilkan berdasarkan halaman aktif
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentAlbums = albums.slice(startIndex, endIndex);

    // Hitung jumlah halaman
    const totalPages = Math.ceil(albums.length / itemsPerPage);

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
                            {/* Pastikan URL gambar valid */}
                            <img src={`http://localhost:8000/album_images/${album.name}`} alt={album.name} />
                        </div>
                        {/* Link ke halaman album untuk melihat musik terkait */}
                        <Link to={`/album/${album.name}`} className="album-link">
                            <h3>{album.name}</h3>
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
