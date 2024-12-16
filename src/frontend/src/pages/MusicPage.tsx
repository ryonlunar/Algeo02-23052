import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './MusicPage.css';
import musicIcon from '../assets/icon.png';

const MusicPage: React.FC = () => {
    const [musicFiles, setMusicFiles] = useState<any[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 18;

    useEffect(() => {
        axios.get('http://localhost:8000/audios')
            .then(response => {
                setMusicFiles(response.data);
            })
            .catch(error => {
                console.error("There was an error fetching the music files!", error);
            });
    }, []);

    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentMusic = musicFiles.slice(startIndex, endIndex);
    const totalPages = Math.ceil(musicFiles.length / itemsPerPage);

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
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
        <div className="music-page-main">
            <div className="music-grid">
                {currentMusic.map((music, index) => (
                    <div key={index} className="music-item">
                        <div className="music-icon-wrapper">
                            <img src={musicIcon} alt="Music icon" className="music-icon" />
                        </div>
                        <div className="music-player">
                            <audio
                                controls
                                src={`http://localhost:8000/music_audios/${music.name}`}
                            >
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                        <Link to={`/music/${music.name}`} className="music-link">
                            {music.name}
                        </Link>
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
        </div>
    );
};

export default MusicPage;