# KEDB API Server

A sample Express.js server that provides API endpoints for the KEDB Draft Generator app.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the server:
```bash
npm start
```

The server will run on http://localhost:3001

## Endpoints

- POST `/api/suggested-kedbs` - Returns suggested KEDBs
- POST `/api/generate-kedb` - Generates new KEDB content

## Usage with React App

Make sure this server is running before starting the React app. The React app is configured to proxy API requests to this server.