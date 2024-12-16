import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import './AudioDetails.css';

const AudioDetailsModal = ({ imageFile, isOpen, onClose }) => {
    const [audioFiles, setAudioFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [errorMessage, setErrorMessage] = useState('');

    useEffect(() => {
        const fetchMapperData = async () => {
            if (!imageFile || !isOpen) return;

            try {
                const response = await fetch('http://localhost:8000/mapper.txt');
                if (!response.ok) {
                    throw new Error('Failed to fetch mapper data');
                }

                const text = await response.text();
                const lines = text.split('\n').filter(line => line.trim());

                // Debug log to check mapper content
                console.log("Mapper file lines:", lines);

                const relatedAudios = lines
                    .filter(line => {
                        const [audioFile, imageFileName] = line.split('\t');
                        return imageFileName?.trim().toLowerCase() === imageFile.toLowerCase();
                    })
                    .map(line => {
                        const [audioFile] = line.split('\t');
                        return audioFile?.trim() || '';
                    });

                // Debug log for matched audio files
                console.log("Related audio files:", relatedAudios);

                setAudioFiles(relatedAudios);
            } catch (error) {
                console.error('Error fetching mapper data:', error);
                setErrorMessage('Failed to load audio files. Please try again.');
            } finally {
                setLoading(false);
            }
        };

        fetchMapperData();
    }, [imageFile, isOpen]);

    if (!isOpen) return null;

    return (
        <div className="audio-modal-overlay">
            <div className="audio-modal-container">
                <div className="audio-modal-content">
                    <div className="audio-modal-header">
                        <h2 className="audio-modal-title">Related Audio Files</h2>
                        <button onClick={onClose} className="audio-modal-close">
                            ×
                        </button>
                    </div>

                    {loading ? (
                        <div className="audio-modal-loading">Loading...</div>
                    ) : errorMessage ? (
                        <div className="audio-modal-error">{errorMessage}</div>
                    ) : audioFiles.length === 0 ? (
                        <div className="audio-modal-empty">No audio files found for this album</div>
                    ) : (
                        <div className="audio-list">
                            {audioFiles.map((audioFile, index) => (
                                <div key={index} className="audio-item">
                                    <div className="audio-content">
                                        <p className="audio-title">{audioFile}</p>
                                        <audio
                                            controls
                                            className="audio-player"
                                            src={`http://localhost:8000/music_audios/${audioFile}`}
                                        >
                                            Your browser does not support the audio element.
                                        </audio>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

AudioDetailsModal.propTypes = {
    imageFile: PropTypes.string,
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
};

export default AudioDetailsModal;
