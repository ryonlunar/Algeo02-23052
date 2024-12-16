import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./Sidebar.css";

interface UploadModalProps {
  isOpen: boolean;
  onClose: (submitted?: boolean, fileName?: string, file?: File) => void;
  title: string;
  accept?: string;
}

const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, title, accept }) => {
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
      if (file.type === "application/zip") {
        onClose(true, file.name, file);
      } else {
        onClose(true, file.name, file);
      }
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
            accept={accept || (title === "Image" ? ".zip,image/*" : title === "Audio" ? ".zip,audio/*" : "*")}
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

interface PictureModalProps {
  isOpen: boolean;
  onClose: (submitted: boolean, file?: File, similarImages?: string[], similarityScores?: number[], executionTime?: number) => void;
}

const PictureModal: React.FC<PictureModalProps> = ({ isOpen, onClose }) => {
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false); // Add isProcessing state

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setErrorMessage(null);

    const validExtensions = [".jpg", ".jpeg", ".png"];
    const fileExtension = selectedFile.name.toLowerCase().slice(-4); // Get the last 4 characters of the file name

    const validMIMEType =
      selectedFile.type === "image/jpeg" ||
      selectedFile.type === "image/png" ||
      selectedFile.type === "image/jpg";

    if (!validMIMEType && !validExtensions.includes(fileExtension)) {
      setErrorMessage("Please select a valid image file (.jpg, .jpeg, or .png).");
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  const handleSubmitRetrieval = async () => {
    if (!file) return;

    setIsProcessing(true); // Set isProcessing to true when the process starts

    const formData = new FormData();
    formData.append("file", file);

    try {
      const startTime = performance.now();
      const response = await fetch("http://localhost:8000/api/image-search", {
        method: "POST",
        body: formData,
      });
      const endTime = performance.now();

      if (response.ok) {
        const data = await response.json();
        const executionTime = data.execution_time || endTime - startTime;
        onClose(true, file, data.similar_images, data.similarity_scores, executionTime);
      } else {
        console.error("Retrieval failed");
        onClose(false);
      }
    } catch (error) {
      console.error("Error retrieving images:", error);
      onClose(false);
    } finally {
      setIsProcessing(false); // Set isProcessing to false when the process is done
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 className="modal-title">Upload Picture for Retrieval</h2>
        <div className="upload-area" onClick={() => fileInputRef.current?.click()}>
          {file ? <p>File Selected: {file.name}</p> : <p>Select file or Drag and drop here</p>}
          {errorMessage && <p className="error-message">{errorMessage}</p>}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            style={{ display: "none" }}
            accept="image/jpeg, image/png, image/jpg"
          />
        </div>
        <div className="modal-actions">
          <button onClick={() => onClose(false)}>Cancel</button>
          <button onClick={handleSubmitRetrieval} disabled={!file || isProcessing}>
            {isProcessing ? "Processing..." : "Find"}
          </button>
        </div>
      </div>
    </div>
  );
};

interface AudioModalProps {
  isOpen: boolean;
  onClose: (submitted: boolean, file?: File, similarAudios?: string[], similarityScores?: number[], executionTime?: number) => void;
}

const AudioModal: React.FC<AudioModalProps> = ({ isOpen, onClose }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const controller = useRef<AbortController | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setErrorMessage(null);

    const validMIMEType = selectedFile.type === "audio/midi" || selectedFile.type === "audio/x-midi";
    const validExtensions = [".midi", ".mid"];
    const fileExtension = selectedFile.name.toLowerCase().slice(-4); // Get last 4 characters to check file extension

    if (!validMIMEType && !validExtensions.includes(fileExtension)) {
      setErrorMessage("Please select a valid MIDI audio file.");
      setFile(null);
      return;
    }

    const maxSizeInMB = 10;
    if (selectedFile.size > maxSizeInMB * 1024 * 1024) {
      setErrorMessage(`File size must be less than ${maxSizeInMB}MB.`);
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  const handleSubmitAudio = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    controller.current = new AbortController();
    setIsProcessing(true);

    try {
      const startTime = performance.now();
      const response = await fetch("http://localhost:8000/api/audio-search", {
        method: "POST",
        body: formData,
        signal: controller.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const executionTime = data.execution_time || performance.now() - startTime;
      onClose(true, file, data.similar_audios, data.similarity_scores, executionTime);
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Request was cancelled');
      } else {
        console.error("Error searching audio:", error);
      }
      onClose(false);
    } finally {
      setIsProcessing(false);
      controller.current = null;
    }
  };

  const handleCancel = () => {
    if (isProcessing && controller.current) {
      controller.current.abort();
    }
    setFile(null);
    setIsProcessing(false);
    onClose(false);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 className="modal-title">Upload Audio for Search</h2>
        <div className="upload-area" onClick={() => fileInputRef.current?.click()}>
          {file ? (
            <p>File Selected: {file.name}</p>
          ) : (
            <p>Select file or Drag and drop here</p>
          )}
          {errorMessage && <p className="error-message">{errorMessage}</p>}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            style={{ display: "none" }}
            accept="audio/*"
          />
        </div>
        <div className="modal-actions">
          <button onClick={handleCancel}>Cancel</button>
          <button onClick={handleSubmitAudio} disabled={!file || isProcessing}>
            {isProcessing ? "Processing..." : "Find"}
          </button>
        </div>
      </div>
    </div>
  );
};

interface MicModalProps {
  isOpen: boolean;
  onClose: (submitted: boolean, file?: File, similarAudios?: string[], similarityScores?: number[], executionTime?: number) => void;
}

const MicrophoneModal: React.FC<MicModalProps> = ({ isOpen, onClose }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStartRecording = async () => {
    try {
      const response = await fetch("http://localhost:8000/start-recording/", {
        method: "POST",
      });

      if (response.ok) {
        setIsRecording(true);
        setError(null);
        console.log("Recording started...");

        setTimeout(async () => {
          setIsRecording(false);
          setIsProcessing(true);

          try {
            const audioResponse = await fetch("http://localhost:8000/get-recorded-audio/");

            if (!audioResponse.ok) {
              throw new Error("Failed to fetch recorded audio");
            }

            const audioBlob = await audioResponse.blob();
            const audioFile = new File([audioBlob], "recorded_audio.mid", { type: "audio/mid" });

            await fetchDataFromApi(audioFile);
          } catch (error) {
            console.error("Error fetching or processing audio:", error);
            setError("Error during audio processing.");
            setIsProcessing(false);
          }
        }, 30000);
      } else {
        console.error("Failed to start recording");
        setError("Failed to start recording");
        setIsRecording(false);
      }
    } catch (error) {
      console.error("Error starting recording:", error);
      setError("Error during recording");
      setIsRecording(false);
      setIsProcessing(false);
    }
  };

  const fetchDataFromApi = async (micFile: File) => {
    try {
      const formData = new FormData();
      formData.append("file", micFile);

      const startTime = performance.now();
      const response = await fetch("http://localhost:8000/api/audio-search-mic", {
        method: "POST",
        body: formData,
      });
      const endTime = performance.now();

      if (response.ok) {
        const data = await response.json();
        const executionTime = data.execution_time || endTime - startTime;
        onClose(true, micFile, data.similar_audios, data.similarity_scores, executionTime);
      } else {
        console.error("Audio search failed");
        onClose(false);
      }
    } catch (error) {
      console.error("Error searching audio:", error);
      onClose(false);
    }
  };

  const handleCancel = () => {
    setIsRecording(false);
    setIsProcessing(false);
    setError(null);
    onClose(false);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 className="modal-title">Record Audio for Search</h2>
        <div className="modal-actions">
          <button onClick={handleCancel}>Cancel</button>
          {!isRecording && !isProcessing ? (
            <button onClick={handleStartRecording}>Start Recording</button>
          ) : isRecording ? (
            <button disabled>Recording...</button>
          ) : (
            <button disabled>Processing...</button>
          )}
        </div>
        {isProcessing && (
          <div>
            <p>Processing the audio...</p>
          </div>
        )}
        {error && (
          <div style={{ color: 'red' }}>
            <p>{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};


const Sidebar: React.FC = () => {
  const navigate = useNavigate();

  const [showUploadOptions, setShowUploadOptions] = useState(false);
  const [showImageModal, setShowImageModal] = useState(false);
  const [showAudioModal, setShowAudioModal] = useState(false);
  const [showMapperModal, setShowMapperModal] = useState(false);
  const [showPictureModal, setShowPictureModal] = useState(false);
  const [showAudioSearchModal, setShowAudioSearchModal] = useState(false);
  const [showMicSearchModal, setShowMicSearchModal] = useState(false);

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
  const [queryAudio, setQueryAudio] = useState<File | null>(null);
  const [similarImages, setSimilarImages] = useState<string[]>([]);
  const [similarAudios, setSimilarAudios] = useState<string[]>([]);
  const [similarityScores, setSimilarityScores] = useState<number[]>([]);
  const [audioSimilarityScores, setAudioSimilarityScores] = useState<number[]>([]);

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
    executionTime?: number
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

  const handleAudioRetrieval = (
    submitted: boolean,
    file?: File,
    similarAudios?: string[],
    similarityScores?: number[],
    executionTime?: number
  ) => {
    if (submitted && file) {
      setQueryAudio(file);
      setSimilarAudios(similarAudios || []);
      setAudioSimilarityScores(similarityScores || []);
      navigate("/audio-retrieval", {
        state: {
          queryAudio: file,
          similarAudios: similarAudios || [],
          similarityScores: similarityScores || [],
          executionTime,
        },
      });
    }
    setShowAudioSearchModal(false);
  };

  const handleMicRetrieval = (
    submitted: boolean,
    file?: File,
    similarAudios?: string[],
    similarityScores?: number[],
    executionTime?: number
  ) => {
    if (submitted && file) {
      setQueryAudio(file);
      setSimilarAudios(similarAudios ?? []);
      setAudioSimilarityScores(similarityScores ?? []);
      navigate("/audio-retrieval", {
        state: {
          queryAudio: file,
          similarAudios: similarAudios ?? [],
          similarityScores: similarityScores ?? [],
          executionTime,
        },
      });
    } else {
      console.error("Submission failed or no file found");
    }
    setShowMicSearchModal(false);
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
        ) : queryAudio ? (
          <div
            className="query-audio"
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              height: "100%",
            }}
          >
            <img
              src="/src/assets/icon.png"
              alt="Audio Icon"
              style={{
                maxWidth: "200px",
                maxHeight: "110px",
                objectFit: "contain",
              }}
            />
            <div className="audio-teks">
              <span style={{ margin: "10px 0 0 0", textAlign: "center" }}>
                {queryAudio.name}
              </span>
            </div>
          </div>
        ) : (
          <div className="uploaded-files">
            <p>
              <span className="file-label">Image:</span>{" "}
              <span className="file-value">{uploadedFiles.image || "None"}</span>
            </p>
            <p>
              <span className="file-label">Audio:</span>{" "}
              <span className="file-value">{uploadedFiles.audio || "None"}</span>
            </p>
            <p>
              <span className="file-label">Mapper:</span>{" "}
              <span className="file-value">{uploadedFiles.mapper || "None"}</span>
            </p>
          </div>
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

      <button className="sidebar-button" onClick={() => setShowAudioSearchModal(true)}>
        Audio
      </button>

      <button className="sidebar-button" onClick={() => setShowMicSearchModal(true)}>
        Microphone
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
        accept=".txt"
      />
      <PictureModal isOpen={showPictureModal} onClose={handlePictureRetrieval} />
      <AudioModal isOpen={showAudioSearchModal} onClose={handleAudioRetrieval} />
      <MicrophoneModal isOpen={showMicSearchModal} onClose={handleMicRetrieval} />
    </div>
  );
};

export default Sidebar;

