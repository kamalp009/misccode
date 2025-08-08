# KEDB Generator API Documentation

## Overview

This document describes the API endpoints that the KEDB Draft Generator app expects to interact with.

## Base URL

```
http://localhost:3001/api
```

## Authentication

Currently, no authentication is required. In production, you should implement proper authentication.

## Endpoints

### 1. Find Suggested KEDBs

**Endpoint:** `POST /api/suggested-kedbs`

**Description:** Returns a list of suggested KEDB entries based on the incident description.

**Request Body:**
```json
{
  "description": "CTR PC3 CTR.WEEKLY_UNDETECT_REPORT_CLEANUP_V2.B - JOBTERMINATED",
  "limit": 10
}
```

**Response:**
```json
{
  "kedbs": [
    {
      "id": "KB0092892",
      "title": "Generic_KEDB_CRCD_MAXRUN App_ID: CRCD Issue...",
      "recommended": true,
      "content": "**KEDB View**\n\n**How to solve the failure:**\n\n1. Login & navigation..."
    }
  ]
}
```

### 2. Generate KEDB Content

**Endpoint:** `POST /api/generate-kedb`

**Description:** Generates new KEDB content based on the incident description.

**Request Body:**
```json
{
  "description": "CTR PC3 CTR.WEEKLY_UNDETECT_REPORT_CLEANUP_V2.B - JOBTERMINATED",
  "includeSteps": true,
  "format": "markdown"
}
```

**Response:**
```json
{
  "content": "**KEDB Draft**\n\n**Error:** CTR PC3 CTR.WEEKLY_UNDETECT_REPORT_CLEANUP_V2.B - JOBTERMINATED\n\n**Rootcause:** The job terminated unexpectedly..."
}
```

## Sample Backend Implementation

Here's a basic Node.js/Express server example:

```javascript
const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

// Find suggested KEDBs
app.post('/api/suggested-kedbs', (req, res) => {
  const { description } = req.body;

  // Your logic to search and return KEDBs
  const kedbs = [
    {
      id: 'KB0092892',
      title: 'Generic_KEDB_CRCD_MAXRUN App_ID: CRCD Issue...',
      recommended: true,
      content: '**KEDB View**\n\nYour KEDB content here...'
    }
  ];

  res.json({ kedbs });
});

// Generate KEDB content
app.post('/api/generate-kedb', (req, res) => {
  const { description } = req.body;

  // Your logic to generate KEDB content
  const content = `**KEDB Draft**\n\n**Error:** ${description}\n\nGenerated content...`;

  res.json({ content });
});

app.listen(3001, () => {
  console.log('API server running on port 3001');
});
```

## Error Handling

The app includes fallback data when API calls fail, so it will continue to work even if the backend is not available.

## CORS Configuration

Make sure your API server allows CORS requests from `http://localhost:3000` during development.