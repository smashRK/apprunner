# FastAPI + Next.js Greeting App

A simple web application that takes a name as input and returns a greeting message.

## Project Structure
- `/backend` - FastAPI backend
- `/frontend` - Next.js frontend

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   The backend will run on http://localhost:8000

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The frontend will run on http://localhost:3000

## Usage
1. Open http://localhost:3000 in your browser
2. Enter your name in the input field
3. Click "Get Greeting" to receive a personalized greeting