// API Service for KEDB operations
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

// Utility function to make API calls
const makeApiCall = async (url, options = {}) => {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const finalOptions = { ...defaultOptions, ...options };

  try {
    const response = await fetch(url, finalOptions);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

// Fetch suggested KEDBs based on incident description
export const fetchSuggestedKedbs = async (incidentDescription) => {
  const url = `${API_BASE_URL}/suggested-kedbs`;

  try {
    const response = await makeApiCall(url, {
      method: 'POST',
      body: JSON.stringify({ 
        description: incidentDescription,
        limit: 10
      })
    });

    return response.kedbs || response;
  } catch (error) {
    console.error('Error fetching suggested KEDBs:', error);
    throw new Error('Failed to fetch suggested KEDBs');
  }
};

// Generate KEDB content based on incident description
export const generateKedbContent = async (incidentDescription) => {
  const url = `${API_BASE_URL}/generate-kedb`;

  try {
    const response = await makeApiCall(url, {
      method: 'POST',
      body: JSON.stringify({ 
        description: incidentDescription,
        includeSteps: true,
        format: 'markdown'
      })
    });

    return response.content || response.kedbContent || response;
  } catch (error) {
    console.error('Error generating KEDB content:', error);
    throw new Error('Failed to generate KEDB content');
  }
};

// Additional API functions that could be useful

// Get KEDB by ID
export const getKedbById = async (kedbId) => {
  const url = `${API_BASE_URL}/kedb/${kedbId}`;

  try {
    const response = await makeApiCall(url);
    return response;
  } catch (error) {
    console.error('Error fetching KEDB by ID:', error);
    throw new Error('Failed to fetch KEDB details');
  }
};

// Search KEDBs
export const searchKedbs = async (query, filters = {}) => {
  const url = `${API_BASE_URL}/search-kedbs`;

  try {
    const response = await makeApiCall(url, {
      method: 'POST',
      body: JSON.stringify({ 
        query,
        filters,
        limit: filters.limit || 20
      })
    });

    return response.results || response;
  } catch (error) {
    console.error('Error searching KEDBs:', error);
    throw new Error('Failed to search KEDBs');
  }
};

// Save/Update KEDB
export const saveKedb = async (kedbData) => {
  const url = `${API_BASE_URL}/kedb`;
  const method = kedbData.id ? 'PUT' : 'POST';

  try {
    const response = await makeApiCall(url, {
      method,
      body: JSON.stringify(kedbData)
    });

    return response;
  } catch (error) {
    console.error('Error saving KEDB:', error);
    throw new Error('Failed to save KEDB');
  }
};