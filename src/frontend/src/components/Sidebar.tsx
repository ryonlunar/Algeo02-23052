import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./Sidebar.css";

// Komponen UploadModal (Untuk unggahan file biasa)
interface UploadModalProps {
  isOpen: boolean;
  onClose: (submitted?: boolean, fileName?: string, file?: File) => void;
  title: string;
}

const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, title }) => {
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    setFile(droppedFile);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSaveLocally = () => {
    if (file) {
      onClose(true, file.name, file);
    }
  };

  if (!isOpen) return null;

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
          {file ? <p>File Selected: {file.name}</p> : <p>Select file or Drag and drop here</p>}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            style={{ display: "none" }}
            accept={title === "Image" ? "image/*" : "audio/*"}
          />
        </div>
        <div className="modal-actions">
          <button onClick={() => onClose(false)}>Cancel</button>
          <button onClick={handleSaveLocally} disabled={!file}>
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

// Komponen PictureModal (Untuk logika retrieval gambar)
interface PictureModalProps {
  isOpen: boolean;
  onClose: (submitted: boolean, file?: File, similarImages?: string[], similarityScores?: number[]) => void;
}

const PictureModal: React.FC<PictureModalProps> = ({ isOpen, onClose }) => {
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmitRetrieval = async () => {
    if (!file) return;
  
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const startTime = performance.now(); // Tambahkan waktu mulai
      const response = await fetch("http://localhost:8000/api/retrieve", {
        method: "POST",
        body: formData,
      });
      const endTime = performance.now(); // Tambahkan waktu akhir
  
      if (response.ok) {
        const data = await response.json();
        const executionTime = data.execution_time || endTime - startTime; // Gunakan nilai dari server atau hitung manual
  
        onClose(true, file, data.similar_images, data.similarity_scores, executionTime); // Kirim executionTime
      } else {
        console.error("Retrieval failed");
        onClose(false);
      }
    } catch (error) {
      console.error("Error retrieving images:", error);
      onClose(false);
    }
  };
  

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 className="modal-title">Upload Picture for Retrieval</h2>
        <div className="upload-area" onClick={() => fileInputRef.current?.click()}>
          {file ? <p>File Selected: {file.name}</p> : <p>Select file or Drag and drop here</p>}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            style={{ display: "none" }}
            accept="image/*"
          />
        </div>
        <div className="modal-actions">
          <button onClick={() => onClose(false)}>Cancel</button>
          <button onClick={handleSubmitRetrieval} disabled={!file}>
            Find
          </button>
        </div>
      </div>
    </div>
  );
};

// Sidebar utama
const Sidebar: React.FC = () => {
  const navigate = useNavigate();

  const [showUploadOptions, setShowUploadOptions] = useState(false);
  const [showImageModal, setShowImageModal] = useState(false);
  const [showAudioModal, setShowAudioModal] = useState(false);
  const [showMapperModal, setShowMapperModal] = useState(false);
  const [showPictureModal, setShowPictureModal] = useState(false);

  const [uploadedFiles, setUploadedFiles] = useState({
    image: "",
    audio: "",
    mapper: "",
  });

  const [selectedFiles, setSelectedFiles] = useState<{
    [key: string]: File | null;
  }>({
    image: null,
    audio: null,
    mapper: null,
  });

  const [queryImage, setQueryImage] = useState<File | null>(null);
  const [similarImages, setSimilarImages] = useState<string[]>([]);
  const [similarityScores, setSimilarityScores] = useState<number[]>([]);

  const handleSavePendingUpload = (type: "image" | "audio" | "mapper", fileName: string, file: File) => {
    setUploadedFiles((prev) => ({
      ...prev,
      [type]: fileName,
    }));
    setSelectedFiles((prev) => ({
      ...prev,
      [type]: file,
    }));
  };

  const handlePictureRetrieval = (
    submitted: boolean,
    file?: File,
    similarImages?: string[],
    similarityScores?: number[],
    executionTime?: number // Tambahkan ini
  ) => {
    if (submitted && file) {
      setQueryImage(file);
      setSimilarImages(similarImages || []);
      setSimilarityScores(similarityScores || []);
      navigate("/retrieval", {
        state: {
          queryImage: file,
          similarImages: similarImages || [],
          similarityScores: similarityScores || [],
          executionTime,
        },
      });
    }
    setShowPictureModal(false);
  };
  

  const handleSubmitAll = async () => {
    if (!selectedFiles.image && !selectedFiles.audio && !selectedFiles.mapper) {
      alert("Please upload at least one file before submitting.");
      return;
    }

    const formData = new FormData();

    if (selectedFiles.image) {
      formData.append("images", selectedFiles.image);
    }
    if (selectedFiles.audio) {
      formData.append("audios", selectedFiles.audio);
    }
    if (selectedFiles.mapper) {
      formData.append("mapper", selectedFiles.mapper);
    }

    try {
      const response = await fetch("http://localhost:8000/submit-all", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        console.log("All files submitted successfully!");
        alert("Files uploaded successfully!");

        setUploadedFiles({
          image: "",
          audio: "",
          mapper: "",
        });
        setSelectedFiles({
          image: null,
          audio: null,
          mapper: null,
        });

        const inputs = document.querySelectorAll<HTMLInputElement>('input[type="file"]');
        inputs.forEach((input) => {
          input.value = "";
        });
      } else {
        console.error("Error submitting files");
        alert("Error uploading files. Please try again.");
      }
    } catch (error) {
      console.error("Submission error:", error);
      alert("Error uploading files. Please try again.");
    }
  };

  return (
    <div className="sidebar">
      <div className="placeholder">
        {queryImage ? (
          <div className="query-image">
            <img
              src={URL.createObjectURL(queryImage)}
              alt="Query"
              style={{
                maxWidth: "240px",
                maxHeight: "150px",
                objectFit: "contain",
              }}
            />
          </div>
        ) : (
          <>
            <p>Image: {uploadedFiles.image || "None"}</p>
            <p>Audio: {uploadedFiles.audio || "None"}</p>
            <p>Mapper: {uploadedFiles.mapper || "None"}</p>
          </>
        )}
      </div>

      <button className="sidebar-button" onClick={() => setShowUploadOptions(!showUploadOptions)}>
        Upload
      </button>

      {showUploadOptions && (
        <div className="upload-options">
          <button className="sidebar-button" onClick={() => setShowImageModal(true)}>
            Album Images {uploadedFiles.image && "✓"}
          </button>
          <button className="sidebar-button" onClick={() => setShowAudioModal(true)}>
            Music Audios {uploadedFiles.audio && "✓"}
          </button>
          <button className="sidebar-button" onClick={() => setShowMapperModal(true)}>
            Mapper {uploadedFiles.mapper && "✓"}
          </button>
          <button className="sidebar-button" onClick={handleSubmitAll}>
            Submit
          </button>
        </div>
      )}

      <button className="sidebar-button" onClick={() => setShowPictureModal(true)}>
        Pictures
      </button>

      <UploadModal
        isOpen={showImageModal}
        onClose={(submitted, fileName, file) => {
          if (submitted && fileName && file) {
            handleSavePendingUpload("image", fileName, file);
          }
          setShowImageModal(false);
        }}
        title="Image"
      />
      <UploadModal
        isOpen={showAudioModal}
        onClose={(submitted, fileName, file) => {
          if (submitted && fileName && file) {
            handleSavePendingUpload("audio", fileName, file);
          }
          setShowAudioModal(false);
        }}
        title="Audio"
      />
      <UploadModal
        isOpen={showMapperModal}
        onClose={(submitted, fileName, file) => {
          if (submitted && fileName && file) {
            handleSavePendingUpload("mapper", fileName, file);
          }
          setShowMapperModal(false);
        }}
        title="Mapper"
      />
      <PictureModal isOpen={showPictureModal} onClose={handlePictureRetrieval} />
    </div>
  );
};

export default Sidebar;