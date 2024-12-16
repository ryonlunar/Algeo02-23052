import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './AlbumPage.css';
import AudioDetailsModal from './AudioDetail';

const AlbumPage: React.FC = () => {
    const [albums, setAlbums] = useState<any[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedImage, setSelectedImage] = useState<string | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const itemsPerPage = 18;

    useEffect(() => {
        axios.get('http://localhost:8000/albums')
            .then(response => {
                setAlbums(response.data);
            })
            .catch(error => {
                console.error("There was an error fetching the albums!", error);
            });
    }, []);

    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentAlbums = albums.slice(startIndex, endIndex);
    const totalPages = Math.ceil(albums.length / itemsPerPage);

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
    };

    const handleAlbumClick = (imageName: string) => {
        setSelectedImage(imageName);
        setIsModalOpen(true);
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
                    className={`pagination-button ${currentPage === i ? 'active' : ''}`}
                    onClick={() => handlePageChange(i)}
                >
                    {i}
                </button>
            );
        }
        return buttons;
    };

    return (
        <div className="album-page-main">
            <div className="album-grid">
                {currentAlbums.map((album, index) => (
                    <div 
                        key={index} 
                        className="album-item"
                        onClick={() => handleAlbumClick(album.name)}
                    >
                        <div className="album-cover">
                            <img 
                                src={`http://localhost:8000/album_images/${album.name}`} 
                                alt={album.name}
                            />
                        </div>
                        <div className="album-link">
                            {album.name}
                        </div>
                    </div>
                ))}
            </div>

            <div className="pagination">
                <button 
                    className="pagination-button"
                    onClick={() => handlePageChange(1)}
                    disabled={currentPage === 1}
                >
                    {'<<'}
                </button>
                <button 
                    className="pagination-button" 
                    onClick={() => handlePageChange(currentPage - 1)} 
                    disabled={currentPage === 1}
                >
                    {'<'}
                </button>

                {renderPaginationButtons()}

                <button 
                    className="pagination-button" 
                    onClick={() => handlePageChange(currentPage + 1)} 
                    disabled={currentPage === totalPages}
                >
                    {'>'}
                </button>
                <button 
                    className="pagination-button"
                    onClick={() => handlePageChange(totalPages)}
                    disabled={currentPage === totalPages}
                >
                    {'>>'}
                </button>
            </div>

            <AudioDetailsModal 
                imageFile={selectedImage}
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
            />
        </div>
    );
};

export default AlbumPage;