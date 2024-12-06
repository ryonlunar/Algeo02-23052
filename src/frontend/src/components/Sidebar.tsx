import { useState, useRef } from "react";
import "./Sidebar.css";

interface UploadModalProps {
  isOpen: boolean;
  onClose: (uploaded?: boolean, fileName?: string) => void;
  title: string;
  endpoint: string;
}

const UploadModal = ({ isOpen, onClose, title, endpoint }: UploadModalProps) => {
  if (!isOpen) return null;
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    await uploadFile(file);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      await uploadFile(e.target.files[0]);
    }
  };

  const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`http://localhost:8000/${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        onClose(true, file.name);
      } else {
        console.error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 className="modal-title">Upload {title}</h2>
        <div 
          className="upload-area"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <p>Select file</p>
          <p>or</p>
          <p>Drag and drop here</p>
          <input 
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            accept={title === 'Image' ? 'image/*' : 'audio/*'}
          />
        </div>
        <div className="modal-actions">
          <button onClick={() => onClose(false)}>Cancel</button>
        </div>
      </div>
    </div>
  );
};

const Sidebar = () => {
  const [showUploadOptions, setShowUploadOptions] = useState(false);
  const [showImageModal, setShowImageModal] = useState(false);
  const [showAudioModal, setShowAudioModal] = useState(false);
  const [showMapperModal, setShowMapperModal] = useState(false);
  
  const [imageUploaded, setImageUploaded] = useState(false);
  const [audioUploaded, setAudioUploaded] = useState(false);
  const [mapperUploaded, setMapperUploaded] = useState(false);

  const [uploadedFiles, setUploadedFiles] = useState({
    image: '',
    audio: '',
    mapper: ''
  });

  const [showPlaceholderContent, setShowPlaceholderContent] = useState(false);

  const toggleUploadOptions = () => {
    setShowUploadOptions(!showUploadOptions);
  };

  const handleSubmit = () => {
    setShowPlaceholderContent(true);
    setShowUploadOptions(false);
    setImageUploaded(false);
    setAudioUploaded(false);
    setMapperUploaded(false);
  };

  const allFilesUploaded = imageUploaded;

  return (
    <div className="sidebar">
      <div className="placeholder">
        {showPlaceholderContent ? (
          <>
            image: {uploadedFiles.image}<br />
            {audioUploaded && <>audio: {uploadedFiles.audio}<br /></>}
            {mapperUploaded && <>mapper: {uploadedFiles.mapper}</>}
          </>
        ) : (
          'Placeholder'
        )}
      </div>

      <button className="sidebar-button" onClick={toggleUploadOptions}>
        Upload
      </button>

      {showUploadOptions && (
        <div className="upload-options">
          <button 
            className="sidebar-button"
            onClick={() => setShowImageModal(true)}
          >
            Album Images {imageUploaded && "✓"}
          </button>
          <button 
            className="sidebar-button"
            onClick={() => setShowAudioModal(true)}
          >
            Music Audios {audioUploaded && "✓"}
          </button>
          <button 
            className="sidebar-button"
            onClick={() => setShowMapperModal(true)}
          >
            Mapper {mapperUploaded && "✓"}
          </button>
          <button 
            className={`sidebar-button ${!allFilesUploaded ? 'disabled-button' : ''}`}
            onClick={handleSubmit}
            disabled={!allFilesUploaded}
          >
            Submit
          </button>
        </div>
      )}

      <button className="sidebar-button">Pictures</button>
      <button className="sidebar-button">Audios</button>

      <UploadModal 
        isOpen={showImageModal}
        onClose={(uploaded, fileName) => {
          setShowImageModal(false);
          if (uploaded && fileName) {
            setImageUploaded(true);
            setUploadedFiles(prev => ({ ...prev, image: fileName }));
          }
        }}
        title="Image"
        endpoint="upload-image"
      />
      <UploadModal 
        isOpen={showAudioModal}
        onClose={(uploaded, fileName) => {
          setShowAudioModal(false);
          if (uploaded && fileName) {
            setAudioUploaded(true);
            setUploadedFiles(prev => ({ ...prev, audio: fileName }));
          }
        }}
        title="Audio"
        endpoint="upload-audio"
      />
      <UploadModal 
        isOpen={showMapperModal}
        onClose={(uploaded, fileName) => {
          setShowMapperModal(false);
          if (uploaded && fileName) {
            setMapperUploaded(true);
            setUploadedFiles(prev => ({ ...prev, mapper: fileName }));
          }
        }}
        title="Mapper"
        endpoint="upload-mapper"
      />
    </div>
  );
};

export default Sidebar;