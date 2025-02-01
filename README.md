# Video Transcoder Project

Video Transcoder is a full-stack application that allows users to upload videos and convert them into various formats (e.g., MP4, MOV, MKV, AVI) with different quality settings (e.g., 360p, 480p, 720p, 1080p). The solution leverages AWS Lambda functions for transcoding, a FastAPI backend for managing status updates, and a modern React frontend built with Vite and Tailwind CSS for an interactive user experience.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Setup](#setup)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Backend Setup](#2-backend-setup)
  - [3. AWS Lambda Function Setup](#3-aws-lambda-function-setup)
  - [4. Frontend Setup](#4-frontend-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- **Video Transcoding:** Convert uploaded videos to different output formats and quality settings.
- **AWS Lambda Integration:** Offload video processing to AWS Lambda for scalable, on-demand transcoding.
- **Backend Service:** FastAPI-powered backend for managing video status, progress updates, and download links.
- **Interactive Frontend:** A modern React UI with real-time progress updates, progress bar visualization, and download functionality.
- **Modular and Scalable:** Easily extendable for additional features or customizations.

## Architecture

1. **AWS Lambda Transcoder:**  
   - Receives video transcoding tasks (e.g., via AWS SQS).
   - Downloads the video from S3, processes it with FFmpeg, and uploads the result back to S3.
2. **Backend Service (FastAPI):**  
   - Provides endpoints for initiating video uploads and updating/polling conversion statuses.
   - Manages video status values such as `in-progress`, `completed`, and `failed`.
3. **Frontend (React + Vite + Tailwind CSS):**  
   - Enables users to upload videos, select output format and quality.
   - Displays a progress bar and a download button when transcoding is complete.

## Requirements

### Backend (Python / FastAPI)
- Python 3.9+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Requests](https://docs.python-requests.org/)
- FFmpeg (installed and accessible in your environment)
- AWS credentials configured for S3 and SQS access

### Frontend (React / Vite / Tailwind CSS)
- Node.js (v14+ recommended)
- npm or yarn
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/video-transcoder.git
cd video-transcoder
```
### 2. Backend Setup
Navigate to the backend folder (e.g., /backend):

```bash
cd backend
```
Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # For Windows use: venv\Scripts\activate
```
Install the required Python packages:

```bash
pip install -r requirements.txt
```
Start the FastAPI backend server:
```bash
uvicorn main:app --reload
```
Make sure to configure your AWS credentials and update the FFmpeg path in your Lambda function code if needed.

### 3. AWS Lambda Function Setup
Package and deploy your Lambda function using your preferred deployment method (e.g., AWS CLI, Serverless Framework).
Ensure the Lambda function is configured to trigger on events (such as SQS messages) and that it has permissions to access your S3 buckets.
Update the Lambda function code with the correct FFmpeg binary path and other environment-specific configurations.
### 4. Frontend Setup
Navigate to the frontend folder (e.g., /frontend):

```bash
cd ../frontend
```
Install frontend dependencies:

```bash
npm install
```
Start the development server:

```bash
npm run dev
```
Open your browser and navigate to the provided URL (e.g., http://localhost:3000).

### 5. Lambda Service setup locally
## Step 1: Clone the Repository

Clone your repository (if applicable) and navigate to the backend folder:

```bash
git clone https://github.com/yourusername/your-repository.git
cd your-repository/backend
```
Create and activate a virtual environment in the backend directory:

```bash
python3 -m venv venv
source venv/bin/activate  # For Windows use: venv\Scripts\activate
```
Install the required Python packages using the provided requirements.txt file:

```bash
pip install -r requirements.txt
```
Note: Your requirements.txt should include packages such as:
fastapi
uvicorn
boto3
requests
(any other dependencies your project requires)

### Download and Install FFmpeg
place the ffmpeg folder at root level after downloading.
FFmpeg is used for video processing in your Lambda function. Follow the instructions below based on your operating system:

For Windows:
Download the latest static build from the FFmpeg official website.
Extract the downloaded ZIP file.
Copy the path to the bin folder (e.g., C:\ffmpeg\bin).
Add the FFmpeg bin directory to your system's PATH environment variable.
For macOS:
Install FFmpeg via Homebrew:

```bash
brew install ffmpeg
For Linux (Ubuntu/Debian):
```
Install FFmpeg using APT:

```bash
sudo apt update
sudo apt install ffmpeg
```
Step 5: Update the FFmpeg Path in Your Code (If Needed)
If your Lambda function or FastAPI application requires a specific FFmpeg binary path, update the code accordingly. For example, in your Lambda function code:

# Example FFmpeg path configuration:
ffmpeg_path = "/path/to/ffmpeg"  # e.g., "C:/ffmpeg/bin/ffmpeg.exe" on Windows or simply "ffmpeg" if installed globally


### Usage
Upload a Video:

In the frontend UI, select a video file.
Choose the desired output format (e.g., MP4, MKV, MOV, AVI) and quality (e.g., 360p, 480p, 720p, 1080p).
Click the Convert button to upload the video and start the transcoding process.
Monitor Conversion:

The frontend will display a progress bar that updates periodically as the backend reports conversion progress.
Status messages will be shown indicating whether the conversion is in progress, completed, or has failed.
Download the Video:

Once the conversion is complete, a Download Video button will appear.
Click the button to download the transcoded video.
