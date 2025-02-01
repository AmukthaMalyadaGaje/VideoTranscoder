import React, { useState, useRef } from "react";

function App() {
  const [videoFile, setVideoFile] = useState(null);
  const [outputFormat, setOutputFormat] = useState("mp4");
  const [quality, setQuality] = useState("720p");
  const [message, setMessage] = useState("");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("idle"); // Possible values: idle, uploading, processing, completed, error
  const [downloadUrl, setDownloadUrl] = useState("");
  const [videoId, setVideoId] = useState(null);
  const pollingInterval = useRef(null);

  // Handle file selection
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setVideoFile(e.target.files[0]);
    }
  };

  // Handle form submission to upload and start conversion
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!videoFile) {
      setMessage("Please select a video file.");
      return;
    }

    setUploading(true);
    setMessage("Uploading video...");
    setProgress(0);
    setStatus("uploading");

    // Prepare form data for upload
    const formData = new FormData();
    formData.append("file", videoFile);
    formData.append("output_format", outputFormat);
    formData.append("video_quality", quality);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload_video/", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Upload failed");
      }
      const data = await response.json();
      // Assume the backend returns a video_id for tracking the conversion process.
      const vidId = data.video_id;
      setVideoId(vidId);
      setMessage("Video uploaded successfully. Conversion started...");
      setStatus("processing");
      // Start polling for conversion status.
      pollStatus(vidId);
    } catch (error) {
      setMessage("Error uploading video.");
      setStatus("error");
    } finally {
      setUploading(false);
    }
  };

  // Poll the backend for conversion progress and status.
  const pollStatus = (vidId) => {
    pollingInterval.current = setInterval(async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/video_status/${vidId}`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch status");
        }
        const data = await response.json();
        // Assume the backend returns a JSON object with keys: progress (0-100), status, and download_url.
        setProgress(data.progress);
        setStatus(data.status);
        if (data.status === "completed") {
          setDownloadUrl(data.transcoded_video_url);
          setMessage("Conversion completed!");
          clearInterval(pollingInterval.current);
        } else if (data.status === "failed") {
          setMessage("Conversion failed.");
          clearInterval(pollingInterval.current);
        }
      } catch (error) {
        setMessage("Error fetching conversion status.");
        clearInterval(pollingInterval.current);
      }
    }, 3000);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <div className="bg-white shadow-xl rounded-lg p-8 max-w-xl w-full">
        <h1 className="text-3xl font-bold text-center mb-6">
          Video Transcoder
        </h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Upload */}
          <div>
            <label className="block text-gray-700 font-semibold mb-2">
              Upload Video
            </label>
            <input
              type="file"
              accept="video/*"
              onChange={handleFileChange}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          {/* Output Format */}
          <div>
            <label className="block text-gray-700 font-semibold mb-2">
              Output Format
            </label>
            <select
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
            >
              <option value="mp4">MP4</option>
              <option value="mkv">MKV</option>
              <option value="mov">MOV</option>
              <option value="avi">AVI</option>
            </select>
          </div>
          {/* Quality */}
          <div>
            <label className="block text-gray-700 font-semibold mb-2">
              Quality
            </label>
            <select
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
            >
              <option value="360p">360p</option>
              <option value="480p">480p</option>
              <option value="720p">720p</option>
              <option value="1080p">1080p</option>
            </select>
          </div>
          {/* Submit Button */}
          <button
            type="submit"
            disabled={uploading || status === "processing"}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition duration-200"
          >
            {uploading || status === "processing" ? "Processing..." : "Convert"}
          </button>
        </form>
        {/* Display Message */}
        {message && <p className="mt-4 text-center text-gray-600">{message}</p>}
        {/* Progress Bar */}
        {(status === "processing" || status === "completed") && (
          <div className="mt-6">
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className="bg-blue-600 h-4 rounded-full"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="mt-2 text-center text-gray-700">{progress}%</p>
          </div>
        )}
        {/* Download Button */}
        {status === "completed" && downloadUrl && (
          <div className="mt-6 text-center">
            <a
              href={downloadUrl}
              download
              className="inline-block bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded transition duration-200"
            >
              Download Video
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
